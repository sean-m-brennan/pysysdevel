"""
Find/fetch MS Visual Studio
"""

import os, platform, sys

from sysdevel.util import *

environment = dict()
msvc_found = False
DEBUG = False


def null():
    global environment
    environment['MSVC'] = None
    environment['NMAKE'] = None
    environment['MSVC_VARS'] = None


def is_installed(environ, version):
    global environment, msvc_found
    set_debug(DEBUG)
    if 'MINGW_CC' in environ:
        raise Exception('MS Visual C *and* MinGW both specified ' +
                        'as the chosen compiler.')

    version, _, _ = get_msvc_version()
    dot_ver = '.'.join(version)
    ver = ''.join(version)

    msvc_dirs = []
    vcvars = None
    nmake = None
    msvc = None
    for d in programfiles_directories():
        msvc_dirs.append(os.path.join(d, 'Microsoft Visual Studio ' + dot_ver,
                                      'VC'))
    try:
        vcvars = find_program('vcvarsall', msvc_dirs)
        nmake = find_program('nmake', msvc_dirs)
        msvc = find_program('cl', msvc_dirs)
        msvc_found = True
    except Exception, e:
        if DEBUG:
            print e
        pass

    environment['MSVC_VARS'] = vcvars
    environment['NMAKE'] = nmake
    environment['MSVC'] = msvc
    return msvc_found


def install(environ, version, locally=True):
    if not msvc_found:
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
            #patch c:\Python*\Lib\distutils\msvc9compiler.py
            # insert ld_args.append('/MANIFEST')
            # after  ld_args.append('/MANIFESTFILE:' + temp_manifest)
        else:
            raise Exception('MSVC runtime included as part of the OS, ' +
                            'but not found.')
