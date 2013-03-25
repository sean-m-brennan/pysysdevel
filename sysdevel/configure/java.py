#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install Antlr
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

import platform, shutil, os
from sysdevel.util import *

environment = dict()
java_found = False


def null():
    global environment
    environment['JAVA'] = None
    environment['JAVAC'] = None
    environment['JAR'] = None
    environment['CLASSPATH'] = []


def is_installed(environ, version):
    global environment, java_found
    try:
        locations = glob.glob(os.path.join('C:' + os.sep + 'OpenSCG',
                                           'openjdk*'))
        java_runtime = find_program('java', locations)
        java_compiler = find_program('javac', locations)
        jar_archiver = find_program('jar', locations)

        if not __check_java_version(java_runtime, [version]):
            return java_found
        classpaths = []
        try:
            _sep_ = ':'
            if 'windows' in platform.system().lower():
                _sep_ = ';'
            pathlist = os.environ['CLASSPATH'].split(_sep_)
            for path in pathlist:
                classpaths.append(path)
        except:
            pass
        java_found = True
    except Exception,e:
        return java_found

    environment['JAVA'] = java_runtime
    environment['JAVAC'] = java_compiler
    environment['JAR'] = jar_archiver
    environment['CLASSPATH'] = classpaths
    return java_found


def install(environ, version, target='build', locally=True):
    global environment
    if version is None:
        version = '1.6.0'
    sub = str(version).split('.')[1]
    website = 'http://www.java.com/'
    installer = None
    if 'windows' in platform.system().lower():
        website = 'http://oscg-downloads.s3.amazonaws.com/installers/'
        installer = 'oscg-openjdk6b24-1-windows-installer.exe'
    global_install('Java', website,
                   installer,
                   'openjdk' + sub,
                   'openjdk-' + sub + '-jdk',
                   'java-1.' + str(version) + '-openjdk-devel')
    if not is_installed(environ, version):
        raise Exception('Java installation failed.')


def __check_java_version(java_cmd, version_list):
    import subprocess
    cmd_line = [java_cmd, '-version']
    p = subprocess.Popen(cmd_line,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    for ver in version_list:
        if ver is None:
            continue
        if not ver in out and not ver in err:
            return False
    return True
