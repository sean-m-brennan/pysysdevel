"""
Find/fetch msvcr.dll (required if linking to Python on Windows)
"""

import os, platform, sys

from sysdevel.util import *

environment = dict()
msvcrt_found = False
DEBUG = False


def null():
    global environment
    environment['MSVCRT_DIR'] = None
    environment['MSVCRT_LIBS'] = []


def is_installed(environ, version):
    global environment, msvcrt_found
    set_debug(DEBUG)

    version, _, _ = _get_version()
    dot_ver = '.'.join(version)
    ver = ''.join(version)

    msvcrt_dirs = []
    try:
        msvcrt_dirs.append(os.environ['MSVCRT_DIR'])
    except:
        pass
    try:
        msvcrt_dirs.append(os.path.join(os.environ['ProgramFiles'],
                                         'Microsoft Visual Studio ' + dot_ver,
                                         'VC', 'redist', 'x86',
                                         'Microsoft.VC' + ver + '.CRT'))
    except:
        pass
    try:
        msvcrt_dirs.append(os.path.join(os.environ['ProgramFiles(x86)'],
                                         'Microsoft Visual Studio ' + dot_ver,
                                         'VC', 'redist', 'x86',
                                         'Microsoft.VC' + ver + '.CRT'))
    except:
        pass
    try:
        msvcrt_dirs.append(os.environ['SYSTEM'])
    except:
        pass
    try:
        msvcrt_dirs.append(os.path.join(os.environ['WINDIR'], 'System32'))
    except:
        pass
    try:
        msvcrt_dirs.append(os.path.join(os.environ['WINDIR'], 'SysWOW64'))
    except:
        pass
    try:
        environment['MSVCRT_DIR'], _ = find_library('msvcr' + ver, msvcrt_dirs)
        msvcrt_found = True
    except Exception, e:
        if DEBUG:
            print e
        pass
    environment['MSVCRT_LIBS'] = ['msvcr' + ver, 'msvcp' + ver]
    return msvcrt_found


def install(environ, version, locally=True):
    if not msvcrt_found:
        version, ms_id, name = _get_version()
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
        


def _get_version():
    py_version = get_python_version()
    py_32bit = platform.architecture()[0] == '32bit'
    name = ''
    ms_id = None
    version = ('',)
    if py_version < ('2', '4'):
        raise Exception('sysdevel only supports Python 2.4 and up')
    if py_32bit:
        if py_version <= ('2', '5'):
            name = '.NET Framework version 1.1 redistributable package'
            ms_id = '26'
            version = ('7', '1')
        else:
            name = 'Visual C++ 2008 redistributable package (x86)'
            ms_id = '29'
            version = ('9', '0')
    else:
        if py_version >= ('2', '6'):
            name = 'Visual C++ 2008 redistributable package (x64)'
            ms_id = '15336'
            version = ('9', '0')

    return version, ms_id, name
