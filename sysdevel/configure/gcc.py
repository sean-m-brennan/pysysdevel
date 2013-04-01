"""
Find/fetch/install the GCC collection
"""
import os

from sysdevel.util import *

environment = dict()
gcc_found = False
DEBUG = False


def null():
    global environment
    environment['GCC'] = None
    environment['GXX'] = None
    environment['GFORTRAN'] = None


def is_installed(environ, version):
    global environment, gcc_found
    set_debug(DEBUG)
    try:
        gcc = find_program('gcc')
        gxx = find_program('g++')
        gfort = find_program('gfortran')
        gcc_found = True
    except Exception, e:
        if DEBUG:
            print e
        return gcc_found

    environment['GCC'] = gcc
    environment['GXX'] = gxx
    environment['GFORTRAN'] = gfort
    return gcc_found


def install(environ, version, locally=True):
    if not gcc_found:
        website = ('http://gcc.gnu.org',)
        if 'windows' in platform.system().lower():
            if version is None:
                version = '20120426'
            website = ('http://sourceforge.net/projects/mingw/',
                       'files/Installer/mingw-get-inst/mingw-get-inst-' +
                       str(version) + '/')
        global_install('GCC', website,
                       'mingw-get-inst-' + str(version) + '.exe',
                       None, ## XCode + Gfortran (see HACKING)
                       'build-essential g++ gfortran ' +
                       'autoconf automake libtool gettext',
                       'gcc gcc-c++ gcc-gfortran ' +
                       'autoconf automake libtool make gettext')
        if not is_installed(environ, version):
            raise Exception('GCC installation failed.')
