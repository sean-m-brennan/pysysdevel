"""
Find/fetch msvcr??.dll (required if linking to Python on Windows)
"""

import os, platform, sys

from sysdevel.util import *

environment = dict()
msvcrt_found = False
DEBUG = False


def null():
    global environment
    environment['MSVCRT_DIR'] = None
    environment['MSVCRT_DEBUG_DIR'] = None
    environment['MSVCRT_LIBS'] = []


def is_installed(environ, version):
    global environment, msvcrt_found
    set_debug(DEBUG)

    version, _, _ = get_msvc_version()
    dot_ver = '.'.join(version)
    ver = ''.join(version)

    msvcr_rel_dirs = []
    msvcr_dbg_dirs = []
    msvs_present = False
    for d in programfiles_directories():
        msvcr_rel_dirs.append(os.path.join(d,
                                           'Microsoft Visual Studio ' + dot_ver,
                                           'VC', 'redist', 'x86',
                                           'Microsoft.VC' + ver + '.CRT'))
        msvcr_dbg_dirs.append(os.path.join(d,
                                           'Microsoft Visual Studio ' + dot_ver,
                                           'VC', 'redist',
                                           'Debug_NonRedist', 'x86',
                                           'Microsoft.VC' + ver + '.DebugCRT'))
        if os.path.exists(os.path.join(d, 'Microsoft Visual Studio ' + dot_ver)):
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
    try:
        ## Just the DLLs
        release_dir, _ = find_library('msvcr' + ver, msvcr_rel_dirs)
        debug_dir, _ = find_library('msvcr' + ver, msvcr_dbg_dirs)
        ''' FIXME do we need the manifests?
        try:
            # Manifests
            manifest = find_file('Microsoft.VC' + ver + '.CRT.manifest',
                                 msvcr_rel_dirs)
            environment['MSVCRT_DIR'] = os.path.dirname(manifest)
        except:
            pass
            '''
        msvcrt_found = True
    except Exception, e:
        if DEBUG:
            print e
        pass

    environment['MSVCRT_DIR'] = release_dir
    environment['MSVCRT_DEBUG_DIR'] = debug_dir
    environment['MSVCRT_LIBS'] = ['msvcr' + ver, 'msvcp' + ver]
    return msvcrt_found


def install(environ, version, locally=True):
    if not msvcrt_found:
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
