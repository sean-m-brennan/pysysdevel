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
# pylint: disable=W0105
"""
WebSocket standalone server
"""

## choose only one:
#IMPLEMENTATION = 'mod_pywebsocket'  ## faulty
#IMPLEMENTATION = 'ws4py'  ## not implemented
IMPLEMENTATION = 'simplewebsocketserver'

if IMPLEMENTATION == 'mod_pywebsocket':
    from pywebsocketserver import *

elif IMPLEMENTATION == 'simplewebsocketserver':
    import socket
    import select
    import ssl
    try:
        from multiprocessing import Process, Event
    except ImportError:
        from threading import Thread as Process, Event

    from simplewebsocketserver import SimpleWebSocketServer, WebSocket

    _DEFAULT_HOST = socket.getfqdn()
    _DEFAULT_PORT = 9876


    class WebSocketServer(Process, SimpleWebSocketServer):
        def __init__(self, resource_handler,
                     host=_DEFAULT_HOST, port=_DEFAULT_PORT,
                     origin=_DEFAULT_HOST,
                     tls_pkey=None, tls_cert=None, permissive=False,
                     debug=False):
            '''
            Create a standalone websocket server given
            a websockethandler.WebResourceFactory derived class.
            Use with SSL requires the files 'tls_pkey' and 'tls_cert'.
            '''
            Process.__init__(self, name='Websocket server')
            SimpleWebSocketServer.__init__(self, host, port, None)

            self.__ws_is_shut_down = Event()
            self.__ws_serving = False

            self.handler = resource_handler
            self.using_tls = False
            if tls_pkey != None and tls_cert != None:
                self.certfile = certfile
                self.keyfile = keyfile
                self.version = ssl.PROTOCOL_SSLv23
                self.using_tls = True


        def decorateSocket(self, sock):
            if self.using_tls:
                sslsock = ssl.wrap_socket(sock,
                                          server_side=True,
                                          certfile=self.certfile,
                                          keyfile=self.keyfile,
                                          ssl_version=self.version)
                return sslsock
            else:
                return sock


        def run(self):  ## alias
            self.serve_forever()


        def serve_forever(self, poll_interval=0.5):
            ## same as superclass, but with better shutdown
            self.__ws_serving = True
            try:
                while self.__ws_serving:
                    r, _, x = select.select(self.listeners, [],
                                            self.listeners, poll_interval)
                    for ready in r:
                        if ready == self.serversocket:
                            sock, address = self.serversocket.accept()
                            newsock = self.decorateSocket(sock)
                            newsock.setblocking(0)
                            fileno = newsock.fileno()
                            self.listeners.append(fileno)
                            self.connections[fileno] = WebSocket(self, newsock,
                                                                 address,
                                                                 self.handler)
                        else:
                            client = self.connections[ready]
                            fileno = client.client.fileno()
            
                            try:
                                client.handle_data()
                            except Exception as n:
                                logging.debug(str(client.address) + ' ' + str(n))
                                try:
                                    client.handle_close()
                                except:
                                    pass
                                client.close()

                                del self.connections[fileno]
                                self.listeners.remove(ready)
      
                    for failed in x:
                        if failed == self.serversocket:
                            self.close()
                            raise Exception("server socket failed")
                        else:
                            client = self.connections[failed]
                            fileno = client.client.fileno()
                            try:
                                client.handle_close()
                            except:
                                pass
                            client.close()

                            del self.connections[fileno]
                            self.listeners.remove(failed)

            except KeyboardInterrupt:
                pass
            finally:
                self.__ws_is_shut_down.set()



        def quit(self):  ## alias
            self.shutdown()

        def shutdown(self):
            self.__ws_serving = False
            self.__ws_is_shut_down.wait()



else:
    raise Exception('Invalid websocket implementation')
