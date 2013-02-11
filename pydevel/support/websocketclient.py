# -*- coding: utf-8 -*-
"""
WebSockets support for pyjamas 
"""
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

SOCKET_IO_SUPPORTED = False  ## TODO: Socket.io support in the websocket server

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
        self._io = None
        self._socket_type = 'unsupported'
        self.has_fallback = fallback


    def _detect_socket_support(self):
        self._socket_type = 'unsupported'
        loc = JS("""$wnd.location.href""")
        if not loc.startswith('file://') and SOCKET_IO_SUPPORTED:
            if JS("""typeof $wnd.io != 'undefined'""") and \
                    JS("""typeof $wnd.io.Socket != 'undefined'"""):
                self._socket_type = 'io'
        elif JS("""typeof $wnd.WebSocket != 'undefined'"""):
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
        elif self._socket_type == 'io':
            server = host + ':' + str(port) + '/cxd_gse'
            JS("""@{{self}}._io = new $wnd.io.Socket(@{{host}},{
                         port:@{{port}},
                         transports:['websocket','flashsocket'],
                         resource:@{{self}}.resource })""")
            self._io.connect()
            self.uri = server
            self._io.on('connect', self.onOpen)
            self._io.on('disconnect', self.onClose)
            self._io.on('error', self.onError)
            self._io.on('message', self.onMessage)
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
            if self._ws != None:
                self._ws.send(message)
            else:
                self._io.emit('message', message)
        except Exception,e:
            log.debug(str(e))


    def close(self):
        log.debug('WS closing')
        if self._ws != None:
            self._ws.close()
        else:
            self._io.disconnect()
        self._opened = False


    def isOpen(self):
        if self._ws != None:
            return self._ws.readyState == 1
        else:
            return self._opened
 

    def onError(self, evt):
        log.error('WebSocket error: ' + evt)


    def onOpen(self, evt):
        if self._ws != None:
            log.debug('WS connected to ' + self.uri)
        else:
            log.debug('Socket.IO connected to ' + self.uri)
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
            if self._ws != None:
                self.handler.receive(evt.data)
            else:
                self.handler.receive(evt)
        except Exception,e:
            log.debug(str(e))
