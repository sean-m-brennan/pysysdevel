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

## Note web interfaces never see this module

import sys
import os
import platform

try:
    import logging
    LOGGABLE = True
except ImportError:
    sys.stderr.write("\nUnable to import the logging module." +
                     " Logging disabled.\n")
    sys.stderr.flush()
    LOGGABLE = False

# pylint: disable=E0611
from sysdevel.ui import gui_select



def multiline_text(text):
    return text


class FlexUI(object):
    ## Override these constants
    APP_BASE_DIR = '.'
    IMAGE_DIR = 'img'
    DOCS_DIR = 'doc'
    LOGFILE = 'flex.log'

    def __init__(self, argv):
        if argv == sys.argv:
            self.name = os.path.split(argv[0])[1]
            self.argv = argv[1:]
        else:
            self.name = type(self)
            self.argv = argv
        self.homedir = os.path.expanduser('~')
        if 'windows' in platform.system().lower():
            self.homedir = os.path.expandvars('%USERPROFILE%')

        self.debug_level = 0
        self.backend = gui_select.WX
        self.web_daemon = False
        self.no_gui = False
        self.log = FalseLog()
        self.gui = None

        self.handle_options()

        ## Override these
        self.key = 'flex'
        self.resource_file = os.path.join(self.APP_BASE_DIR, self.key)

        self.data_threads = []
        ## Add data acquisition threads

        ## Subclasses decide whether to run __init_UI() directly here or not


    def __init_UI(self):
        if LOGGABLE:
            if self.debug_level == 4 or (self.debug_level >= 2 and self.no_gui):
                logging.basicConfig(format='%(message)s', level=logging.DEBUG)
            elif self.debug_level == 3 or (self.debug_level >= 1 and self.no_gui):
                logging.basicConfig(format='%(message)s', level=logging.INFO)
            else:
                logging.basicConfig(filename=self.get_log_file(),
                                    format='%(asctime)s  ' +
                                    '%(name)s - %(message)s',
                                    level=logging.WARNING)
            self.log = logging.getLogger(self.name)

        if self.no_gui:
            self.backend = gui_select.TEXT

        self.gui = gui_select.UIFactory(self, LOGGABLE)


    def usage(self):
        sys.stderr.write(
            'Usage: ' + self.name + ' [-h] [-v|-vv|-vvv|-vvvv] ' +
            '[--backend <str>] ' +
            '[--daemon] ' + 
            '  -h, --help      display command line parameters\n' +
            '  -v[vvv]         activate debugging output with increasing verbosity\n' +
            '  --backend <str> specify a graphical backend\n' +
            '  --daemon        run as web data server\n'
            )


    def handle_options(self):
        i = 1
        while i < len(self.argv):
            if self.argv[i] == '-h' or self.argv[i] == '--help':
                self.usage()
                sys.exit()
            elif self.argv[i].startswith('-v'):
                for _ in self.argv[i][1:]:
                    self.debug_level += 1
                i += 1
            elif self.argv[i] == '--backend':
                i += 1
                self.backend = self.argv[i]
                i += 1
            elif self.argv[i] == '--daemon':
                i += 1
                self.web_daemon = True
                self.no_gui = True
            elif self.argv[i] == '--headless':
                i += 1
                self.no_gui = True


    def Start(self):
        for ac in self.data_threads:
            if ac:
                ac.start()
        self.gui.Run()


    def Quit(self):
        self.gui.onExit()
        self.log.info('Quitting the application.')
        for ac in self.data_threads:
            if ac:
                ac.quit()
        logging.shutdown()


    @classmethod
    def get_log_file(klass):
        frozen = getattr(sys, 'frozen', '')
        if not frozen:
            log_file = os.path.join(klass.APP_BASE_DIR, klass.LOGFILE)
        elif frozen in ('dll', 'console_exe', 'windows_exe'):
            log_file = os.path.join(os.path.dirname(sys.executable),
                                    klass.LOGFILE)
        elif frozen in ('macosx_app'):
            log_file = os.path.join(os.environ['RESOURCEPATH'], klass.LOGFILE)
        if os.path.exists(log_file):
            incr = 1
            idx = log_file.rindex('.log')
            while os.path.exists(log_file[:idx] + str(incr) +
                                 log_file[idx:]):
                incr += 1
            log_file = log_file[:idx] + str(incr) + log_file[idx:]
        return log_file


    @classmethod
    def main(klass, argv=None):
        if argv is None:
            argv = sys.argv
        klass(argv).Start()




class FalseLog(object):
    """
    If the logging module is not available, this gives those calls somewhere
    to go.
    """
    def debug(self, fmt, **kwargs):
        pass
    
    def info(self, fmt, **kwargs):
        pass
    
    def warning(self, fmt, **kwargs):
        pass

    def error(self, fmt, **kwargs):
        pass

    def exception(self, fmt, **kwargs):
        pass

    def critical(self, fmt, **kwargs):
        pass
