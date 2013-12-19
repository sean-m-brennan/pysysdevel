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

from ..prerequisites import *
from ..configuration import dynamic_module, latest_pypi_version
from ..configuration import is_pypi_listed, pypi_exceptions
from ..filesystem import mkdir
from .. import options
from ...util import is_string


DEBUG_PYPI = False
DEBUG_LOCAL = False


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
                     sublevel=0, out=sys.stdout, err=sys.stderr):
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
            out.write('CONFIGURE  ')
            if len(environment):
                out.write('(from cache)')
            out.write('\n')
        environment['PACKAGE_VERSION'] = version

        prerequisite_list.insert(0, 'httpsproxy_urllib2')
        if 'windows' in platform.system().lower() and \
           in_prerequisites('mingw', prerequisite_list) and \
           in_prerequisites('boost', prerequisite_list) and not \
           in_prerequisites('msvcrt', prerequisite_list):
            err.write("WARNING: if you're using the boost-python DLL, " +
                             "also add 'msvcrt' as a prerequisite.\n")
        if 'darwin' in platform.system().lower() and \
           not in_prerequisites('macports', prerequisite_list) and \
           not in_prerequisites('homebrew', prerequisite_list):
            if system_uses_macports():
                prerequisite_list.insert(0, 'macports')
            elif system_uses_homebrew():
                prerequisite_list.insert(0, 'homebrew')
            else:
                err.write("WARNING: neither MacPorts nor Homebrew " +
                                 "detected. All required libraries will be " +
                                 "built locally.\n")

        for help_name in prerequisite_list:
            if len(help_name) > 0:
                environment = __configure_package(environment, help_name,
                                                  skip, install, quiet,
                                                  out, err)
        save_cache(environment)
    except Exception:
        logfile = os.path.join(options.target_build_dir, 'config.log')
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
        err.write('Configuration error; see ' + logfile + ' for details.\n' +
                         'Prerequisites might be present, so building anyway...\n')
    sys.path.insert(0, os.path.join(options.target_build_dir,
                                    options.local_lib_dir))
    return environment


def __configure_package(environment, help_name, skip, install, quiet,
                        out=sys.stdout, err=sys.stderr):
    req_version = None
    if not is_string(help_name):
        req_version = help_name[1]
        help_name = help_name[0]
    elif '=' in help_name:
        n_end = help_name.find('(')
        if n_end < 0:
            n_end = help_name.find('>')
            if n_end < 0:
                n_end = help_name.find('=')
        v_begin = help_name.rfind('=') + 1
        v_end = help_name.find(')')
        req_version = help_name[v_begin:v_end]
        help_name = help_name[:n_end]
    if help_name == 'None':
        return environment

    base = help_name = help_name.strip()
    packages = [__package__ + '.', '',]
    cfg_dir = os.path.abspath(os.path.join(options.target_build_dir,
                                           '..', options.user_config_dir))
    if os.path.exists(cfg_dir):
        sys.path.insert(0, cfg_dir)
    successful = False
    for package in packages:
        if successful:
            continue
        full_name = package + help_name
        try:
            if not package and is_pypi_listed(base):
                ## Likely actual package module
                raise ImportError('Invalid config')
            __import__(full_name, globals=globals())
            helper = sys.modules[full_name]
            module_path = os.path.dirname(helper.__file__)
            if not package and \
               not module_path.endswith(options.user_config_dir):
                ## Probably an actual package module
                raise ImportError('Invalid config')
            successful = True
        except (ImportError, KeyError):
            full_name = package + help_name + '_js'
            try:
                __import__(full_name, globals=globals())
                helper = sys.modules[full_name]
                successful = True
            except (ImportError, KeyError):
                full_name = package + help_name + '_py'
                try:
                    __import__(full_name, globals=globals())
                    helper = sys.modules[full_name]
                    successful = True
                except (ImportError, KeyError):
                    if DEBUG_LOCAL and not package and not is_pypi_listed(base):
                        traceback.print_exc()
    if not successful:
        try:
            ## grab it from the Python Package Index
            if base in pypi_exceptions.keys():
                name, deps = pypi_exceptions[base]
                helper = dynamic_module(base, req_version, deps,
                                        name, DEBUG_PYPI)
            else:
                helper = dynamic_module(base, req_version, debug=DEBUG_PYPI)
        except:
            if DEBUG_PYPI:
                traceback.print_exc()
            err.write('No setup helper module ' + base + '\n')
            raise ImportError('No configuration found for ' + help_name)
    return __run_helper__(environment, help_name, helper,
                          req_version, skip, install, quiet, out, err)


configured = []

def __run_helper__(environment, short_name, helper, version,
                   skip, install, quiet, out=sys.stdout, err=sys.stderr):
    configured.append(short_name)
    try:
        cfg = helper.configuration()
    except:
        print 'Error loading ' + short_name + ' configuration.'
        raise
    for dep in cfg.dependencies:
        dep_name = dep
        if not is_string(dep):
            dep_name = dep[0]
        if dep_name in configured:
            continue
        environment = __configure_package(environment, dep,
                                          skip, install, quiet, out, err)
        save_cache(environment)
    if not quiet:
        out.write('Checking for ' + short_name + ' ')
        if not version is None:
            out.write('v.' + version)
        out.write('\n')
        out.flush()
    if skip:
        cfg.null()
    elif cfg.force or not cfg.is_installed(environment, version):
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
