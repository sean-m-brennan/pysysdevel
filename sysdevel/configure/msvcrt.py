
import os
import platform
import sys

from sysdevel.util import *
from sysdevel.configuration import config

class configuration(config):
    """
    Find/fetch/install msvcr??.dll (required if linking to Python on Windows)
    """
    def __init__(self):
        config.__init__(self, debug=False)


    def null(self):
        self.environment['MSVCRT_DIR'] = None
        self.environment['MSVCRT_DEBUG_DIR'] = None
        self.environment['MSVCRT_LIBS'] = []


    def is_installed(self, environ, version):
        set_debug(self.debug)

        msvcr_rel_dirs = []
        msvcr_dbg_dirs = []
        limit = False
        if 'MSVCRT_DIR' in environ:
            msvcr_rel_dirs.append(environ['MSVCRT_DIR'])
            limit = True
            if 'MSVCRT_DEBUG_DIR' in environ:
                msvcr_dbg_dirs.append(environ['MSVCRT_DEBUG_DIR'])

        version, _, _ = get_msvc_version()
        dot_ver = '.'.join(version)
        ver = ''.join(version)

        msvs_present = False
        if not limit:
            for d in programfiles_directories():
                msvcr_rel_dirs.append(
                    os.path.join(d, 'Microsoft Visual Studio ' + dot_ver,
                                 'VC', 'redist', 'x86',
                                 'Microsoft.VC' + ver + '.CRT'))
                msvcr_dbg_dirs.append(
                    os.path.join(d, 'Microsoft Visual Studio ' + dot_ver,
                                 'VC', 'redist', 'Debug_NonRedist', 'x86',
                                 'Microsoft.VC' + ver + '.DebugCRT'))
                if os.path.exists(
                    os.path.join(d, 'Microsoft Visual Studio ' + dot_ver)):
                    msvs_present = True

            if not msvs_present:
                try:
                    msvcr_rel_dirs.append(os.environ['MSVCRT_DIR'])
                except:
                    pass
                try:
                    msvcr_rel_dirs.append(os.environ['SYSTEM'])
                except:
                    try:
                        msvcr_rel_dirs.append(os.path.join(os.environ['WINDIR'],
                                                           'System32'))
                    except:
                        pass
        release_dir = None
        debug_dir = None
        try:
            # Just the DLLs
            release_dir, _ = find_library('msvcr' + ver, msvcr_rel_dirs,
                                          limit=limit)
            debug_dir, _ = find_library('msvcr' + ver, msvcr_dbg_dirs,
                                        limit=limit)
            self.found = True
        except Exception, e:
            if self.debug:
                print e
            return self.found

        self.environment['MSVCRT_DIR'] = release_dir
        self.environment['MSVCRT_DEBUG_DIR'] = debug_dir
        self.environment['MSVCRT_LIBS'] = ['msvcr' + ver, 'msvcp' + ver]
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            version, ms_id, name = get_msvc_version()
            if ms_id:
                import webbrowser
                website = ('http://www.microsoft.com/en-us/download/',
                           'details.aspx?id=' + ms_id)
                sys.stdout.write('Manually download and install (from ' +
                                 website[0] + ')\nthe ' + name + '.\n' +
                                 'Opening a browser to confirm download ...\n')
                webbrowser.open(''.join(website))
                raw_input('Press any key once the redistributable ' +
                          'package is installed')
            else:
                raise Exception('MSVC runtime included as part of the OS, ' +
                                'but not found.')
