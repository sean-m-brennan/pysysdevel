# -*- coding: utf-8 -*-
"""
Entry point for finding/installing required libraries
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

__all__ = ['antlr', 'archive', 'boost', 'cdf', 'ctypesgen', 'f2c',
           'ffnet', 'gccxml', 'gmat', 'graphviz', 'gsl', 'hdf5', 'mingw',
           'mpich', 'pyjamas', 'pyplusplus', 'pyserial', 'pywebsocket',
           'sqlite3', 'wxwidgets',]


import os, sys, platform

def configure_system(prerequisite_list, version,
                     required_python_version='2.4', install=True):
    '''
    Given a list of required software and optionally a Python version,
    verify that python is the proper version and that
    other required software is installed.
    Install missing prerequisites that have an installer defined.
    '''
    pyver = platform.python_version() 
    if pyver < required_python_version:
        raise Exception('Python version > ' + required_python_version +
                        ' is required.  Running ' + pyver)

    environment = dict()
    for help_name in prerequisite_list:
        full_name = 'pydevel.config.' + help_name
        try:
            __import__(full_name)
            helper = sys.modules[full_name]
            if not helper.is_installed():
                if not install:
                    raise Exception(help_name + ' cannot be found.')
                helper.install()
            environment = dict(helper.environment.items() +
                               environment.items())
        except ImportError, e:
            print 'No setup helper module ' + help_name
            raise e

    environment['PACKAGE_VERSION'] = version

    return environment
