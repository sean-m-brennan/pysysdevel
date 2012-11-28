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


def null():
    global environment
    environment['PYWEBSOCKET_ROOT'] = None


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
        website = 'http://pywebsocket.googlecode.com/files/'
        ver = '0.7.6'
        archive = 'mod_pywebsocket-' + ver + '.tar.gz'
        pkg_dir = os.path.join('pywebsocket-' + ver, 'src')
        install_pypkg_locally(pkg_dir, website, archive, target)
