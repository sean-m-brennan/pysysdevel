#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find USB library
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
usb_found = False
DEBUG = False


def null():
    global environment
    environment['USB_INCLUDE_DIR'] = ''
    environment['USB_LIB_DIR'] = None
    environment['USB_LIBRARIES'] = []
    environment['USB_LIBS'] = []


def is_installed(environ, version):
    global environment, usb_found
    set_debug(DEBUG)
    base_dirs = []
    try:
        base_dirs.append(environ['MSYS_DIR'])
    except:
        pass
    try:
        inc_dir = find_header('usb.h', base_dirs)
        lib_dir, libs  = find_libraries('usb', base_dirs)
        usb_found = True
    except Exception, e:
        if DEBUG:
            print e
        return usb_found

    environment['USB_INCLUDE_DIR'] = inc_dir
    environment['USB_LIB_DIR'] = lib_dir
    environment['USB_LIBRARIES'] = libs
    environment['USB_LIBS'] = ['usb']
    return usb_found


def install(environ, version, locally=True):
    if not usb_found:
        if version is None:
            version = '1.0.9'
        major = '.'.join(version.split('.')[:2])
        website = ('http://prdownloads.sourceforge.net/project/libusb',
                   'libusb-' + major + '/libusb-' + version + '/')
        if locally or 'windows' in platform.system().lower():
            src_dir = 'libusb-' + str(version)
            archive = src_dir + '.tar.bz2'
            autotools_install(environ, website, archive, src_dir, locally)
        else:
            global_install('USB', website,
                           brew='libusb', port='libusb-devel',
                           deb='libusb-dev', rpm='libusb-devel')
        if not is_installed(environ, version):
            raise Exception('USB installation failed.')
