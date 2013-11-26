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
import imp
import traceback

from .prerequisites import *
from .filesystem import glob_insensitive
from .fetching import urlretrieve, fetch, open_archive
from .building import process_progress
from . import options


#TODO: what does pip do for these?
pypi_exceptions = {
    'argparse':          ('argparse', []),  ## because it breaks the AST FIXME?
    'dateutil':          ('python-dateutil', ['six']),
    'ephem':             ('pyephem', None),
    'fuzzy':             ('Fuzzy', None),
    'jinja2':            ('Jinja2', None),
    'pygments':          ('Pygments', None),
    'pyyaml':            ('PyYAML', ['libyaml']),
    'qunitsuite':        ('QUnitSuite', None),
    'scipy':             ('scipy', ['gfortran',]), #'atlas'], #'lapack'?]),
    'serial':            ('pyserial', None),
    'shapely':           ('Shapely', ['geos']),
    'sphinx':            ('Sphinx', ['docutils', 'jinja2', 'pygments',
                                     'roman',]), # 'rst2pdf']), #FIXME
    'sqlalchemy':        ('SQLAlchemy', None),
    'usb':               ('pyusb', ['libusb']),
}



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
        self.environment[self.lib.upper() + '_INCLUDE_DIR'] = ''
        self.environment[self.lib.upper() + '_LIB_DIR'] = ''
        self.environment[self.lib.upper() + '_DEF_FILES'] = []
        self.environment[self.lib.upper() + '_SHLIB_DIR'] = ''
        self.environment[self.lib.upper() + '_LIB_FILES'] = []
        self.environment[self.lib.upper() + '_LIBRARIES'] = []


    def is_installed(self, environ, version=None):
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
        except Exception:
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


    def install(self, environ, version, locally=True):
        raise NotImplementedError('lib' + self.lib + ' installation')



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
                status = process_progress(p)
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
                status = process_progress(p)
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



class py_config(config):
    def __init__(self, pkg, version, dependencies=[], debug=False,
                 indexed_as=None):
        config.__init__(self, dependencies, debug)
        self.pkg = pkg
        self.version = version
        self.indexed = pkg
        if indexed_as:
            self.indexed = indexed_as


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
            elif hasattr(impl, 'VERSION'):
                ver = impl.VERSION
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
                self.indexed[0] + '/' + self.indexed + '/'
            if version is None:
                version = self.version
            src_dir = self.indexed + '-' + str(version)
            archive = src_dir + '.tar.gz'
            try:
                fetch(website, archive, archive, quiet=True)
            except Exception:
                try:
                    archive = src_dir + '.zip'
                    fetch(website, archive, archive, quiet=True)
                except Exception:
                    try:
                        archive = src_dir + '.tar.bz2'
                        fetch(website, archive, archive, quiet=True)
                    except Exception:
                        try:
                            archive = src_dir + '.tgz'
                            fetch(website, archive, archive, quiet=True)
                        except Exception:
                            try:
                                archive = src_dir + '.tar.Z'
                                fetch(website, archive, archive, quiet=True)
                            except Exception:
                                    archive = src_dir + '.tar'
                                    fetch(website, archive, archive)
            install_pypkg(src_dir, website, archive, locally=locally)
            ## Urgent FIXME install check is not always working
            #if not self.is_installed(environ, version):
            #    raise Exception(self.pkg + ' installation failed.')



class pypi_config(py_config):
    def __init__(self, pkg, version, dependencies=None, debug=False,
                 indexed_as=None):
        name = pkg
        if indexed_as:
            name = indexed_as
        if dependencies is None:
            if version is None:
                version = latest_pypi_version(name)
            try:
                archive = name + '-' + version + pypi_archive(name, version)
                fetch(pypi_url(name), archive, archive)
            except:
                raise Exception('Cannot download source for ' + pkg)
            z, names = open_archive(archive)
            try:
                extract_dir = os.path.join(options.target_build_dir, '.' + pkg)
                member = [s for s in names if 'setup.py' in s][0]
                z.extract(member, extract_dir)
                rf = RequirementsFinder(os.path.join(extract_dir, member))
                dependencies = rf.requires_list
            except:
                if debug:
                    traceback.print_exc()
            z.close()
        py_config.__init__(self, pkg, version, dependencies, debug, indexed_as)


    def install(self, environ, version, locally=True):
        if not self.found:
            py_config.install(self, environ,
                              latest_pypi_version(self.indexed, version),
                              locally)




def dynamic_module(pkg, version=None, dependencies=None, debug=False,
                   indexed_as=None):
    module = imp.new_module(pkg + '_pypi')
    code = "from " + __package__ + ".configuration import pypi_config\n" + \
           "class configuration(pypi_config):\n" + \
           "    def __init__(self):\n" + \
           "        pypi_config.__init__(self, " + repr(pkg) + ", " + \
           repr(version) + ", " + repr(dependencies) + ", " + \
           repr(debug) + ", " + repr(indexed_as) + ")\n"
    exec code in module.__dict__
    return module


def is_pypi_listed(pkg):
    listing = os.path.join(options.target_build_dir, '.' + pkg + '_list_test')
    try:
        urlretrieve(pypi_url(pkg, False), listing, quiet=True)
        return True
    except:
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
    listing = os.path.join(options.target_build_dir, '.' + which + '_list')
    if not os.path.exists(listing):
        urlretrieve(pypi_url(which), listing)
    f = open(listing, 'r')
    contents = f.read()
    f.close()
    l = len(which + '-' + version)
    idx = contents.find(which + '-' + version)
    for archive in ['.zip', '.tar.bz2', '.tar.gz', '.tgz', '.tar.Z', '.tar']:
        if contents[idx+l:].startswith(archive):
            return archive
    raise Exception('No source archive available for ' + which)


def latest_pypi_version(which, requested_ver=None):
    listing = os.path.join(options.target_build_dir, '.' + which + '_list')
    urlretrieve(pypi_url(which), listing)
    version = '0'
    versions = []
    f = open(listing, 'r')
    contents = f.read()
    f.close()
    idx = contents.find(which + '-', 0)
    l = len(which + '-')
    while idx >= 0:
        endl = contents.find('\n', idx)
        end_t = contents.find('.tar', idx, endl)
        end_z = contents.find('.zip', idx, endl)
        if end_t > 0 and end_z > 0:
            end = min(end_t, end_z)
        else:
            end = max(end_t, end_z)
        if end > 0:
            versions.append(contents[idx+l:end])
        idx = contents.find(which + '-', end)
    if requested_ver in versions:
        return requested_ver
    for ver in versions:
        if compare_versions(version, ver) < 0:
            version = ver
    return version


def latest_version(what, website, pattern):
    pre = pattern.split('*')[0]
    post = pattern.split('*')[-1]
    listing = os.path.join(options.target_build_dir, '.' + what + '_list')
    urlretrieve(website + '/', listing)
    version = '0'
    versions = []
    f = open(listing, 'r')
    contents = f.read()
    f.close()
    idx = contents.find(pre, 0)
    l = len(pre)
    while idx >= 0:
        endl = contents.find('\n', idx)
        end = contents.find(post, idx)
        if end > 0 and end < endl:
            versions.append(contents[idx+l:end])
        idx = contents.find(pre, end)
    for ver in versions:
        if compare_versions(version, ver) < 0:
            version = ver
    return version


