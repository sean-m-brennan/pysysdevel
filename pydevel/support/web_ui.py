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
log = logging.getConsoleLogger()
from pyjamas.HTTPRequest import HTTPRequest

try:
    import json
except ImportError:
    import simplejson as json

import websocketclient


class WSdataHandler(websocketclient.WebSocketHandler):
    def __init__(self, parent):
        websocketclient.WebSocketHandler.__init__(self)
        self.app = parent

    def close(self):
        log.debug('Disconnected')

    def receive(self, data):
        log.debug('Received ' + data)
        if data.lower().startswith('step'):
            self.app.step_in(int(data[4]), json.loads(data[6:]))
        elif data[:6].lower() == 'error:':
            self.app.error(data[6:])
        else:
            log.warning('Unknown data: ' + data)


class PHPdataHandler(object):
    def __init__(self, app):
        self.app = app

    def onError(self, msg):
        self.app.error(msg)

    def onCompletion(self, data):
        log.debug('Received ' + data)
        self.app.step_in(int(data[4]), json.loads(data[6:]))

    def onTimeout(self, msg):
        self.app.timeout()
        log.error('XMLHttpRequest timeout: ' + str(msg))



class WebUI(object):
    def prepWebUI(self, server, resource):
        Window.addWindowCloseListener(self)

        self.ws_dh = WSdataHandler(self)
        location = Window.getLocation()
        search = location.getSearch()[1:]
        params = '/'.join(search.split('&'))
        full_resource = resource + '/' + params
        self.server = server
        self.ws = websocketclient.WebSocketClient(full_resource, self.ws_dh,
                                                  fallback=True)
        self.ws.connect(self.server)

        self.php_dh = PHPdataHandler(self)
        self.php_script = resource + '.php'


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
        log.debug('Sending ' + msg)
        if self.connected():
            self.ws_dh.send(msg)
        else:  ## fallback to PHP
            log.info('Server at ' + self.server + ' not available.')
            HTTPRequest().asyncPost(self.php_script, msg, self.php_dh)


    def onWindowClosed(self):
        pass

    def onWindowClosing(self):
        pass
