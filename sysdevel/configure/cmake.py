"""
Find CMake
"""
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

import os

from sysdevel.util import *

environment = dict()
cmake_found = False
DEBUG = False


def null():
    global environment
    environment['CMAKE'] = None


def is_installed(environ, version):
    global environment, cmake_found
    if version is None:
        version = '2.8'

    set_debug(DEBUG)
    base_dirs = []
    for d in programfiles_directories():
        base_dirs.append(os.path.join(d, 'CMake ' + version))
    try:
        base_dirs.append(environ['MINGW_DIR'])
        base_dirs.append(environ['MSYS_DIR'])
    except:
        pass
    try:
        environment['CMAKE'] = find_program('cmake', base_dirs)
        cmake_found = True
    except Exception, e:
        if DEBUG:
            print e
    return cmake_found


def install(environ, version, locally=True):
    if not cmake_found:
        if version is None:
            version = '2.8.10.2'
        website = ('http://www.cmake.org/',
                   'files/v' + major_minor_version(version) + '/')
        #FIXME no local install
        global_install('CMake', website,
                       winstaller='cmake-' + str(version) + '-win32-x86.exe',
                       brew='cmake', port='cmake', deb='cmake', rpm='cmake')
        if not is_installed(environ, version):
            raise Exception('CMake installation failed.')
