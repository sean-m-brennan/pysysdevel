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

import os
import sys
import platform


class FatalError(SystemExit):
    """
    Uncatchable error, exits uncleanly.
    """
    def __init__(self, what):
        sys.stderr.write('FatalError: ' + what + '\n')
        sys.stderr.flush()
        os._exit(-1)


def simplify_version(version):
    if isinstance(version, float):
        return str(version)
    elif isinstance(version, str):
        ver_tpl = version.split('.')
        return ver_tpl[0] + '.' + ver_tpl[1]


def configure_system(prerequisite_list, version, required_python_version='2.4',
                     install=True, quiet=False):
    '''
    Given a list of required software and optionally a Python version,
    verify that python is the proper version and that
    other required software is installed.
    Install missing prerequisites that have an installer defined.
    '''
    skip = False
    for idx, arg in enumerate(sys.argv[:]):
        if arg.startswith('clean'):
            skip = True
            quiet = True

    pyver = simplify_version(platform.python_version())
    reqver = simplify_version(required_python_version)
    if pyver < reqver:
        raise FatalError('Python version >= ' + reqver + ' is required.  ' +
                         'You are running version ' + pyver)

    if not quiet:
        sys.stdout.write('CONFIGURE \n')
    environment = dict()
    environment['PACKAGE_VERSION'] = version

    if 'windows' in platform.system().lower():
        prerequisite_list.insert(0, 'mingw')
    for help_name in prerequisite_list:
        environment = __configure_package(environment, help_name,
                                          skip, install, quiet)


def __configure_package(environment, help_name, skip, install, quiet):
    req_version = None
    if not isinstance(help_name, basestring):
        req_version = help_name[1]
        help_name = help_name[0]
    full_name = 'sysdevel.configure.' + help_name
    try:
        __import__(full_name)
        return __run_helper__(environment, help_name, full_name,
                              req_version, skip, install, quiet)
    except ImportError, e:
        full_name = 'sysdevel.configure.' + help_name + '_py'
        try:
            __import__(full_name)
            return __run_helper__(environment, help_name, full_name,
                                  req_version, skip, install, quiet)
        except ImportError, e:
            sys.stderr.write('No setup helper module ' + help_name + '\n')
            raise e


def __run_helper__(environment, short_name, long_name, version,
                   skip, install, quiet):
    helper = sys.modules[long_name]
    dependencies = []
    if hasattr(helper, 'DEPENDENCIES'):
        dependencies = helper.DEPENDENCIES
    for dep in dependencies:
        environment = __configure_package(environment, dep, skip, install, quiet)
    if not quiet:
        sys.stdout.write('Checking for ' + short_name + '  ')
        if not version is None:
            sys.stdout.write('v.' + version + '  ')
        sys.stdout.flush()
    if skip:
        helper.null()
    elif not helper.is_installed(environment, version):
        if not install:
            raise Exception(help_name + ' cannot be found.')
        helper.install(environment, version)
    elif not quiet:
        sys.stdout.write('\n')
    return dict(helper.environment.items() + environment.items())


