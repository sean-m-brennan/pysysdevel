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


def is_installed(version=None):
    global environment, cdf_found
    if version is None:
        version = '34_1'
    try:
        base_dirs = []
        if 'windows' in platform.system().lower():
            base_dirs += [os.path.join('C:', os.sep, 'CDF Distribution',
                                       'cdf' + version + '-dist']
        incl_dir = find_header('cdf.h', base_dirs)
        environment['CDF_INCLUDE_DIR'] = incl_dir
        lib_name = 'cdf'
        if 'windows' in platform.system().lower():
            lib_name += 'NativeLibrary'
        environment['CDF_LIB_DIR'], lib = find_library('cdf', base_dirs)
        environment['CDF_LIBRARY'] = lib
        cdf_found = True
    except Exception,e:
        cdf_found = False
    return cdf_found


def install(target='build', version=None):
    global environment
    if version is None:
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
    if 'windows' in platform.system().lower():
        raise Exception('Install CDF maually from ' + website)
    here = os.path.abspath(os.getcwd())
    abs_target = os.path.abspath(target)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    if not cdf_found:
        try:
            import tarfile, subprocess
            download_file = 'cdf' + version + '-dist-cdf.tar.gz'
            set_downloading_file(download_file)
            if not os.path.exists(os.path.join(download_dir, download_file)):
                urlretrieve(website + download_file,
                            os.path.join(download_dir, download_file),
                            download_progress)
                sys.stdout.write('\n')
            if not os.path.exists(target):
                os.makedirs(target)
            os.chdir(target)
            pkg_dir = 'cdf' + version + '-dist'
            src_dir = os.path.abspath(os.path.join(pkg_dir, 'src'))
            if not os.path.exists(pkg_dir):
                z = tarfile.open(os.path.join(here, download_dir,
                                              download_file), 'r:gz')
                z.extractall()
            os.chdir(pkg_dir)
            log_file = pkg_dir + '.log'
            log = open(log_file, 'w')
            cmd_line = ['make', 'OS=' + oper_sys, 'ENV=gnu', 'all']
            try:
                sys.stdout.write('PREREQUISITE cdf ')
                p = subprocess.Popen(cmd_line, stdout=log, stderr=log)
                status = process_progress(p)
                log.close()
            except KeyboardInterrupt,e:
                p.terminate()
                log.close()
                raise e
            if status != 0:
                sys.stdout.write(' failed; See ' + log_file + '\n')
                raise Exception("Command '" + cmd_line + "' failed: " +
                                str(status))
            else:
                sys.stdout.write(' done\n')
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
