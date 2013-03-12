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
antlr_found = False
java_antlr_found = False
python_antlr_found = False


def null():
    global environment
    environment['JAVA_RUNTIME'] = None
    environment['ANTLR'] = None


def is_installed(version=None):
    global environment, antlr_found, java_antlr_found, python_antlr_found
    try:
        _sep_ = ':'
        if 'windows' in platform.system().lower():
            _sep_ = ';'
        ## Sun/Oracle Java is required
        environment['JAVA_RUNTIME'] = java_runtime = find_program('java')
        _check_java_version(java_runtime, 'Sun', 'HotSpot')
        classpaths = []
        try:
            pathlist = os.environ['CLASSPATH'].split(_sep_)
            for path in pathlist:
                classpaths.append(os.path.dirname(path))
        except:
            pass
        try:
            antlr_root = os.environ['ANTLR_ROOT']
        except:
            antlr_root = None
        try:
            win_loc = os.path.join(os.environ['ProgramFiles'], 'ANTLR', 'lib')
        except:
            win_loc = None
        jarfile = find_file('antlr*3*.jar', ['/usr/share/java',
                                             '/opt/local/share/java',
                                             win_loc, antlr_root,] + classpaths)
        environment['ANTLR'] = [java_runtime,
                                "-classpath", os.path.abspath(jarfile),
                                "org.antlr.Tool",]
        java_antlr_found = True
    except Exception,e:
        print 'ANTLR not found: ' + str(e)
    try:
        import antlr3
        python_antlr_found = True
    except Exception,e:
        print 'ANTLR not found: ' + str(e)
    antlr_found = python_antlr_found and java_antlr_found
    return antlr_found


def install(target='build', version=None):
    global environment

    website = 'http://www.antlr.org/download/'
    if version is None:
        ver = '3.1.2'
    else:
        ver = version
    here = os.path.abspath(os.getcwd())
    abs_target = os.path.abspath(target)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    if not java_antlr_found:
        try:
            import tarfile
            download_file = 'antlr-' + ver + '.tar.gz'
            set_downloading_file(website + download_file)
            if not os.path.exists(os.path.join(download_dir, download_file)):
                urlretrieve(website + download_file,
                            os.path.join(download_dir, download_file),
                            download_progress)
            set_downloading_file(download_file)
            if not os.path.exists(target):
                os.makedirs(target)
            os.chdir(target)
            z = tarfile.open(os.path.join(here, download_dir, download_file),
                             'r:gz')
            z.extractall()
            jarfile = os.path.join('antlr-' + ver, 'lib',
                                   'antlr-' + ver + '.jar')
            environment['ANTLR'] = [environment['JAVA_RUNTIME'],
                                    "-classpath", os.path.abspath(jarfile),
                                    "org.antlr.Tool",]
            os.chdir(here)
        except Exception,e:
            os.chdir(here)
            raise Exception('Unable to install ANTLR: ' + str(e))

    if not python_antlr_found:
        try:
            import tarfile
            download_file = 'antlr_python_runtime-' + ver + '.tar.gz'
            set_downloading_file(download_file)
            if not os.path.exists(os.path.join(download_dir, download_file)):
                urlretrieve(website + 'Python/' + download_file,
                            os.path.join(download_dir, download_file),
                            download_progress)
            if not os.path.exists(target):
                os.makedirs(target)
            os.chdir(target)
            pkg_dir = 'antlr_python_runtime-' + ver
            if not os.path.exists(pkg_dir):
                z = tarfile.open(os.path.join(here, download_dir,
                                              download_file), 'r:gz')
                z.extractall()
            target_dir = os.path.join(here, target, local_lib_dir)
            try:
                os.makedirs(target_dir)
            except:
                pass
            try:
                shutil.copytree(os.path.join(pkg_dir, 'antlr3'),
                                os.path.join(target_dir, 'antlr3'))
            except:
                pass
            if not target_dir in sys.path:
                sys.path.insert(0, target_dir)
            os.chdir(here)
        except Exception,e:
            os.chdir(here)
            raise Exception('Unable to install ANTLR: ' + str(e))


def _check_java_version(java_cmd, vendor, version):
    import subprocess
    cmd_line = [java_cmd, '-version']
    p = subprocess.Popen(cmd_line,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if not version in out and not version in err:
        raise Exception('Using incorrect vendor or version of java; ' +
                        'should be ' + vendor + ' ' + version)
