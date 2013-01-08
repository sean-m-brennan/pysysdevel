#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install Matplotlib
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
matplotlib_found = False


def null():
    global environment
    environment['MATPLOTLIB_VERSION'] = None
    environment['MATPLOTLIB_DATA_FILES'] = []


def is_installed(version=None):
    global environment, matplotlib_found
    try:
        import matplotlib
        ver = matplotlib.__version__
        if not version is None and ver < version:
            print 'Found matplotlib v.' + ver
            return matplotlib_found
        environment['MATPLOTLIB_VERSION'] = ver
        environment['MATPLOTLIB_DATA_FILES'] = matplotlib.get_py2exe_datafiles()
        matplotlib_found = True
    except Exception,e:
        print 'Matplotlib not found: ' + str(e)
    return matplotlib_found


def install(target='build', version=None):
    global environment
    if not matplotlib_found:
        import matplotlib
        website = 'https://github.com/downloads/matplotlib/matplotlib/'
        if version is None:
            version = '1.2.0'
        archive = 'matplotlib-' + version + '.tar.gz'
        install_pypkg_locally('matplotlib-' + version, website, archive, target)
        environment['MATPLOTLIB_VERSION'] = version

        ## matplotlib.get_py2exe_datafiles (can't re-import properly here)
        datapath = os.path.abspath(os.path.join(target, local_lib_dir,
                                                'matplotlib', 'mpl-data'))
        head, tail = os.path.split(datapath)
        d = {}
        for root, dirs, files in os.walk(datapath):
            # Need to explicitly remove cocoa_agg files or py2exe complains
            # NOTE I dont know why, but do as previous version
            if 'Matplotlib.nib' in files:
                files.remove('Matplotlib.nib')
            files = [os.path.join(root, filename) for filename in files]
            root = root.replace(tail, 'mpl-data')
            root = root[root.index('mpl-data'):]
            d[root] = files
        environment['MATPLOTLIB_DATA_FILES'] = d.items()
        sys.path.insert(0, os.path.join(target, local_lib_dir))
