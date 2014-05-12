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
WebSocket handling
"""

try:
    from multiprocessing import Process
except ImportError:
    from threading import Thread as Process
import logging

from sysdevel.modeling.models import DataViewer


def json_handler(obj):
    from datetime import datetime
    # pylint: disable=E0611
    from numpy import ndarray
    # pylint: enable=E0611
    HAVE_SPACEPY = False
    try:
        from spacepy.datamodel import dmarray
        HAVE_SPACEPY = True
    except ImportError:
        pass

    if type(obj) == datetime:
        return obj.isoformat()
    elif type(obj) == ndarray:
        return obj.tolist()
    elif HAVE_SPACEPY and type(obj) == dmarray:
        return obj.tolist()
    elif isinstance(obj, DataViewer):
        import inspect
        discard = dir(type('dummy', (object,), {}))
        discard += inspect.getmembers(obj,
                                      lambda x: inspect.isbuiltin(x) or \
                                      inspect.ismethod(x))
        return [item for item in inspect.getmembers(obj) if item not in discard]
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))




class WebHandlerService(Process):
    '''
    Abstract class for handling messages from a web client
    '''
    def __init__(self, name):
        super(WebHandlerService, self).__init__(name=name)
        self.log = logging.getLogger(self.__class__.__name__)

    def closing(self):
        raise NotImplementedError('WebHandlerService must be subclassed.')

    def quit(self):
        raise NotImplementedError('WebHandlerService must be subclassed.')

    def handle_message(self, message):
        raise NotImplementedError('WebHandlerService must be subclassed.')



class WebResourceFactory(object):
    '''
    Abstract callable factory class for creating WebHandlerServices
    Takes a dispatch.Dispatcher instance and a web resource string
    Returns a WebHandlerService instance
    '''
    def __call__(self, dispatcher, resource):
        raise NotImplementedError('WebResourceFactory must be subclassed.')



class WebServer(object):
    '''
    Abstract class for creating a websockets server
    '''
    def __init__(self, log_file, log_level=logging.WARNING):
        if log_file is None:  ## log to stdout
            logging.basicConfig(format='%(asctime)s  %(name)s - %(message)s',
                                level=log_level)
        else:
            logging.basicConfig(filename=log_file, filemode='w',
                                format='%(asctime)s  %(name)s - %(message)s',
                                level=log_level)

    def run(self):
        raise NotImplementedError('WebServer must be subclassed.')

    def quit(self):
        raise NotImplementedError('WebServer must be subclassed.')
