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

## Note web interfaces never see this module

import sys
import os

try:
    import logging
    LOGGABLE = True
except ImportError, e:
    sys.stderr.write("\nUnable to import the logging module." +
                     " Logging disabled.\n")
    sys.stderr.flush()
    LOGGABLE = False

import gui_select



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

        self.handle_options()

        ## Override these
        self.key = 'flex'
        self.resource_file = os.path.join(self.APP_BASE_DIR, self.key)

        self.data_threads = []
        ## Add data acquisition threads

        ## Call self.__init_UI()


    def __init_UI(self)
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
                for flag in self.argv[i][1:]:
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
