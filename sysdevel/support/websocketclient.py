"""
WebSockets support for pyjamas 
"""

import sys

from __pyjamas__ import JS
from pyjamas import Window
from pyjamas import logging
log = logging.getConsoleLogger()


class WebSocketHandler(object):
    '''
    Abstract handler class
    '''
    def __init__(self):
        self.sender = None

    def close(self):
        raise NotImplementedError('WebSocketHandler is abstract')

    def receive(self, data):
        raise NotImplementedError('WebSocketHandler is abstract')

    def send(self, data):
        if self.sender != None:
            self.sender.send(data)


class WebSocketClient(object):
    def __init__(self, resource, handler, fallback=False):
        self._opened = False
        self.uri = ''
        self.resource = resource
        self.handler = handler
        self.handler.sender = self
        self._ws = None
        self._socket_type = 'unsupported'
        self.has_fallback = fallback


    def _detect_socket_support(self):
        loc = JS("""$wnd.location.href""")
        if JS("""typeof $wnd.WebSocket != 'undefined'"""):
            self._socket_type = 'ws'


    def connect(self, host='localhost', port=9876, proto='ws'):
        self._opened = False
        self._ws = None
        self._detect_socket_support()
        if self._socket_type == 'ws':
            server = proto + '://' + host + ':' + str(port) + '/' + self.resource
            JS("""@{{self}}._ws = new $wnd.WebSocket(@{{server}});""")
            self.uri = server
            self._ws.onopen = self.onOpen
            self._ws.onclose = self.onClose
            self._ws.onerror = self.onError
            self._ws.onmessage = self.onMessage
        else:
            self.unsupported()


    def unsupported(self):
        self._opened = False
        if not self.has_fallback:
            Window.alert('Unsupported browser.\n' + 
                         'Try Google Chrome (redirecting now).')
            JS("""$wnd.location.replace("http://www.google.com/chrome")""")


    def send(self, message):
        try:
            self._ws.send(message)
        except Exception,e:
            log.debug(str(e))


    def close(self):
        log.debug('WS closing')
        if self._ws != None:
            self._ws.close()
        self._opened = False


    def isOpen(self):
        if self._ws != None:
            return self._ws.readyState == 1
        return False


    def onError(self, evt):
        log.error('WebSocket error: ' + evt)


    def onOpen(self, evt):
        if self._ws != None:
            log.debug('WS connected to ' + self.uri)
        self._opened = True


    def onClose(self, evt):
        if self._opened:
            msg = 'Lost connection with the websocket server.'
            if self.has_fallback:
                msg += '\nFalling back to PHP.'
            Window.alert(msg)
            self.handler.close()
        else:
            if not self.has_fallback:
                Window.alert("No websocket server available at " + self.uri)
        self._opened = False


    def onMessage(self, evt):
        try:
            self.handler.receive(evt.data)
        except Exception,e:
            log.debug(str(e))
