"""
Copyright 2013.  Los Alamos National Security, LLC.
This material was produced under U.S. Government contract
DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which is
operated by Los Alamos National Security, LLC for the U.S. Department
of Energy. The U.S. Government has rights to use, reproduce, and
distribute this software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS
NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should be
clearly marked, so as not to confuse it with the version available
from LANL.

Licensed under the Mozilla Public License, Version 2.0 (the
"License"); you may not use this file except in compliance with the
License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/2.0/

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.
"""

# pylint: disable=F0401

from pyjamas import Window
from pyjamas import logging
from pyjamas.HTTPRequest import HTTPRequest
from __pyjamas__ import JS
from datetime import datetime

try:
    import json
except ImportError:
    import simplejson as json

from sysdevel.ui import websocketclient



class WSdataHandler(websocketclient.WebSocketHandler):
    def __init__(self, parent, callback=None):
        websocketclient.WebSocketHandler.__init__(self)
        self.app = parent
        self.log = logging.getConsoleLogger()
        self.callback = callback

    def close(self):
        self.log.debug('Disconnected')

    def receive(self, data):
        self.log.debug('Received ' + data)
        if self.callback:
            self.callback(data)
        elif data.lower().startswith('step'):
            self.app.step_in(int(data[4]), json.loads(data[6:]))
        elif data[:6].lower() == 'error:':
            self.app.error(data[6:])
        else:
            self.log.warning('Unknown data: ' + data)


class PHPdataHandler(object):
    def __init__(self, app, callback=None):
        self.app = app
        self.log = logging.getConsoleLogger()
        self.callback = callback

    def onError(self, msg):
        self.app.error(msg)

    def onCompletion(self, data):
        self.log.debug('Received ' + data)
        if self.callback:
            self.callback(data)
        else:
            self.app.step_in(int(data[4]), json.loads(data[6:]))

    def onTimeout(self, msg):
        self.app.timeout()
        self.log.error('XMLHttpRequest timeout: ' + str(msg))



def multiline_text(text):
    return text.replace('\n', '<br/>')



class WebUI(object):
    @classmethod
    def main(klass, argv=None):
        klass(argv).__init_UI()  # pylint: disable=W0212


    def __init__(self, argv=None):
        self.server = '@@{WEBSOCKET_SERVER}'
        self.resource = '@@{WEBSOCKET_RESOURCE}'
        self.callback = None
        self.fallback = False
        if argv:
            for arg in argv:
                if arg == '-s' or arg == '--server':
                    idx = argv.index(arg)
                    self.server = argv[idx+1]
                elif arg == '-r' or arg == '--resource':
                    idx = argv.index(arg)
                    self.resource = argv[idx+1]
                elif arg == '--callback':
                    idx = argv.index(arg)
                    self.callback = getattr(self, argv[idx+1])
                elif arg == '--fallback':
                    idx = argv.index(arg)
                    if len(argv) > idx and argv[idx+1][0] != '-':
                        self.fallback = argv[idx+1]
                    else:
                        self.fallback = True
        if 'WEBSOCKET_' in self.server or 'WEBSOCKET_' in self.resource:
            raise Exception('Invalid configuration for WebUI')
        self.log = logging.getConsoleLogger()
        self.ws = None
        self.ws_dh = None
        self.php_script = None
        self.php_dh = None


    def __init_UI(self):
        ## Two-phase to mimic flex_ui class
        Window.addWindowCloseListener(self)

        self.ws_dh = WSdataHandler(self, self.callback)
        location = Window.getLocation()
        search = location.getSearch()[1:]
        params = '/'.join(search.split('&'))
        full_resource = self.resource + '/' + params
        self.ws = websocketclient.WebSocketClient(full_resource, self.ws_dh,
                                                  fallback=bool(self.fallback))
        self.ws.connect(self.server)

        self.php_dh = PHPdataHandler(self, self.callback)
        self.php_script = self.resource + '.php'
        if not isinstance(self.fallback, bool):
            self.php_script = self.fallback


    def step_in(self, n, data):
        raise NotImplementedError()

    def step_out(self, n):
        raise NotImplementedError()

    def error(self, info):
        raise NotImplementedError()

    def timeout(self):
        raise NotImplementedError()


    def connected(self):
        if self.ws is None:
            return False
        return self.ws.isOpen()

    def send_to_server(self, msg_type, data=None):
        msg = str(msg_type).lower()
        if data:
            msg += '=' + json.dumps(data)
        self.log.debug('Sending ' + msg)
        if self.connected():
            self.ws_dh.send(msg)
        elif self.fallback:  ## fallback to PHP
            self.log.info('Server at ' + self.server + ' not available.')
            HTTPRequest().asyncPost(self.php_script, msg, self.php_dh)
        else:
            self.log.error('Server at ' + self.server + ' not available.')


    def onWindowClosed(self):
        pass

    def onWindowClosing(self):
        pass



## strptime substitute, *almost* verbatim from PyJS time.py
JS("""
    var _BETTER_DATE_FORMAT_REGXES = {
        'Y': new RegExp('^-?[0-9]+'),
        'y': new RegExp('^-?[0-9]{1,2}'),
        'd': new RegExp('^[0-9]{1,2}'),
        'm': new RegExp('^[0-9]{1,2}'),
        'H': new RegExp('^[0-9]{1,2}'),
        'M': new RegExp('^[0-9]{1,2}'),
        'S': new RegExp('^[0-9]{1,2}'),
        'f': new RegExp('^[0-9]+')
    };

    /*
     * _parseData does the actual parsing job needed by `strptime`
     */
    function _better_parseDate(datestring, format) {
        var parsed = {};
        for (var i1=0,i2=0;i1<format.length;i1++,i2++) {
            var c1 = format[i1];
            var c2 = datestring[i2];
            if (c1 == '%') {
                c1 = format[++i1];
                var data = _BETTER_DATE_FORMAT_REGXES[c1].exec(datestring.substring(i2));
                if (!data.length) {
                    return null;
                }
                data = data[0];
                i2 += data.length-1;
                if (c1 == 'f') {
                    while (data.length < 3) {
                        data += '0';
                    }
                    data = data.substring(0, 3);
                }
                var value = parseInt(data, 10);
                if (isNaN(value)) {
                    return null;
                }
                parsed[c1] = value;
                continue;
            }
            if (c1 != c2) {
                return null;
            }
        }
        return parsed;
    }

    /*
     * basic implementation of strptime. The only recognized formats
     * defined in _BETTER_DATE_FORMAT_REGEXES
     */
    function better_strptime(datestring, format) {
        var parsed = _better_parseDate(datestring, format);
        if (!parsed) {
            return null;
        }
        // create initial date (!!! year=0 means 1900 !!!)
        var date = new Date(0, 0, 1, 0, 0);
        date.setFullYear(0); // reset to year 0
        if (typeof parsed.Y != "undefined") {
            date.setFullYear(parsed.Y);
        }
        // POSIX rules
        if (typeof parsed.y != "undefined") {
            if (parsed.y > 99) {
                return null;
            }
            else if (parsed.y < 69) {
                date.setFullYear(2000+parsed.y);
            }
            else {
                date.setFullYear(1900+parsed.y);
            }
        }
        if (typeof parsed.m != "undefined") {
            if (parsed.m < 1 || parsed.m > 12) {
                return null;
            }
            // !!! month indexes start at 0 in javascript !!!
            date.setMonth(parsed.m - 1);
        }
        if (typeof parsed.d != "undefined") {
            if (parsed.d < 1 || parsed.d > 31) {
                return null;
            }
            date.setDate(parsed.d);
        }
        if (typeof parsed.H != "undefined") {
            if (parsed.H < 0 || parsed.H > 23) {
                return null;
            }
            date.setHours(parsed.H);
        }
        if (typeof parsed.M != "undefined") {
            if (parsed.M < 0 || parsed.M > 59) {
                return null;
            }
            date.setMinutes(parsed.M);
        }
        if (typeof parsed.S != "undefined") {
            if (parsed.S < 0 || parsed.S > 59) {
                return null;
            }
            date.setSeconds(parsed.S);
        }
        if (typeof parsed.f != "undefined") {
            if (parsed.f < 0 || parsed.f > 999) {
                return null;
            }
            date.setMilliseconds(parsed.f);
        }
        return date;
    };
""")


def strptime(datestring, fmt):
    '''
    Simple strptime replacement. No timezone, no locale.
    '%f' format is truncated to milliseconds.
    PyJS implementation is incorrect for dates and incomplete for times.
    '''
    try:
        return datetime.fromtimestamp(float(JS("better_strptime(@{{datestring}}.valueOf(), @{{fmt}}.valueOf()).getTime() / 1000.0")))
    except:
        raise ValueError("Invalid or unsupported values for strptime: '%s', '%s'" % (datestring, fmt))
