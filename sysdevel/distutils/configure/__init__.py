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
# pylint: disable=W0105
"""
Entry point for finding/installing required libraries
"""

import os
import sys
import platform
import traceback

from sysdevel.distutils.prerequisites import read_cache, save_cache, in_prerequisites
from sysdevel.distutils.prerequisites import system_uses_macports, system_uses_homebrew
from sysdevel.distutils.prerequisites import requirement_versioning
from sysdevel.distutils.configuration import dynamic_module, latest_pypi_version
from sysdevel.distutils.configuration import is_pypi_listed, find_package_config
from sysdevel.distutils.pypi_exceptions import pypi_exceptions
from sysdevel.distutils.filesystem import mkdir
from sysdevel.distutils import options as opts
from sysdevel.util import is_string


class FatalError(SystemExit):
    """
    Uncatchable error, exits uncleanly.
    """
    # pylint: disable=W0231
    def __init__(self, what):
        sys.stderr.write('Fatal Error: ' + what + '\n')
        sys.stderr.flush()
        os._exit(-1)  # pylint: disable=W0212



def simplify_version(version):
    if isinstance(version, float):
        return str(version)
    elif isinstance(version, str):
        ver_tpl = version.split('.')
        return ver_tpl[0] + '.' + ver_tpl[1]


# pylint: disable=W0102
def configure_system(prerequisite_list, version,
                     required_python_version='2.4', install=None, quiet=False,
                     sublevel=None, out=sys.stdout, err=sys.stderr,
                     locally=None, download=None, options=dict()):
    '''
    Given a list of required software and optionally a Python version,
    verify that python is the proper version and that
    other required software is installed.
    Install missing prerequisites that have an installer defined.
    '''
    if locally is None:  ## parameter value overrides
        if 'locally' in options.keys():
            locally = options['locally']
        else:
            locally = True  ## default value
    if install is None:  ## parameter value overrides
        if 'install' in options.keys():
            install = options['install']
        else:
            install = True  ## default value
    if download is None:  ## parameter value overrides
        if 'download' in options.keys():
            download = options['download']
        else:
            download = False  ## default value
    if sublevel is None:  ## parameter value overrides
        if 'sublevel' in options.keys():
            sublevel = options['sublevel']
        else:
            sublevel = 0  ## default value
    opts.set_top_level(sublevel)

    environment = dict()
    try:
        environment = read_cache()
        skip = False
        for arg in sys.argv:
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
                environment = find_package_config(help_name, __run_helper__,
                                                  environment, skip,
                                                  install, quiet,
                                                  out, err, locally, download)
        save_cache(environment)
    except Exception:  # pylint: disable=W0703
        logfile = os.path.join(opts.target_build_dir, 'config.log')
        if not os.path.exists(opts.target_build_dir):
            mkdir(opts.target_build_dir)
        log = open(logfile, 'a')
        log.write('** Configuration error. **\n' + traceback.format_exc())
        log.close()
        err.write('Configuration error; see ' + logfile + ' for details.\n' +
                  "If the build fails, run 'python setup.py dependencies " + 
                  "--show'\nand install the listed packages by hand.\n" +
                  'Prerequisites might be present, so building anyway...\n')
    return environment


def configure_package(which, locally=True):
    return find_package_config(which, __run_helper__, dict(), skip=False,
                               install=True, quiet=False, locally=locally)


configured = []

def __run_helper__(short_name, helper, version, strict,
                   environment, skip, install, quiet,
                   out=sys.stdout, err=sys.stderr,
                   locally=True, download=False):
    configured.append(short_name)
    try:
        cfg = helper.configuration()
    except Exception:
        ver_info = ''
        if version:
            ver_info = ' v.' + str(version)
        err.write('Error loading ' + short_name + ver_info +
                  ' configuration.\n')
        raise
    for dep in cfg.dependencies:
        dep_name = dep
        if not is_string(dep):
            dep_name = dep[0]
        if dep_name in configured:
            continue
        environment = find_package_config(dep, __run_helper__, 
                                          environment, skip, install, quiet,
                                          out, err, locally, download)
        if not environment is None:
            save_cache(environment)
    environment = read_cache()
    if not quiet:
        msg = 'Checking for ' + short_name
        if version:
            msg += ' v.' + version
        if strict:
            msg += ' (strict)'
        msg += ' ' * (40 - len(msg))
        out.write(msg)
        out.flush()
    if download:
        cfg.download(environment, version, strict)

    if skip:
        cfg.null()
    elif not cfg.is_installed(environment, version, strict):
        if install:
            if not quiet:
                out.write('Installing...\n')
            cfg.install(environment, version, strict, locally)
        elif not quiet:
            out.write('not found.\n')
    elif cfg.force:
        if install:
            if not quiet:
                out.write('Forcing install...\n')
            cfg.install(environment, version, strict, locally)
        elif not quiet:
            out.write('found.\n')
    elif not quiet:
        out.write('found.\n')
    env = dict(list(cfg.environment.items()) + list(environment.items()))
    if not 'PREREQUISITES' in env:
        env['PREREQUISITES'] = [short_name]
    else:
        tmp_env = env['PREREQUISITES'] + [short_name]
        env['PREREQUISITES'] = list(set(tmp_env))
    save_cache(env)  ## intermediate cache
    return env
