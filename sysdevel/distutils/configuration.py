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
Configuration classes
"""

import os
import sys
import platform
import subprocess
import imp
import glob
import traceback
import shutil
from distutils.sysconfig import get_python_lib
from types import ModuleType

from sysdevel.distutils.prerequisites import programfiles_directories, find_header, find_library, find_definitions, find_program, system_uses_homebrew, compare_versions, install_pypkg_without_fetch, RequirementsFinder, ConfigError, read_cache, requirement_versioning
from sysdevel.distutils.filesystem import glob_insensitive, mkdir
from sysdevel.distutils.fetching import urlretrieve, fetch, unarchive, open_archive, DownloadError, URLError, HTTPError, ContentTooShortError
from sysdevel.distutils.building import process_progress
from sysdevel.distutils.pypi_exceptions import pypi_exceptions
from sysdevel.distutils import options
from sysdevel.util import is_string


## All these classes are abstract
# pylint: disable=W0223

class config(object):
    def __init__(self, dependencies=None, debug=False, force=False):
        if dependencies is None:
            self.dependencies = []
        else:
            self.dependencies = dependencies
        self.debug = debug
        self.environment = read_cache()
        self.found = False
        self.force = force

    def null(self):
        pass

    def download(self, environ, version, strict=False):
        # pylint: disable=W0613
        return ''

    def is_installed(self, environ, version, strict=False):
        raise NotImplementedError('is_installed')

    def install(self, environ, version, strict=False, locally=True):
        raise NotImplementedError('install')



class lib_config(config):
    def __init__(self, lib, header, dependencies=None,
                 debug=False, force=False):
        config.__init__(self, dependencies, debug, force)
        self.lib = lib
        self.hdr = header


    def null(self):
        self.environment[self.lib.upper() + '_INCLUDE_DIR'] = ''
        self.environment[self.lib.upper() + '_LIB_DIR'] = ''
        self.environment[self.lib.upper() + '_DEF_FILES'] = []
        self.environment[self.lib.upper() + '_SHLIB_DIR'] = ''
        self.environment[self.lib.upper() + '_LIB_FILES'] = []
        self.environment[self.lib.upper() + '_LIBRARIES'] = []


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        default_lib_paths = ['lib64', 'lib', '']
        default_include_paths = ['include', os.path.join(self.lib, 'include')]

        locations = [os.path.join(options.target_build_dir, d)
                     for d in default_include_paths + default_lib_paths]
        limit = False
        if self.lib.upper() + '_SHLIB_DIR' in environ and \
                environ[self.lib.upper() + '_SHLIB_DIR']:
            locations.append(environ[self.lib.upper() + '_SHLIB_DIR'])
        if self.lib.upper() + '_LIB_DIR' in environ and \
                environ[self.lib.upper() + '_LIB_DIR']:
            locations.append(environ[self.lib.upper() + '_LIB_DIR'])
            if self.lib.upper() + '_INCLUDE_DIR' in environ and \
                    environ[self.lib.upper() + '_INCLUDE_DIR']:
                locations.append(environ[self.lib.upper() + '_INCLUDE_DIR'])
                limit = True

        if not limit:
            try:
                locations += os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
                locations += os.environ['LIBRARY_PATH'].split(os.pathsep)
                locations += os.environ['CPATH'].split(os.pathsep)
            except KeyError:
                pass
            try:
                locations.append(os.environ[self.lib.upper() + '_ROOT'])
            except KeyError:
                pass
            try:
                locations.append(os.environ[self.lib.upper() + '_LIBRARY_DIR'])
            except KeyError:
                pass
            for d in programfiles_directories():
                locations.append(os.path.join(d, 'GnuWin32'))
                locations += glob_insensitive(d, self.lib + '*')
            try:
                locations.append(environ['MINGW_DIR'])
                locations.append(environ['MSYS_DIR'])
            except KeyError:
                pass
        try:
            if self.hdr:
                incl_dir = find_header(self.hdr, locations, limit=limit)
                default_lib_paths = ['lib64', 'lib', '']
                for lib in default_lib_paths:
                    locations.insert(0,
                                     os.path.abspath(os.path.join(incl_dir,
                                                                  '..', lib)))
            lib_dir, lib = find_library(self.lib, locations, limit=limit)
            def_dir, defs = lib_dir, []
            if 'windows' in platform.system().lower():
                def_dir, defs = find_definitions(self.lib, locations,
                                                 limit=limit)
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        if self.hdr:
            self.environment[self.lib.upper() + '_INCLUDE_DIR'] = incl_dir
        self.environment[self.lib.upper() + '_LIB_DIR'] = def_dir
        self.environment[self.lib.upper() + '_DEF_FILES'] = defs
        self.environment[self.lib.upper() + '_SHLIB_DIR'] = lib_dir
        self.environment[self.lib.upper() + '_LIB_FILES'] = [lib]
        self.environment[self.lib.upper() + '_LIBRARIES'] = [self.lib]
        return self.found


    def install(self, environ, version, strict=False, locally=True):
        raise NotImplementedError('lib' + self.lib + ' installation')



class file_config(config):
    def __init__(self, filename, dnld_dir, website,
                 dependencies=None, debug=False, force=False):
        config.__init__(self, dependencies, debug, force)
        self.target_dir = dnld_dir
        self.website = website
        self.source = filename
        self.targets = [filename]  ## list of filenames or (subdir, file) tuples


    def download(self, environ, version, strict=False):
        if not version is None:
            self.website = self.website + '/' + version + '/'
        for t in self.targets:
            if is_string(t):
                fetch(self.website, t, t)
            else:
                fetch(self.website + '/' + t[0], t[1], t[1])
        return ''


    def is_installed(self, environ, version=None, strict=False):
        for item in self.targets:
            if is_string(item):
                if not os.path.exists(os.path.join(self.target_dir, item)):
                    return False
            else:
                if not os.path.exists(os.path.join(self.target_dir,
                                                   item[0], item[1])):
                    return False
        return True


    def install(self, environ, version, strict=False, locally=True):
        self.download(environ, version, strict)
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)
        for t in self.targets:
            if is_string(t):
                shutil.copy(os.path.join(options.download_dir, t),
                            self.target_dir)
            else:
                js_subdir = os.path.join(self.target_dir, t[0])
                js_file = t[1]
                if not os.path.exists(js_subdir):
                    os.makedirs(js_subdir)
                shutil.copy(os.path.join(options.download_dir, js_file),
                            js_subdir)



class prog_config(config):
    def __init__(self, exe, dependencies=None, debug=False, force=False):
        config.__init__(self, dependencies, debug, force)
        self.exe = exe


    def null(self):
        self.environment[self.exe.upper()] = None


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        limit = False
        locations = []
        if self.exe.upper() in environ and environ[self.exe.upper()]:
            locations.append(os.path.dirname(environ[self.exe.upper()]))
            limit = True

        if not limit:
            try:
                locations.append(os.environ[self.exe.upper() + '_ROOT'])
            except KeyError:
                pass
            try:
                locations.append(environ['MINGW_DIR'])
                locations.append(environ['MSYS_DIR'])
            except KeyError:
                pass

        try:
            program = find_program(self.exe, locations, limit=limit)
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        self.environment[self.exe.upper()] = program
        return self.found


    def install(self, environ, version, strict=False, locally=True):
        raise NotImplementedError(self.exe + ' installation')



class nodejs_config(config):
    def __init__(self, module, dependencies=None, debug=False, force=False):
        if dependencies is None:
            dependencies = ['node',]
        elif not 'node' in dependencies:
            dependencies.append('node')
        config.__init__(self, dependencies, debug, force)
        self.module = module


    def is_installed(self, environ, version=None, strict=False):
        cmd_line = [environ['NPM'], 'list', self.module.lower()]
        return self.__check_installed(cmd_line) or \
            self.__check_installed(cmd_line + ['-g'])


    def __check_installed(self, cmd_line):
        p = subprocess.Popen(cmd_line,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, _ = p.communicate()
        if '(empty)' in out:
            return False
        return True


    def install(self, environ, version, strict=False, locally=True):
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
                status = process_progress(p)
            except KeyboardInterrupt:
                p.terminate()
                log.close()
                raise
            if status != 0:
                log.close()
                sys.stdout.write(' failed; See ' + log_file)
                raise ConfigError(self.module,
                                  'NPM update is required, but could not be ' +
                                  'installed; See ' + log_file)

            cmd_line = pre + [environ['NPM'], 'install', 'node-webgl'] + post
            try:
                p = subprocess.Popen(cmd_line, stdout=log, stderr=log)
                status = process_progress(p)
            except KeyboardInterrupt:
                p.terminate()
                log.close()
                raise
            if status != 0:
                log.close()
                if log_file:
                    sys.stdout.write(' failed; See ' + log_file)
                    raise ConfigError(self.module,
                                      'Node-' + self.module + ' is required, ' +
                                      'but could not be installed; See ' + log_file)
                else:
                    sys.stdout.write(' failed')
                    raise ConfigError(self.module,
                                      'Node-' + self.module + ' is required, ' +
                                      'but could not be installed.')



class py_config(config):
    def __init__(self, pkg, version, dependencies=None, indexed_as=None,
                 debug=False, force=False):
        config.__init__(self, dependencies, debug, force)
        self.pkg = pkg.lower()
        self.version = version
        self.indexed = pkg
        if indexed_as:
            self.indexed = indexed_as
        self.did_install = False


    def check_version(self, module, version, strict):
        do_check = False
        if hasattr(module, '__version__'):
            ver = module.__version__
            do_check = True
        elif hasattr(module, 'VERSION'):
            ver = module.VERSION
            do_check = True
        elif hasattr(module, 'version'):
            if isinstance(module.version, ModuleType):
                return self.check_version(module.version, version, strict)
            elif type(module.version) == type(''):
                ver = module.version
                do_check = True
        if do_check:
            not_ok = (compare_versions(ver, version) == -1)
            if strict:
                not_ok = (compare_versions(ver, version) != 0)
            if not_ok:
                self.found = False
                if self.debug:
                    sys.stderr.write('Wrong version of ' + self.pkg + ': ' +
                                     str(ver) + ' vs ' + str(version) + '  ')
                return False
        return True


    def is_installed(self, environ, version=None, strict=False):
        local_dirs = [os.path.join(os.path.abspath(options.target_build_dir),
                                   options.local_lib_dir)]
        ## pkgutil methods don't work immediately after an install
        for d in local_dirs + [get_python_lib()] + sys.path:
            if os.path.exists(os.path.join(d, self.pkg + '.py')) or \
               os.path.exists(os.path.join(d, self.pkg, '__init__.py')):
                self.found = True
                break
        if self.did_install:  ## assume correct version was just installed
            return self.found
        if self.found and not version is None:
            try:
                for d in local_dirs:
                    if not d in sys.path:
                        sys.path.insert(0, d)
                if self.pkg in sys.modules.keys():
                    impl = reload(sys.modules[self.pkg])
                else:
                    impl = __import__(self.pkg)
                self.found = self.check_version(impl, version, strict)
            except ImportError:
                self.found = False
                if self.debug:
                    print(sys.exc_info()[1])
        return self.found


    def download(self, environ, version, strict=False):
        website = pypi_url(self.indexed)
        if version is None:
            version = self.version
        src_dir = self.indexed + '-' + str(version)
        archive = src_dir + '.tar.gz'
        try:
            fetch(website, archive, archive)
            unarchive(archive, src_dir)
            return src_dir
        except (DownloadError, URLError, HTTPError, ContentTooShortError):
            try:
                archive = src_dir + '.zip'
                fetch(website, archive, archive)
                unarchive(archive, src_dir)
                return src_dir
            except (DownloadError, URLError, HTTPError, ContentTooShortError):
                try:
                    archive = src_dir + '.tar.bz2'
                    fetch(website, archive, archive)
                    unarchive(archive, src_dir)
                    return src_dir
                except (DownloadError, URLError, HTTPError, ContentTooShortError):
                    try:
                        archive = src_dir + '.tgz'
                        fetch(website, archive, archive)
                        unarchive(archive, src_dir)
                        return src_dir
                    except (DownloadError, URLError, HTTPError, ContentTooShortError):
                        try:
                            archive = src_dir + '.tar.Z'
                            fetch(website, archive, archive)
                            unarchive(archive, src_dir)
                            return src_dir
                        except (DownloadError, URLError, HTTPError, ContentTooShortError):
                            archive = src_dir + '.tar'
                            fetch(website, archive, archive)
                            unarchive(archive, src_dir)
                            return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            src_dir = self.download(environ, version, strict)
            install_pypkg_without_fetch(self.pkg, None, src_dir, locally)
            self.did_install = True
            if not self.is_installed(environ, version, strict):
                raise ConfigError(self.pkg, 'Installation failed.')



class pypi_config(py_config):
    def __init__(self, pkg, version, dependencies=None, indexed_as=None,
                 debug=False, force=False):
        name = pkg
        if indexed_as:
            name = indexed_as
        if dependencies is None:
            if version is None:
                version = latest_pypi_version(name)
            archive = name + '-' + version + pypi_archive(name, version)
            fetch(pypi_url(name), archive, archive)
            z, names = open_archive(archive)
            try:
                extract_dir = os.path.join(options.target_build_dir, '.' + pkg)
                member = [s for s in names if 'setup.py' in s][0]
                z.extract(member, extract_dir)
                rf = RequirementsFinder(os.path.join(extract_dir, member))
                dependencies = rf.requires_list
            except Exception:  # pylint: disable=W0703
                if debug:
                    traceback.print_exc()
            z.close()
        py_config.__init__(self, pkg, version, dependencies, name,
                           debug, force)


    def download(self, environ, version, strict=False):
        if not strict:
            version = latest_pypi_version(self.indexed, version)
        return py_config.download(self, environ, version, strict)


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if not strict:
                version = latest_pypi_version(self.indexed, version)
            py_config.install(self, environ, version, strict, locally)




def dynamic_module(pkg, version=None, strict=False, dependencies=None,
                   indexed_as=None, debug=False, force=False):
    module = imp.new_module(pkg + '_pypi')
    code = "from " + __package__ + ".configuration import pypi_config\n" + \
           "class configuration(pypi_config):\n" + \
           "    def __init__(self):\n" + \
           "        pypi_config.__init__(self, " + repr(pkg) + ", " + \
           repr(version) + ", " + repr(dependencies) + ", " + \
           repr(indexed_as) + ", " + repr(debug) + ", " + \
           repr(force) + ")\n" + \
           "\n" + \
           "    def is_installed(self, environ, " + \
           "version=None, strict=False):\n" + \
           "        return pypi_config.is_installed(self, environ, " + \
           repr(version) + ", " + repr(strict) + ")\n" + \
           "\n" + \
           "    def install(self, environ, version, " + \
           "strict=False, locally=True):\n" + \
           "        pypi_config.install(self, environ, " + \
           repr(version) + ", " + repr(strict) + ", locally)\n\n"
    exec code in module.__dict__  # pylint: disable=W0122
    return module


def is_pypi_listed(pkg):
    if not os.path.exists(options.target_build_dir):
        mkdir(options.target_build_dir)
    listing = os.path.join(options.target_build_dir, '.' + pkg + '_list_test')
    try:
        urlretrieve(pypi_url(pkg, False), listing)
        return True
    except (DownloadError, URLError, HTTPError, ContentTooShortError):
        return False


def pypi_url(pkg, src=True):
    if src:
        ## This ensures that there are sources available:
        return 'https://pypi.python.org/packages/source/' + \
            pkg[0] + '/' + pkg + '/'
    else:
        ## This is what pip uses:
        return 'http://pypi.python.org/simple/' + pkg + '/'


def pypi_archive(which, version):
    archive_types = ['.zip', '.tar.bz2', '.tar.gz', '.tgz', '.tar.Z', '.tar']
    if version is None or \
       not version in available_versions(which, pypi_url(which),
                                         which + '-*', True):
        print('Warning: version ' + str(version) + ' of ' + which +
              ' is not available.')
        version = earliest_pypi_version(which)
    try:
        if not os.path.exists(options.target_build_dir):
            mkdir(options.target_build_dir)
        listing = os.path.join(options.target_build_dir, '.' + which + '_list')
        if not os.path.exists(listing):
            urlretrieve(pypi_url(which), listing)
        f = open(listing, 'r')
        contents = f.read()
        f.close()
        l = len(which + '-' + version)
        idx = contents.find(which + '-' + version)
        for archive in archive_types:
            if contents[idx+l:].startswith(archive):
                return archive
    except (DownloadError, URLError, HTTPError, ContentTooShortError):
        ## Default to whatever is in the third_party directory
        file_list = glob.glob(os.path.join(options.download_dir, which + '*'))
        for f in file_list:
            for archive in archive_types:
                if archive in f:
                    return archive
    raise ConfigError(which, 'No source archive available')


def available_versions(what, website, pattern, archives=False):
    archive_types = ['.zip', '.tar.bz2', '.tar.gz', '.tgz', '.tar.Z', '.tar']
    pre = pattern.split('*')[0]
    post = pattern.split('*')[-1]
    try:
        listing = os.path.join(options.target_build_dir, '.' + what + '_list')
        urlretrieve(website + '/', listing)
        versions = []
        f = open(listing, 'r')
        contents = f.read()
        f.close()
        idx = contents.find(pre, 0)
        l = len(pre)
        while idx >= 0:
            endl = contents.find('\n', idx)
            end = contents.find(post, idx)
            if archives:
                end_t = contents.find('.tar', idx, endl)
                end_z = contents.find('.zip', idx, endl)
                if end_t > 0 and end_z > 0:
                    end = min(end_t, end_z)
                else:
                    end = max(end_t, end_z)
            if end > 0 and end < endl:
                versions.append(contents[idx+l:end])
            idx = contents.find(pre, end)
        return versions
    except (DownloadError, URLError, HTTPError, ContentTooShortError):
        ## Default to whatever is in the third_party directory
        file_list = glob.glob(os.path.join(options.download_dir, pattern))
        if len(file_list) > 0:
            pre = os.path.join(options.download_dir, pre)
            version_list = []
            for f in file_list:
                for archive in archive_types:
                    if archive in f:
                        version_list.append(f[len(pre):-(len(post) +
                                                         len(archive))])
                        break
            return version_list
        else:
            raise



def latest_version(what, website, pattern,
                   requested='0', archives=False):
    version = requested
    versions = available_versions(what, website, pattern, archives)
    for ver in versions:
        if compare_versions(version, ver) < 0:
            version = ver
    if requested in versions:
        return requested
    return version


def earliest_version(what, website, pattern,
                     requested='9999999999', archives=False):
    version = requested
    versions = available_versions(what, website, pattern, archives)
    for ver in versions:
        if compare_versions(version, ver) > 0:
            version = ver
    if requested in versions:
        return requested
    return version


def latest_pypi_version(what, requested_ver=None):
    return latest_version(what, pypi_url(what),
                          what + '-*', requested_ver, True)


def earliest_pypi_version(what, requested_ver=None):
    return earliest_version(what, pypi_url(what),
                            what + '-*', requested_ver, True)



DEBUG_PYPI = True
DEBUG_LOCAL = False


def find_package_config(help_name, helper_funct, *args, **kwargs):
    setup_directory = kwargs.get('setup_dir', os.getcwd())

    help_name, req_version, strict = requirement_versioning(help_name)
    if help_name is None:
        return None

    base = help_name = help_name.strip()
    packages = ['sysdevel.distutils.configure.', '',]
    cfg_dir = os.path.abspath(os.path.join(setup_directory,
                                           options.user_config_dir))
    if os.path.exists(cfg_dir) and not cfg_dir in sys.path:
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
                helper = dynamic_module(base, req_version, strict, deps,
                                        name, DEBUG_PYPI)
            else:
                helper = dynamic_module(base, req_version, strict,
                                        debug=DEBUG_PYPI)
        except Exception:
            if DEBUG_PYPI:
                traceback.print_exc()
            raise ImportError('No configuration found for ' + help_name)
    local_python_dir = os.path.join(options.target_build_dir,
                                    options.local_lib_dir)
    if not local_python_dir in sys.path:
        sys.path.insert(0, local_python_dir)
    return helper_funct(help_name, helper, req_version, strict,
                        *args, **kwargs)
