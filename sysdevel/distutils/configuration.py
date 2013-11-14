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
Configuration classes
"""

import os
import sys
import platform
import traceback
import subprocess

from .prerequisites import *
from .filesystem import glob_insensitive
from .building import process_progress
from . import options


class config(object):
    def __init__(self, dependencies=[], debug=False):
        self.dependencies = dependencies
        self.debug = debug
        self.environment = dict()
        self.found = False

    def null(self):
        pass

    def is_installed(self, environ, version):
        raise NotImplementedError('is_installed')

    def install(self, environ, version, locally=True):
        raise NotImplementedError('install')



class lib_config(config):
    def __init__(self, lib, header, dependencies=[], debug=False):
        config.__init__(self, dependencies, debug)
        self.lib = lib
        self.hdr = header


    def null(self):
        self.environment[self.lib.upper() + '_INCLUDE_DIR'] = None
        self.environment[self.lib.upper() + '_LIB_DIR'] = None
        self.environment[self.lib.upper() + '_SHLIB_DIR'] = None
        self.environment[self.lib.upper() + '_LIB_FILES'] = []
        self.environment[self.lib.upper() + '_LIBRARIES'] = []


    def is_installed(self, environ, version=None):
        options.set_debug(self.debug)

        locations = []
        limit = False
        if self.lib.upper() + '_LIB_DIR' in environ and \
                environ[self.lib.upper() + '_LIB_DIR']:
            locations.append(environ[self.lib.upper() + '_LIB_DIR'])
            limit = True
            if self.lib.upper() + '_INCLUDE_DIR' in environ and \
                    environ[self.lib.upper() + '_INCLUDE_DIR']:
                locations.append(environ[self.lib.upper() + '_INCLUDE_DIR'])

        if not limit:
            try:
                locations += os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
                locations += os.environ['CPATH'].split(os.pathsep)
            except:
                pass
            try:
                locations.append(os.environ[self.lib.upper() + '_ROOT'])
            except:
                pass
            for d in programfiles_directories():
                locations.append(os.path.join(d, 'GnuWin32'))
                locations += glob_insensitive(d, self.lib + '*')
            try:
                locations.append(environ['MINGW_DIR'])
                locations.append(environ['MSYS_DIR'])
            except:
                pass
        try:
            if self.hdr:
                incl_dir = find_header(self.hdr, locations, limit=limit)
            lib_dir, lib = find_library(self.lib, locations, limit=limit)
            self.found = True
        except Exception:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        if self.hdr:
            self.environment[self.lib.upper() + '_INCLUDE_DIR'] = incl_dir
        self.environment[self.lib.upper() + '_LIB_DIR'] = lib_dir
        #self.environment[self.lib.upper() + '_SHLIB_DIR'] = lib_dir #FIXME
        self.environment[self.lib.upper() + '_LIB_FILES'] = [lib]
        self.environment[self.lib.upper() + '_LIBRARIES'] = [self.lib]
        return self.found


    def install(self, environ, version, locally=True):
        raise NotImplementedError('lib' + self.lib + ' installation')



class py_config(config):
    def __init__(self, pkg, version, dependencies=[], debug=False):
        config.__init__(self, dependencies, debug)
        self.pkg = pkg
        self.version = version


    def is_installed(self, environ, version=None):
        try:
            impl = __import__(self.pkg.lower())
            check_version = False
            if hasattr(impl, '__version__'):
                ver = impl.__version__
                check_version = True
            elif hasattr(impl, 'version'):
                ver = impl.version
                check_version = True
            if check_version:
                if compare_versions(ver, version) == -1:
                    return self.found
            self.found = True
        except Exception:
            if self.debug:
                print(sys.exc_info()[1])
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'https://pypi.python.org/packages/source/' + \
                self.pkg[0] + '/' + self.pkg + '/'
            if version is None:
                version = self.version
            src_dir = self.pkg + '-' + str(version)
            archive = src_dir + '.tar.gz'
            try:
                install_pypkg(src_dir, website, archive, locally=locally)
            except Exception:
                archive = src_dir + '.zip'
                install_pypkg(src_dir, website, archive, locally=locally)
            if not self.is_installed(environ, version):
                raise Exception(self.pkg + ' installation failed.')



class file_config(config):
    def __init__(self, dependencies=[], debug=False):
        config.__init__(self, dependencies, debug)


    def is_installed(self, environ, version=None):
        return False  ## always fetch



class prog_config(config):
    def __init__(self, exe, dependencies=[], debug=False):
        config.__init__(self, dependencies, debug)
        self.exe = exe


    def null(self):
        self.environment[self.exe.upper()] = None


    def is_installed(self, environ, version=None):
        options.set_debug(self.debug)
        limit = False
        locations = []
        if self.exe.upper() in environ and environ[self.exe.upper()]:
            locations.append(os.path.dirname(environ[self.exe.upper()]))
            limit = True

        if not limit:
            try:
                locations.append(os.environ[self.exe.upper() + '_ROOT'])
            except:
                pass
            try:
                locations.append(environ['MINGW_DIR'])
                locations.append(environ['MSYS_DIR'])
            except:
                pass

        try:
            program = find_program(self.exe, locations, limit=limit)
            self.found = True
        except Exception:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        self.environment[self.exe.upper()] = program
        return self.found


    def install(self, environ, version, locally=True):
        raise NotImplementedError(self.exe + ' installation')



class nodejs_config(config):
    def __init__(self, module, dependencies=['node'], debug=False):
        if not 'node' in dependencies:
            dependencies.append('node')
        config.__init__(self, dependencies, debug)
        self.module = module


    def is_installed(self, environ, version=None):
        cmd_line = [environ['NPM'], 'list', self.module.lower()]
        return self.__check_installed(cmd_line) or \
            self.__check_installed(cmd_line + ['-g'])


    def __check_installed(self, cmd_line):
        p = subprocess.Popen(cmd_line,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if '(empty)' in out:
            return False
        return True


    def install(self, environ, version, locally=True):
        if not self.found:
            pre = []
            post = []
            if not locally:
                if not 'windows' in platform.system().lower() and \
                        not system_uses_homebrew():
                    pre.append('sudo')
                post.append('-g')

            if self.debug:
                log = sys.stdout
            else:
                log_file = os.path.join(options.target_build_dir,
                                        'node-' + self.module.lower() + '.log')
                log = open(log_file, 'w')

            cmd_line = pre + [environ['NPM'], 'update'] + post
            try:
                p = subprocess.Popen(cmd_line, stdout=log, stderr=log)
                status = process_progress(p, options.VERBOSE)
            except KeyboardInterrupt:
                p.terminate()
                log.close()
                e = sys.exc_info()[1]
                raise e
            if status != 0:
                log.close()
                sys.stdout.write(' failed; See ' + log_file)
                raise Exception('NPM update is required, but could not be ' +
                                'installed; See ' + log_file)

            cmd_line = pre + [environ['NPM'], 'install', 'node-webgl'] + post
            try:
                p = subprocess.Popen(cmd_line, stdout=log, stderr=log)
                status = process_progress(p, options.VERBOSE)
            except KeyboardInterrupt:
                p.terminate()
                log.close()
                e = sys.exc_info()[1]
                raise e
            if status != 0:
                log.close()
                if log_file:
                    sys.stdout.write(' failed; See ' + log_file)
                    raise Exception('Node-' + self.module + ' is required, ' +
                                    'but could not be installed; See ' + log_file)
                else:
                    sys.stdout.write(' failed')
                    raise Exception('Node-' + self.module + ' is required, ' +
                                    'but could not be installed.')
