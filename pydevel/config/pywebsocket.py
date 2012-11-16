#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install mod_pywebsocket
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

from pydevel.util import *

environment = dict()
pywebsocket_found = False


def is_installed():
    global environment, pywebsocket_found
    try:
        pywebsocket_root = os.environ['PYWEBSOCKET_ROOT']
        environment['PYWEBSOCKET_ROOT'] = pywebsocket_root
        sys.path.insert(0, os.path.join(pywebsocket_root, 'build', 'lib'))
        pywebsocket_found = True
    except:
        try:
            import mod_pywebsocket
            pywebsocket_found = True
        except:
            pass
    return pywebsocket_found


def install(target='build'):
    global environment
    if not pywebsocket_found:
        try:
            import urllib, tarfile, subprocess
            website = 'http://pywebsocket.googlecode.com/files/'
            ver = '0.7.6'
            here = os.path.abspath(os.getcwd())
            download_file = 'mod_pywebsocket-' + ver + '.tar.gz'
            if not os.path.exists(target):
                os.makedirs(target)
            os.chdir(target)
            if not os.path.exists(download_file):
                set_downloading_file(website + download_file)
                urllib.urlretrieve(website + download_file, download_file,
                                   download_progress)
            pkg_dir = os.path.join('pywebsocket-' + ver, 'src')
            if not os.path.exists(pkg_dir):
                z = tarfile.open(download_file, 'r:gz')
                z.extractall()             
            os.chdir(pkg_dir)
            cmd_line = ['python', 'setup.py', 'install',
                        '--home=' + os.path.join(here, target)]
            status = subprocess.call(cmd_line)
            if status != 0:
                raise Exception("Command '" + str(cmd_line) +
                                "' returned non-zero exit status "
                                + str(status))
            target_dir = os.path.join(here, target, 'lib', 'python')
            if not target_dir in sys.path:
                sys.path.insert(0, target_dir)
            os.chdir(here)
        except Exception,e:
            raise Exception('Unable to install pywebsocket: ' + str(e))
