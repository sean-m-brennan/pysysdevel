#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find NASA Common Data Format library
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

import os, platform, subprocess

from sysdevel.util import *

environment = dict()
cdf_found = False


def null():
    global environment
    environment['CDF_INCLUDE_DIR'] = None
    environment['CDF_LIB_DIR'] = None
    environment['CDF_LIBS'] = []
    environment['CDF_LIBRARIES'] = []


def is_installed(environ, version):
    global environment, cdf_found
    lib_name = 'cdf'
    if 'windows' in platform.system().lower():
        lib_name += 'NativeLibrary'
    base_dirs = []
    if 'windows' in platform.system().lower():
        base_dirs.append(os.path.join('C:', os.sep, 'CDF Distribution',
                                      'cdf' + version + '-dist'))
        try:
            base_dirs.append(environ['MSYS_DIR'])
        except:
            pass
    try:
        incl_dir = find_header('cdf.h', base_dirs)
        lib_dir, lib = find_library('cdf', base_dirs)
        cdf_found = True
    except Exception,e:
        return cdf_found

    environment['CDF_INCLUDE_DIR'] = incl_dir
    environment['CDF_LIB_DIR'] = lib_dir
    environment['CDF_LIBS'] = [lib]
    environment['CDF_LIBRARIES'] = [lib_name]
    return cdf_found


def install(environ, version, target='build'):
    if not cdf_found:
        if version is None:
            version = '34_1'
        website = ('http://cdf.gsfc.nasa.gov/',)
        if not 'darwin' in platform.system().lower():
            website = ('http://cdaweb.gsfc.nasa.gov/',
                       'pub/software/cdf/dist/cdf' + str(version))
            if 'windows' in platform.system().lower():
                os_dir = 'w32'
                oper_sys = 'mingw'
            elif 'linux' in platform.system().lower():
                oper_sys = os_dir = 'linux'
            website += '/' + os_dir + '/'
            here = os.path.abspath(os.getcwd())
            src_dir = 'cdf' + str(version) + '-dist'
            archive = src_dir + '-cdf.tar.gz'
            fetch(''.join(website), archive, archive)
            unarchive(os.path.join(here, download_dir, archive),
                      target, src_dir)
            build_dir = os.path.join(src_dir, '_build')
            mkdir(build_dir)
            os.chdir(build_dir)
            if 'windows' in platform.system().lower():
                ## assumes MinGW installed and detected
                mingw_check_call(environ,
                                 ['make',  'OS=mingw', 'ENV=gnu', 'all'])
                mingw_check_call(environ,
                                 ['make', 'INSTALLDIR=/', 'install'])
            else:
                sudo_prefix = []
                if not as_admin():
                    sudo_prefix = ['sudo']
                subprocess.check_call(['make', 'OS=linux', 'ENV=gnu', 'all'])
                subprocess.check_call(sudo_prefix + 
                                      ['make', 'INSTALLDIR=/usr', 'install'])
            os.chdir(here)
        else:
            global_install('CDF', website,
                           None,
                           'cdf',
                           None,
                           None)
        if not is_installed(environ, version):
            raise Exception('CDF installation failed.')
