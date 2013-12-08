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

"""
WebSocket standalone server
"""

try:
    ## Python 3.x
    from http.server import HTTPServer, SimpleHTTPRequestHandler
    from http.client import HTTPMessage
    import socketserver
except:
    from BaseHTTPServer import HTTPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler
    from httplib import HTTPMessage
    import SocketServer as socketserver

import sys
import logging
import socket
import select
import threading

_HAS_SSL = False
_HAS_OPEN_SSL = False
try:
    import ssl
    _HAS_SSL = True
except ImportError:
    try:
        import OpenSSL.SSL
        _HAS_OPEN_SSL = True
    except ImportError:
        pass

from mod_pywebsocket import common, dispatch, util, handshake, standalone
from mod_pywebsocket import http_header_util, memorizingfile, extensions

## derived partially from mod_pywebsocket.standalone


_WEBSOCKET_HOST             = socket.getfqdn()
_WEBSOCKET_PORT             = 9876

_DEFAULT_LOG_MAX_BYTES      = 1024 * 256
_DEFAULT_LOG_BACKUP_COUNT   = 5
_DEFAULT_REQUEST_QUEUE_SIZE = 128
_MAX_MEMORIZED_LINES        = 1024  ## for WebSocket handshake lines.



def get_ws_logger(cls, debug=False):
    if cls.__class__.__name__ == 'type':
        logname = '%s.%s' % (cls.__module__, cls.__name__)
    elif cls.__class__.__name__ == 'module':
        logname = cls.__name__
    else:
        logname = '%s.%s' % (cls.__class__.__module__, cls.__class__.__name__)
    log = logging.getLogger(logname)
    if debug:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.WARNING)
    return log



class WebSocketServer(threading.Thread,
                      socketserver.ThreadingMixIn,
                      HTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, resource_handler,
                 host=_WEBSOCKET_HOST, port=_WEBSOCKET_PORT,
                 origin=_WEBSOCKET_HOST,
                 tls_pkey=None, tls_cert=None, permissive=False,
                 debug=False):
        '''
        Create a standalone websocket server given
        a websockethandler.WebResourceFactory derived class.
        Use with SSL requires the files 'tls_pkey' and 'tls_cert'.
        '''
        ## Unify mod_pywebsocket logs
        self._logger = get_ws_logger(self, debug)
        for cls in [util._Inflater, util._Deflater,
                    handshake, handshake.hybi.Handshaker,
                    handshake.hybi00.Handshaker, handshake.draft75.Handshaker,
                    extensions.DeflateFrameExtensionProcessor,
                    ]:
            get_ws_logger(cls, debug)

        threading.Thread.__init__(self, name='Websocket server')

        self.origin = origin
        self.port = port
        self.permissive = permissive

        self.using_tls = False
        if tls_pkey != None and tls_cert != None:
            self.private_key = tls_pkey
            self.certificate = tls_cert
            self.using_tls = True
        self.draft75 = True
        self.strict_draft75 = False
        self.request_queue_size = _DEFAULT_REQUEST_QUEUE_SIZE
        self.__ws_is_shut_down = threading.Event()
        self.__ws_serving = False

        socketserver.BaseServer.__init__(self, (host, port),
                                         WebSocketRequestHandler)
        self.wsdispatcher = WebsocketDispatch(resource_handler,
                                              self._logger, origin, permissive)
        self._create_sockets()
        self.server_bind()
        self.server_activate()




    def _create_sockets(self):
        self.server_name, self.server_port = self.server_address
        self._sockets = []
        if not self.server_name:
            # On platforms that doesn't support IPv6, the first bind fails.
            # On platforms that supports IPv6
            # - If it binds both IPv4 and IPv6 on call with AF_INET6, the
            #   first bind succeeds and the second fails (we'll see 'Address
            #   already in use' error).
            # - If it binds only IPv6 on call with AF_INET6, both call are
            #   expected to succeed to listen both protocol.
            addrinfo_array = [
                (socket.AF_INET6, socket.SOCK_STREAM, '', '', ''),
                (socket.AF_INET, socket.SOCK_STREAM, '', '', '')]
        else:
            addrinfo_array = socket.getaddrinfo(self.server_name,
                                                self.server_port,
                                                socket.AF_UNSPEC,
                                                socket.SOCK_STREAM,
                                                socket.IPPROTO_TCP)
        for addrinfo in addrinfo_array:
            self._logger.debug('WS Create socket on: %r', addrinfo)
            family, socktype, proto, canonname, sockaddr = addrinfo
            try:
                socket_ = socket.socket(family, socktype)
            except Exception:
                e = sys.exc_info()[1]
                self._logger.debug('WS Skip by failure: %r', e)
                continue
            if self.using_tls:
                if _HAS_SSL:
                    socket_ = ssl.wrap_socket(socket_,
                                              keyfile=self.private_key,
                                              certfile=self.certificate,
                                              ssl_version=ssl.PROTOCOL_SSLv23)
                if _HAS_OPEN_SSL:
                    ctx = OpenSSL.SSL.Context(OpenSSL.SSL.SSLv23_METHOD)
                    ctx.use_privatekey_file(self.private_key)
                    ctx.use_certificate_file(self.certificate)
                    socket_ = OpenSSL.SSL.Connection(ctx, socket_)
            self._sockets.append((socket_, addrinfo))


    def server_bind(self):
        failed_sockets = []

        for socketinfo in self._sockets:
            socket_, addrinfo = socketinfo
            self._logger.debug('WS Bind on: %r', addrinfo)
            if self.allow_reuse_address:
                socket_.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                socket_.bind(self.server_address)
            except Exception:
                e = sys.exc_info()[1]
                self._logger.debug('WS Skip by failure: %r', e)
                socket_.close()
                failed_sockets.append(socketinfo)

        for socketinfo in failed_sockets:
            self._sockets.remove(socketinfo)


    def server_activate(self):
        failed_sockets = []

        for socketinfo in self._sockets:
            socket_, addrinfo = socketinfo
            self._logger.debug('WS Listen on: %r', addrinfo)
            try:
                socket_.listen(self.request_queue_size)
            except Exception:
                e = sys.exc_info()[1]
                self._logger.debug('WS Skip by failure: %r', e)
                socket_.close()
                failed_sockets.append(socketinfo)

        for socketinfo in failed_sockets:
            self._sockets.remove(socketinfo)


    def server_close(self):
        for socketinfo in self._sockets:
            socket_, addrinfo = socketinfo
            self._logger.debug('WS Close on: %r', addrinfo)
            socket_.close()


    def fileno(self):
        self._logger.critical('WS fileno not supported')
        return self._sockets[0][0].fileno()


    def handle_error(self, request, client_address):
        self._logger.error('WS exception in processing request from: %r\n%s',
                           client_address, util.get_stack_trace())


    def get_request(self):
        accepted_socket, client_address = self.socket.accept()
        if self.using_tls and _HAS_OPEN_SSL:
            accepted_socket = standalone._StandaloneSSLConnection(accepted_socket)
        return accepted_socket, client_address


    def run(self):  ## alias
        self.serve_forever()

    def serve_forever(self, poll_interval=0.5):
        self.__ws_serving = True
        self.__ws_is_shut_down.clear()
        handle_request = self.handle_request
        if hasattr(self, '_handle_request_noblock'):
            handle_request = self._handle_request_noblock
        else:
            self._logger.debug('WS Fallback to blocking request handler')
        try:
            while self.__ws_serving:
                r, w, e = select.select(
                    [socket_[0] for socket_ in self._sockets],
                    [], [], poll_interval)
                for socket_ in r:
                    self.socket = socket_
                    handle_request()
                self.socket = None
        finally:
            self.__ws_is_shut_down.set()


    def quit(self):  ## alias
        self.shutdown()

    def shutdown(self):
        self.__ws_serving = False
        self.__ws_is_shut_down.wait()




class WebsocketDispatch(dispatch.Dispatcher):
    def __init__(self, res_hndlr, log, origin=None, permissive=False):
        self.resource_handler = res_hndlr
        self.log = log
        self.origin = origin
        self.permissive = permissive
        self.clients = []
        dispatch.Dispatcher.__init__(self, './', None, False)

    def do_extra_handshake(self, request):
        if (not self.permissive and (self.origin is None or
                                     request.ws_origin == 'null' or
                                     request.ws_origin.startswith('file://') or
                                     request.ws_origin != self.origin)) or \
              (self.permissive and (self.origin is not None and
                                    request.ws_origin != 'null' and
                                    not request.ws_origin.startswith('file://') and
                                    request.ws_origin != self.origin)):
            ## this causes a 400 Bad Request
            raise handshake.AbortedByUserException('Invalid origin: ' +
                                                   str(request.ws_origin) + 
                                                   ' should be ' +
                                                   str(self.origin))
        return

    def receive_data(self, request, resource):
        self.clients.append(request.ws_stream)
        handler_factory = self.resource_handler()
        service = handler_factory(self, resource)
        if service is None:
            return
        while not service.closing():
            try:
                msg = request.ws_stream.receive_message()
                service.handle_message(msg)
            except Exception:
                e = sys.exc_info()[1]
                self.log.debug('WS receive: ' + str(e))
                break
        try:
            self.clients.remove(request.ws_stream)
        except ValueError:
            pass
        service.quit()

    def send_data(self, data):
        if len(self.clients) > 0:
            for s in self.clients:
                try:
                    s.send_message(data, binary=False)
                except Exception:
                    e = sys.exc_info()[1]
                    self.log.debug('WS send: ' + str(e))
                    try:
                        self.clients.remove(s)
                    except ValueError:
                        pass


    ## overrides for CGI based methods
    def add_resource_path_alias(self, alias_path, existing_path):
        pass

    def get_handler_suite(self, resource):
        return None

    def _source_handler_files_in_dir(self, root_dir, scan_dir, allow):
        pass




class WebSocketRequestHandler(SimpleHTTPRequestHandler):
    MessageClass = HTTPMessage

    def setup(self):
        """Override SocketServer.StreamRequestHandler.setup to wrap rfile
        with MemorizingFile.

        This method will be called by BaseRequestHandler's constructor
        before calling BaseHTTPRequestHandler.handle.
        BaseHTTPRequestHandler.handle will call
        BaseHTTPRequestHandler.handle_one_request and it will call
        WebSocketRequestHandler.parse_request.
        """
        # Call superclass's setup to prepare rfile, wfile, etc. See setup
        # definition on the root class SocketServer.StreamRequestHandler to
        # understand what this does.
        SimpleHTTPRequestHandler.setup(self)

        self.rfile = memorizingfile.MemorizingFile(
            self.rfile,
            max_memorized_lines=_MAX_MEMORIZED_LINES)


    def __init__(self, request, client_address, server):
        self._logger = get_ws_logger(self)
        self.origin = server.origin
        self.port = server.port
        self.permissive = server.permissive
        SimpleHTTPRequestHandler.__init__(self, request, client_address, server)


    def parse_request(self):
        if not SimpleHTTPRequestHandler.parse_request(self):
            return False
        host, port, resource = http_header_util.parse_uri(self.path)
        if resource is None:
            self._logger.info('WS Invalid URI: %r', self.path)
            self._logger.info('WS Fallback to normal HTTP.')
            return True
        if (not self.permissive and (host is None or self.origin is None or 
                                    host.startswith('file://') or
                                    host != self.origin)) or \
                     (self.permissive and host is not None and
                      self.origin is not None and
                      not host.startswith('file://') and host != self.origin):
            self._logger.info('WS Invalid host: %r (expected: %r)',
                              host, self.origin)
            self._logger.info('WS Fallback to normal HTTP.')
            return True
        if port is not None and self.port is not None and port != self.port:
            self._logger.info('WS Invalid port: %r (expected: %r)',
                              port, self.port)
            self._logger.info('WS Fallback to normal HTTP.')
            return True
        
        self.path = resource
        return self.handle_ws(resource)


    def handle_ws(self, resource):
        request = standalone._StandaloneRequest(self, self.server.using_tls)
        try:
            try:
                handshake.do_handshake(
                    request,
                    self.server.wsdispatcher,
                    allowDraft75=self.server.draft75,
                    strict=self.server.strict_draft75)
            except handshake.VersionException:
                e = sys.exc_info()[1]
                self._logger.info('WS handshake version error: %s', e)
                self.send_response(common.HTTP_STATUS_BAD_REQUEST)
                self.send_header(common.SEC_WEBSOCKET_VERSION_HEADER,
                                 e.supported_versions)
                self.end_headers()
                return False
            except handshake.HandshakeException:
                # Handshake for ws(s) failed.
                e = sys.exc_info()[1]
                self._logger.info('WS handshake error: %s', e)
                self.send_error(e.status)
                return False

            request._dispatcher = self.server.wsdispatcher
            self.server.wsdispatcher.receive_data(request, resource)
        except handshake.AbortedByUserException:
            e = sys.exc_info()[1]
            self._logger.info('WS handshake aborted: %s', e)
        return False


    def log_request(self, code='-', size='-'):
        pass

    def log_error(self, *args):
        self._logger.warning('%s - %s',
                             self.address_string(),
                             args[0] % args[1:])
