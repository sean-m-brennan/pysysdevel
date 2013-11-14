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

from ..prerequisites import read_cache, save_cache, in_prerequisites
from ..prerequisites import system_uses_macports, system_uses_homebrew
from ..filesystem import mkdir
from .. import options
from ...util import is_string


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
                     required_python_version='2.4', install=True, quiet=False,
                     sublevel=0):
    '''
    Given a list of required software and optionally a Python version,
    verify that python is the proper version and that
    other required software is installed.
    Install missing prerequisites that have an installer defined.
    '''
    options.set_top_level(sublevel)
    environment = dict()
    try:
        environment = read_cache()
        skip = False
        for idx, arg in enumerate(sys.argv[:]): #FIXME?? argv[:]):
            if arg.startswith('clean'):
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

        prerequisite_list.insert(0, 'httpsproxy_urllib2')
        if 'windows' in platform.system().lower() and \
           in_prerequisites('mingw', prerequisite_list) and \
           in_prerequisites('boost', prerequisite_list) and not \
           in_prerequisites('msvcrt', prerequisite_list):
            sys.stderr.write("WARNING: if you're using the boost-python DLL, " +
                             "also add 'msvcrt' as a prerequisite.\n")
        if 'darwin' in platform.system().lower() and \
           not in_prerequisites('macports', prerequisite_list) and \
           not in_prerequisites('homebrew', prerequisite_list):
            if system_uses_macports():
                prerequisite_list.insert(0, 'macports')
            elif system_uses_homebrew():
                prerequisite_list.insert(0, 'homebrew')
            else:
                sys.stderr.write("WARNING: neither MacPorts nor Homebrew " +
                                 "detected. All required libraries will be " +
                                 "built locally.\n")

        for help_name in prerequisite_list:
            environment = __configure_package(environment, help_name,
                                              skip, install, quiet)
        save_cache(environment)
    except Exception:
        logfile = os.path.join(options.target_build_dir, 'config.err')
        if not os.path.exists(options.target_build_dir):
            mkdir(options.target_build_dir)
        if sublevel == 0:
            log = open(logfile, 'w')
        else:
            log = open(logfile, 'a')
        log.write('** Configuration error. **\n' + 
                  "If the build fails, run 'python setup.py dependencies " + 
                  "--show'\nand install the listed packages by hand.\n" +
                  traceback.format_exc())
        log.close()
        sys.stderr.write('Configuration error; see ' + logfile + ' for details.\n' +
                         'Prerequisites might be present, so building anyway...\n')
    sys.path.insert(0, os.path.join(options.target_build_dir,
                                    options.local_lib_dir))
    return environment


def __configure_package(environment, help_name, skip, install, quiet):
    req_version = None
    if not is_string(help_name):
        req_version = help_name[1]
        help_name = help_name[0]
    base = help_name = help_name.strip()
    package = __package__ + '.'
    full_name = package + help_name
    try:
        __import__(full_name, globals=globals())
    except ImportError:
        full_name = package + help_name + '_py'
        try:
            __import__(full_name, globals=globals())
        except ImportError:
            full_name = package + help_name + '_js'
            try:
                __import__(full_name, globals=globals())
            except ImportError:
                sys.stderr.write('No setup helper module ' + base + '\n')
                raise ImportError('No configuration found for ' + help_name)
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
        if not is_string(dep):
            dep_name = dep[0]
        if dep_name in configured:
            continue
        environment = __configure_package(environment, dep,
                                          skip, install, quiet)
        save_cache(environment)
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
    env = dict(list(cfg.environment.items()) + list(environment.items()))
    if not 'PREREQUISITES' in env:
        env['PREREQUISITES'] = [short_name]
    else:
        tmp_env = env['PREREQUISITES'] + [short_name]
        env['PREREQUISITES'] = list(set(tmp_env))
    save_cache(env)  ## intermediate cache
    return env
