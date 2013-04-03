#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find wxPython
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

import platform

from sysdevel.util import *

environment = dict()
wxpy_found = False


def null():
    pass


def is_installed(environ, version):
    global wxpy_found
    try:
        import wx
        ver = wx.__version__
        if compare_versions(ver, version) == -1:
            return wxpy_found
        wxpy_found = True
    except:
        pass
    return wxpy_found
    

def install(environ, version, locally=True):
    if not wxpy_found:
        if version is None:
            version = '2.9.4.0'
        short_ver = '.'.join(version.split('.')[:2])
        py_ver = ''.join(get_python_version())
        brew_extra = ''
        win_extra = '32'
        if platform.architecture()[0] == '64bit':
            brew_extra = ' --devel'
            win_extra = '64'
        website = ('http://sourceforge.net/projects/wxpython/',
                   'files/wxPython/' + str(version) + '/')
        ## NOTE: no local install
        
        global_install('wxPython', website,
                       winstaller='wxPython' + short_ver + '-win' + \
                           win_extra + '-' + str(version) + '-py' + \
                           py_ver + '.exe',
                       brew='--python wxmac' + brew_extra,
                       port='py' + py_ver + '-wxpython',
                       deb='python-wxgtk python-wxtools',
                       rpm='wxPython-devel')
        if system_uses_homebrew():
            target  = os.path.join(homebrew_prefix(), 'lib',
                                   'python' + '.'.join(get_python_version()),
                                   'site-packages', 'wx')
            if not os.path.exists(target):
                os.symlink(glob.glob(os.path.join(homebrew_prefix(), 'lib',
                                                  'python2.6', 'site-packages',
                                                  'wx-*', 'wx'))[0], target)
                       
        if not is_installed(environ, version):
            raise Exception('wxpython installation failed.')
