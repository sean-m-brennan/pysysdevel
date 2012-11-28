#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find NASA CDF library
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

from pydevel.util import *

environment = dict()
cdf_found = False


def null():
    global environment
    environment['CDF_INCLUDE_DIR'] = None
    environment['CDF_LIB_DIR'] = None
    environment['CDF_LIBRARY'] = None


def is_installed():
    global environment, cdf_found
    try:
        incl_dir = find_header('cdf.h')
        environment['CDF_INCLUDE_DIR'] = incl_dir
        environment['CDF_LIB_DIR'], lib = find_library('cdf')
        environment['CDF_LIBRARY'] = lib
        cdf_found = True
    except Exception,e:
        cdf_found = False
    return cdf_found


def install(target='build'):
    global environment
    version = '34_1'
    website = 'http://cdaweb.gsfc.nasa.gov/pub/software/cdf/dist/cdf' + version
    if 'windows' in platform.system().lower():
        os_dir = 'w32'
        oper_sys = 'mingw'
    elif 'darwin' in platform.system().lower():
        oper_sys = os_dir = 'macosx'
    else:
        oper_sys = os_dir = 'linux'
    website += '/' + os_dir + '/'
    here = os.path.abspath(os.getcwd())
    abs_target = os.path.abspath(target)
    if not cdf_found:
        try:
            import urllib, tarfile, subprocess
            download_file = 'cdf' + version + '-dist-cdf.tar.gz'
            set_downloading_file(download_file)
            if not os.path.exists(download_file):
                urllib.urlretrieve(website + download_file, download_file,
                                   download_progress)
                sys.stdout.write('\n')
            if not os.path.exists(target):
                os.makedirs(target)
            os.chdir(target)
            pkg_dir = 'cdf' + version + '-dist'
            src_dir = os.path.abspath(os.path.join(pkg_dir, 'src'))
            if not os.path.exists(pkg_dir):
                z = tarfile.open(os.path.join(here, download_file), 'r:gz')
                z.extractall()
            os.chdir(pkg_dir)
            log = open(pkg_dir + '.log', 'w')
            subprocess.check_call(['make', 'OS=' + oper_sys, 'ENV=gnu', 'all'],
                                  stdout=log)
            log.close()
            environment['CDF_INCLUDE_DIR'] = os.path.join(src_dir, 'include')
            environment['CDF_LIB_DIR'], lib = find_library('cdf', [src_dir],
                                                           limit=True)
            environment['CDF_LIBRARY'] = lib
            os.chdir(here)
        except Exception, e:
            os.chdir(here)
            print e
            raise Exception('CDF not found. (include=' +
                            str(environment['CDF_INCLUDE_DIR']) + ' library=' +
                            str(environment['CDF_LIB_DIR']) + ')')
