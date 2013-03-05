#**************************************************************************
# 
# This material was prepared by the Los Alamos National Security, LLC 
# (LANS), under Contract DE-AC52-06NA25396 with the U.S. Department of 
# Energy (DOE). All rights in the material are reserved by DOE on behalf 
# of the Government and LANS pursuant to the contract. You are authorized 
# to use the material for Government purposes but it is not to be released 
# or distributed to the public. NEITHER THE UNITED STATES NOR THE UNITED 
# STATES DEPARTMENT OF ENERGY, NOR LOS ALAMOS NATIONAL SECURITY, LLC, NOR 
# ANY OF THEIR EMPLOYEES, MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR 
# ASSUMES ANY LEGAL LIABILITY OR RESPONSIBILITY FOR THE ACCURACY, 
# COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, PRODUCT, OR 
# PROCESS DISCLOSED, OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE 
# PRIVATELY OWNED RIGHTS.
# 
#**************************************************************************

from pyjamas import Window
from pyjamas import logging
from pyjamas.HTTPRequest import HTTPRequest
from __pyjamas__ import JS
from datetime import datetime

try:
    import json
except ImportError:
    import simplejson as json

import websocketclient



class WSdataHandler(websocketclient.WebSocketHandler):
    def __init__(self, parent):
        websocketclient.WebSocketHandler.__init__(self)
        self.app = parent
        self.log = logging.getConsoleLogger()

    def close(self):
        self.log.debug('Disconnected')

    def receive(self, data):
        self.log.debug('Received ' + data)
        if data.lower().startswith('step'):
            self.app.step_in(int(data[4]), json.loads(data[6:]))
        elif data[:6].lower() == 'error:':
            self.app.error(data[6:])
        else:
            self.log.warning('Unknown data: ' + data)


class PHPdataHandler(object):
    def __init__(self, app):
        self.app = app
        self.log = logging.getConsoleLogger()

    def onError(self, msg):
        self.app.error(msg)

    def onCompletion(self, data):
        self.log.debug('Received ' + data)
        self.app.step_in(int(data[4]), json.loads(data[6:]))

    def onTimeout(self, msg):
        self.app.timeout()
        self.log.error('XMLHttpRequest timeout: ' + str(msg))



def multiline_text(text):
    return test.replace('\n', '<br/>')



class WebUI(object):
    def __init_(self):
        self.server = '@@{WEBSOCKET_SERVER}'
        self.resource = '@@{WEBSOCKET_RESOURCE}'
        self.log = logging.getConsoleLogger()


    def __init_UI(self):
        Window.addWindowCloseListener(self)

        self.ws_dh = WSdataHandler(self)
        location = Window.getLocation()
        search = location.getSearch()[1:]
        params = '/'.join(search.split('&'))
        full_resource = self.resource + '/' + params
        self.ws = websocketclient.WebSocketClient(full_resource, self.ws_dh,
                                                  fallback=True)
        self.ws.connect(self.server)

        self.php_dh = PHPdataHandler(self)
        self.php_script = self.resource + '.php'


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
        else:  ## fallback to PHP
            self.log.info('Server at ' + self.server + ' not available.')
            HTTPRequest().asyncPost(self.php_script, msg, self.php_dh)


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
        'M': new RegExp('^[0-9]{1,2}')
        'S': new RegExp('^[0-9]{1,2}')
        'f': new RegExp('^[0-9]+')
    }

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
        if (typeof parsed.S != "undefined") {
            if (parsed.S < 0 || parsed.S > 59) {
                return null;
            }
            date.setSeconds(parsed.S);
        if (typeof parsed.f != "undefined") {
            if (parsed.f < 0 || parsed.f > 999) {
                return null;
            }
            date.setMilliseconds(parsed.f);
        }
        return date;
    };
""")


def strptime(datestring, format):
    '''
    Simple strptime replacement. No timezone, no locale.
    '%f' format is truncated to milliseconds.
    PyJS implementation is incorrect for dates and incomplete for times.
    '''
    try:
        return datetime.fromtimestamp(float(JS("better_strptime(@{{datestring}}.valueOf(), @{{format}}.valueOf()).getTime() / 1000.0")))
    except:
        raise ValueError("Invalid or unsupported values for strptime: '%s', '%s'" % (datestring, format))
