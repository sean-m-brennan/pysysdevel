"""
Find/fetch/install the GNU Fortran
"""

import os
import platform

from sysdevel.util import *

environment = dict()
gfortran_found = False
DEBUG = False


def null():
    global environment
    environment['GFORTRAN'] = None


def is_installed(environ, version):
    global environment, gfortran_found
    set_debug(DEBUG)
    try:
        gfort = find_program('gfortran')
        gfortran_found = True
    except Exception, e:
        if DEBUG:
            print e
        return gfortran_found

    ## Unify GCC and GFortran default outputs
    if gcc_is_64bit():
        os.environ['FFLAGS'] = '-arch x86_64'
        os.environ['FCFLAGS'] = '-arch x86_64'
    else:
        os.environ['FFLAGS'] = '-arch i686'
        os.environ['FCFLAGS'] = '-arch i686'

    environment['GFORTRAN'] = gfort
    return gfortran_found


def install(environ, version, locally=True):
    if not gfortran_found:
        website = ('http://gcc.gnu.org',)
        if 'windows' in platform.system().lower():
            if version is None:
                version = '20120426'
            website = ('http://sourceforge.net/projects/mingw/',
                       'files/Installer/mingw-get-inst/mingw-get-inst-' +
                       str(version) + '/')
        if 'darwin' in platform.system().lower() and system_uses_macports():
            raise Exception('GFortran does not appear to be installed.')
        here = os.path.abspath(os.path.dirname(__file__))
        global_install('GFortran', website,
                       winstaller='mingw-get-inst-' + str(version) + '.exe',
                       brew='gfortran ', #+ os.path.join(here, 'g77.rb'),
                       deb='gfortran', rpm='gcc-gfortran')
        if not is_installed(environ, version):
            raise Exception('GFortran installation failed.')
