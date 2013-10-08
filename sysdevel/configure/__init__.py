"""
Copyright 2013.  Los Alamos National Security, LLC.
This material was produced under U.S. Government contract
DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which is
operated by Los Alamos National Security, LLC for the U.S. Department
of Energy. The U.S. Government has rights to use, reproduce, and
distribute this software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS
NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should be
clearly marked, so as not to confuse it with the version available
from LANL.

Licensed under the Mozilla Public License, Version 2.0 (the
"License"); you may not use this file except in compliance with the
License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/2.0/

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.
"""

"""
Entry point for finding/installing required libraries
"""

import os
import sys
import platform
import traceback

from sysdevel import util


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


def configure_system(prerequisite_list, version,
                     required_python_version='2.4', install=True, quiet=False):
    '''
    Given a list of required software and optionally a Python version,
    verify that python is the proper version and that
    other required software is installed.
    Install missing prerequisites that have an installer defined.
    '''
    environment = dict()
    try:
        environment = util.read_cache()
        skip = False
        for idx, arg in enumerate(sys.argv[:]): #FIXME?? argv[:]):
            if arg.startswith('clean') or arg.startswith('dependencies'):
                skip = True
                quiet = True

        pyver = simplify_version(platform.python_version())
        reqver = simplify_version(required_python_version)
        if pyver < reqver:
            raise FatalError('Python version >= ' + reqver + ' is required.  ' +
                             'You are running version ' + pyver)

        if not quiet:
            sys.stdout.write('CONFIGURE  ')
            if len(environment):
                sys.stdout.write('(from cache)')
            sys.stdout.write('\n')
        environment['PACKAGE_VERSION'] = version

        prerequisite_list.insert(0, 'httpsproxy_urllib2_py')
        if 'windows' in platform.system().lower() and \
           util.in_prerequisites('mingw', prerequisite_list) and \
           util.in_prerequisites('boost', prerequisite_list) and not \
           util.in_prerequisites('msvcrt', prerequisite_list):
            print "WARNING: if you're using the boost-python DLL, " + \
                "also add 'msvcrt' as a prereuisite."
        if 'darwin' in platform.system().lower() and \
           not util.in_prerequisites('macports', prerequisite_list) and \
           not util.in_prerequisites('homebrew', prerequisite_list):
            if util.system_uses_macports():
                prerequisite_list.insert(0, 'macports')
            elif util.system_uses_homebrew():
                prerequisite_list.insert(0, 'homebrew')
            else:
                print "WARNING: neither MacPorts nor Homebrew detected. " +\
                    "All required libraries will be built locally."

        for help_name in prerequisite_list:
            environment = __configure_package(environment, help_name,
                                              skip, install, quiet)
        util.save_cache(environment)
    except Exception, e:
        log = open('config.err', 'w')
        #TODO logging module is probably the way to go instead
        log.write('Configuration error:\n' + traceback.format_exc())
        log.close()
        sys.stdout.write('Configuration error. Prerequisites might be present, so building anyway...\n')
        #FIXME advise on running 'setup.py dependencies' and installing by hand
    return environment


def __configure_package(environment, help_name, skip, install, quiet):
    req_version = None
    if not isinstance(help_name, basestring):
        req_version = help_name[1]
        help_name = help_name[0]
    base = help_name
    full_name = 'sysdevel.configure.' + help_name
    try:
        __import__(full_name)
    except ImportError:
        full_name = 'sysdevel.configure.' + help_name + '_py'
        try:
            __import__(full_name)
        except ImportError:
            full_name = 'sysdevel.configure.' + help_name + '_js'
            try:
                __import__(full_name)
            except ImportError:
                sys.stderr.write('No setup helper module ' + base + '\n')
                raise ImportError('No configuration for ' + help_name)
    return __run_helper__(environment, help_name, full_name,
                          req_version, skip, install, quiet)


configured = []

def __run_helper__(environment, short_name, long_name, version,
                   skip, install, quiet):
    helper = sys.modules[long_name]
    configured.append(short_name)
    cfg = helper.configuration()
    for dep in cfg.dependencies:
        dep_name = dep
        if not isinstance(dep, basestring):
            dep_name = dep[0]
        if dep_name in configured:
            continue
        environment = __configure_package(environment, dep,
                                          skip, install, quiet)
        util.save_cache(environment)
    if not quiet:
        sys.stdout.write('Checking for ' + short_name + ' ')
        if not version is None:
            sys.stdout.write('v.' + version)
        sys.stdout.write('\n')
        sys.stdout.flush()
    if skip:
        cfg.null()
    elif not cfg.is_installed(environment, version):
        if not install:
            raise Exception(help_name + ' cannot be found.')
        cfg.install(environment, version)
    env = dict(cfg.environment.items() + environment.items())
    if not 'PREREQUISITES' in env:
        env['PREREQUISITES'] = [short_name]
    else:
        tmp_env = env['PREREQUISITES'] + [short_name]
        env['PREREQUISITES'] = list(set(tmp_env))
    util.save_cache(env)  ## intermediate cache
    return env
