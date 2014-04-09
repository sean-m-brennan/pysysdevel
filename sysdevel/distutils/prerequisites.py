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
Utilities for prerequisite library and build-tool installation
"""

import os
import sys
import platform
import subprocess
import fnmatch
import struct
import glob
import traceback
import ast
import re
import shutil
from distutils.sysconfig import get_python_lib

try:
    import json
except ImportError:
    import simplejson as json

from .filesystem import mkdir
from .building import process_progress
from .fetching import fetch, unarchive
from ..util import is_string
from . import options


class PrerequisiteError(Exception):
    pass


class ConfigError(Exception):
    def __init__(self, which, what):
        Exception.__init__(self)
        self.which = which
        self.what = what

    def __str__(self):
        return "Error finding '" + self.which + "': " + self.what



def requirement_versioning(name):
    version = None
    strict = False
    if not is_string(name) and len(name) > 1:
        if len(name) > 2:
            strict = name[2]
        version = name[1]
        name = name[0]
    elif '=' in name:
        n_end = name.find('(')
        if n_end < 0:
            n_end = name.find('>')
            if n_end < 0:
                n_end = name.find('=')
        v_begin = name.rfind('=') + 1
        v_end = name.find(')')
        if '==' in name[n_end:]:
            strict = True
        version = name[v_begin:v_end].strip()
        name = name[:n_end].strip()
    if name == 'None':
        name = None
    return name, version, strict



class RequirementsFinder(ast.NodeVisitor):
    req_keywords = ['requires', #'install_requires',
                    ]
    cfg_keyword = 'configure_system'

    def __init__(self, filepath=None, filedescriptor=None, codestring=None):
        ast.NodeVisitor.__init__(self)
        self.variables = {}
        self.is_sysdevel_build = False
        self.is_sysdevel_itself = False
        self.needs_early_config = False
        self.requires_list = []
        if filepath:
            if len(glob.glob(os.path.join(os.path.dirname(filepath),
                                          'sysdevel*'))) > 0:
                self.is_sysdevel_itself = True
            self._load_from_path(filepath)
        elif filedescriptor:
            if hasattr(filedescriptor, 'name') and \
               len(glob.glob(os.path.join(os.path.dirname(filedescriptor.name),
                                          'sysdevel*'))) > 0:
                self.is_sysdevel_itself = True
            self._load_from_file(filedescriptor)
        elif codestring:
            self._load_from_string(codestring)


    def _load_from_string(self, code):
        tree = ast.parse(code)
        self.visit(tree)
        required = list(self.requires_list)
        self.requires_list = []
        for r in required:
            self.requires_list.append(requirement_versioning(r))


    def _load_from_file(self, f):
        code = f.read()
        self._load_from_string(code)


    def _load_from_path(self, p):
        source = open(p, 'r')
        self._load_from_file(source)
        source.close()


    def visit_Assign(self, node):
        for target in node.targets:
            if type(target) == ast.Name:
                self.variables[str(target.id)] = node.value
            if type(target) == ast.Tuple:
                for idx in range(len(target.elts)):
                    if type(target.elts[idx]) == ast.Name:
                        if type(node.value) == ast.Tuple:
                            self.variables[
                                str(target.elts[idx].id)] = node.value.elts[idx]
                        #elif type(node.value) == ast.Call:
                        #   TODO evaluate ast.Call for assignment operator
            if type(node.value) == ast.Call:
                if type(node.value.func) == ast.Name:
                    if node.value.func.id == self.cfg_keyword:
                        self.needs_early_config = True


    def visit_keyword(self, node):
        for kw in self.req_keywords:
            if node.arg == kw:
                if type(node.value) == ast.List:
                    self.requires_list = ast.literal_eval(node.value)
                elif type(node.value) == ast.Name:
                    self.requires_list = ast.literal_eval(
                        self.variables[node.value.id])  ## fails on ast.Call
        

    def visit_Import(self, node):
        for name in node.names:
            if name.name.startswith('sysdevel') and not self.is_sysdevel_itself:
                self.is_sysdevel_build = True

    def visit_ImportFrom(self, node):
        if node.module.startswith('sysdevel') and not self.is_sysdevel_itself:
            self.is_sysdevel_build = True

    def generic_visit(self, node):
        ast.NodeVisitor.generic_visit(self, node)



## Caching ###################

def read_cache():
    environ = dict()
    cache_file = os.path.join(options.target_build_dir, '.cache')
    if os.path.exists(cache_file):
        try:
            cache = open(cache_file, 'rb')
            cached = json.load(cache)
            options.set_local_search_paths(cached['local_search_paths'])
            environ = cached['environment']
            cache.close()
            if len(options.local_search_paths) == 0:
                options.set_local_search_paths(
                    [os.path.abspath(options.target_build_dir)])
        except Exception:  # pylint: disable=W0703
            pass
    return environ

def save_cache(environ):
    cache_file = os.path.join(options.target_build_dir, '.cache')
    if not os.path.isdir(options.target_build_dir):
        if os.path.exists(options.target_build_dir):
            os.remove(options.target_build_dir)
        mkdir(options.target_build_dir)
    cache = open(cache_file, 'wb')
    cached = dict()
    cached['local_search_paths'] = options.local_search_paths
    cached['environment'] = environ
    json.dump(cached, cache)
    cache.close()

def delete_cache():
    cache = os.path.join(options.target_build_dir, '.cache')
    if os.path.exists(cache):
        os.remove(cache)

##############################


def find_program(name, pathlist=None, limit=False):
    '''
    Find the path of an executable.
    '''
    if pathlist is None:
        pathlist = []
    try:
        path_env = os.environ['PATH'].split(os.pathsep)
    except KeyError:
        path_env = []
    if not limit:
        pathlist += path_env + options.local_search_paths
    for path in pathlist:
        if path != None and (os.path.exists(path) or glob.glob(path)):
            for p in [path, os.path.join(path, 'bin')]:
                if options.DEBUG:
                    print('Searching ' + p + ' for ' + name)
                full = os.path.join(p, name)
                if os.path.lexists(full):
                    if options.DEBUG:
                        print('Found ' + full)
                    return full
                if os.path.lexists(full + '.exe'):
                    if options.DEBUG:
                        print('Found ' + full + '.exe')
                    return full + '.exe'
                if os.path.lexists(full + '.bat'):
                    if options.DEBUG:
                        print('Found ' + full + '.bat')
                    return full + '.bat'
                if os.path.lexists(full + '.cmd'):
                    if options.DEBUG:
                        print('Found ' + full + '.cmd')
                    return full + '.bat'
    raise ConfigError(name, 'Program not found.')



def find_header(filepath, extra_paths=None, extra_subdirs=None, limit=False):
    '''
    Find the containing directory of the specified header file.
    extra_subdir may be a pattern. For Windows, it is important to not
    have a trailing path separator.
    '''
    if extra_paths is None:
        extra_paths = []
    if extra_subdirs is None:
        extra_subdirs = []
    subdirs = ['include',]
    for sub in extra_subdirs:
        subdirs += [os.path.join('include', sub), sub]
    subdirs += ['']  ## lastly, widen search
    pathlist = []
    for path_expr in extra_paths:
        pathlist += glob.glob(path_expr)
    if not limit:
        pathlist += options.default_path_prefixes + options.local_search_paths
    filename = filepath
    for path in pathlist:
        if path != None and os.path.exists(path):
            for sub in subdirs:
                ext_paths = glob.glob(os.path.join(path, sub))
                for ext_path in ext_paths:
                    if options.DEBUG:
                        print('Searching ' + ext_path + ' for ' + filepath)
                    filename = os.path.basename(filepath)
                    dirname = os.path.dirname(filepath)
                    for root, _, filenames in os.walk(ext_path):
                        rt = os.path.normpath(root)
                        for fn in filenames:
                            if dirname == '' and fnmatch.fnmatch(fn, filename):
                                if options.DEBUG:
                                    print('Found ' + os.path.join(root, filename))
                                return root.rstrip(os.sep)
                            elif fnmatch.fnmatch(os.path.basename(rt), dirname) \
                                    and fnmatch.fnmatch(fn, filename):
                                if options.DEBUG:
                                    print('Found ' + os.path.join(rt, filename))
                                return os.path.dirname(rt).rstrip(os.sep)
    raise ConfigError(filename, 'Header not found.')


def find_definitions(name, extra_paths=None, extra_subdirs=None,
                     limit=False, single=False, wildcard=True):
    '''
    Find the containing directory and definitions filenames of
    the given library. Windows only.
    '''
    if extra_paths is None:
        extra_paths = []
    if extra_subdirs is None:
        extra_subdirs = []
    def_suffixes = ['.dll.a', '.lib']
    prefixes = ['', 'lib']
    subdirs = []
    for sub in extra_subdirs:
        subdirs += [sub]
    subdirs += ['']  ## lastly, widen search
    pathlist = []
    for path_expr in extra_paths:
        pathlist += glob.glob(path_expr)
    if not limit:
        pathlist += options.default_path_prefixes + options.local_search_paths
    for path in pathlist:
        if path != None and os.path.exists(path):
            for sub in subdirs:
                for root, _, filenames in \
                    os.walk(os.path.join(path, sub)):
                    for prefix in prefixes:
                        for def_suffix in def_suffixes:
                            if wildcard:
                                filename = prefix + name + '*' + def_suffix
                            else:
                                filename = prefix + name + def_suffix
                            if options.DEBUG:
                                print('Searching ' + root + ' for ' + filename)
                            defs = []
                            for fn in filenames:
                                if fnmatch.fnmatch(fn, filename):
                                    if single:
                                        if options.DEBUG:
                                            print('Found at ' + root)
                                        return root.rstrip(os.sep), [fn]
                                    else:
                                        defs.append(fn)
                            if len(defs) > 0:
                                if options.DEBUG:
                                    print('Found at ' + root)
                                return root.rstrip(os.sep), defs
    raise ConfigError(name, 'Library definitions not found.')


def find_library(name, extra_paths=None, extra_subdirs=None,
                 limit=False, wildcard=True):
    '''
    Find the containing directory and proper filename (returned as a tuple)
    of the given library.
    '''
    return find_libraries(name, extra_paths, extra_subdirs,
                          limit, True, wildcard=wildcard)


def find_libraries(name, extra_paths=None, extra_subdirs=None,
                   limit=False, single=False, wildcard=True):
    '''
    Find the containing directory and proper filenames (returned as a tuple)
    of the given library. For Windows, it is important to not have a
    trailing path separator.
    '''
    if extra_paths is None:
        extra_paths = []
    if extra_subdirs is None:
        extra_subdirs = []
    default_lib_paths = ['lib64', 'lib', '']
    suffixes = ['.so', '.a']
    prefixes = ['', 'lib']
    if 'windows' in platform.system().lower():
        suffixes = ['.dll', '.a']
        default_lib_paths.append('bin')
    if 'darwin' in platform.system().lower():
        suffixes += ['.dylib']
    subdirs = []
    for sub in extra_subdirs:
        subdirs += [sub]
    subdirs += ['']  ## lastly, widen search
    pathlist = []
    for path_expr in extra_paths:
        pathlist += glob.glob(path_expr)
    if not limit:
        pathlist += options.default_path_prefixes + options.local_search_paths
    for path in pathlist:
        if path != None and os.path.exists(path):
            for subpath in default_lib_paths:
                for sub in subdirs:
                    for root, _, filenames in \
                            os.walk(os.path.join(path, subpath, sub)):
                        for prefix in prefixes:
                            for suffix in suffixes:
                                if wildcard:
                                    filename = prefix + name + '*' + suffix
                                else:
                                    filename = prefix + name + suffix
                                if options.DEBUG:
                                    print('Searching ' + root + \
                                        ' for ' + filename)
                                libs = []
                                for fn in filenames:
                                    if fnmatch.fnmatch(fn, filename):
                                        if single:
                                            if options.DEBUG:
                                                print('Found at ' + root)
                                            return root.rstrip(os.sep), fn
                                        else:
                                            libs.append(fn)
                                if len(libs) > 0:
                                    if options.DEBUG:
                                        print('Found at ' + root)
                                    return root.rstrip(os.sep), libs
    raise ConfigError(name, 'Library not found.')


def libraries_from_components(components, path):
    libs = []
    for comp in components:
        if options.DEBUG:
            print('Searching ' + path + ' for ' + comp)
        _, lib = find_library(comp, [path])
        name = os.path.splitext(lib)[0]
        if name.startswith('lib'):
            name = name[3:]
        libs.append(name)
    return libs


def find_file(filepattern, pathlist=None):
    '''
    Find the full path of the specified file.
    '''
    if pathlist is None:
        pathlist = []
    suffix = ''
    if os.path.sep in filepattern:
        idx = filepattern.rfind(os.path.sep)
        suffix = filepattern[:idx]
        filepattern = filepattern[idx+1:]
    for path in options.local_search_paths + pathlist:
        if path != None and os.path.exists(path):
            if options.DEBUG:
                print('Searching ' + path + ' for ' + filepattern)
            for fn in os.listdir(os.path.join(path, suffix)):
                if fnmatch.fnmatch(fn, filepattern):
                    if options.DEBUG:
                        print('Found ' + os.path.join(path, fn))
                    return os.path.join(path, fn)
    raise ConfigError(filepattern, 'File not found.')



def version_str_split(v):
    pattern = re.compile(r'(\d+)[_\.]?(\d+)*[_\.]?(\d+)*[\-_\.]?(\S+)*')
    m = pattern.match(v)
    if m:
        strs = list(m.groups())
    else:
        strs = ['0', '0', '0', '']
    for i in range(3):
        if strs[i] is None:
            strs[i] = 0
        else:
            strs[i] = int(strs[i])
    if strs[3] is None:
        strs[3] = ''
    return tuple(strs)


def compare_versions(actual, requested):
    ## convert float to string
    if isinstance(actual, float):
        actual = str(actual)
    if isinstance(requested, float):
        requested = str(requested)
    # convert string to tuple
    if is_string(actual):
        ver1 = version_str_split(actual)
    else:
        ver1 = actual
    if is_string(requested):
        ver2 = version_str_split(requested)
    else:
        ver2 = requested
    ## special case
    if ver2 is None:
        if ver1 is None:
            return 0
        return 1  ## None == latest

    if ver1 < ver2:
        return -1
    if ver1 > ver2:
        return 1
    return 0



def patch_file(filepath, match, original, replacement):
    if os.path.exists(filepath):
        orig = open(filepath, 'r')
        lines = orig.readlines()
        orig.close()
        shutil.move(filepath, filepath + '.orig')
        fixed = open(filepath, 'w')
        for line in lines:
            if match in line:
                line = line.replace(original, replacement)
            fixed.write(line)



def get_python_version():
    return (str(sys.version_info[0]), str(sys.version_info[1]))


def major_minor_version(ver):
    sver = str(ver)
    tpl = sver.split('.')
    return '.'.join(tpl[:2])


def in_prerequisites(item, prereqs):
    for p in prereqs:
        if not is_string(p):
            if item == p[0]:
                return True
        elif item == p:
            return True
    return False


def programfiles_directories():
    if 'windows' in platform.system().lower():
        try:
            drive = os.path.splitdrive(os.environ['ProgramFiles'])[0]
        except KeyError:
            drive = 'c:'
        return [os.path.join(drive, os.sep, 'Program Files'),
                os.path.join(drive, os.sep, 'Program Files (x86)'),]
    return []


def convert2unixpath(win_path):
    import string
    if 'windows' in platform.system().lower():
        path = win_path.replace('\\', '/')
        for alpha in string.uppercase + string.lowercase:
            path = path.replace(alpha + ':', '/' + alpha)
        return path
    return win_path



def gcc_is_64bit():
    retval = False
    try:
        tempsrc = 'hello.c'
        tempobj = 'hello.o'
        t = open(tempsrc, 'w')
        t.write('#include <stdio.h>\n' +
                'int main() {\n' +
                '  printf("Hello\\n");\n' +
                '  return 0;\n' +
                '}\n')
        t.close()
        check_call(['gcc', '-o', tempobj, tempsrc])
        p = subprocess.Popen(['file', tempobj], stdout=subprocess.PIPE)
        if 'x86_64' in p.communicate()[0]:
            retval = True
    except OSError:
        pass
    os.unlink(tempsrc)
    try:
        os.unlink(tempobj)
    except OSError:
        pass
    return retval
        

def get_installed_base(loc):
    ver = 'python'+ '.'.join(get_python_version())
    if loc is None:
        loc = sys.prefix
    else:
        loc = os.path.normcase(loc)
    if 'windows' in platform.system().lower():
        base = os.path.join(loc, 'Lib', 'site-packages')
    else:
        base = os.path.join(loc, 'lib', ver, 'site-packages')
    return base


def get_pyd_suffix():
    import imp
    for s in imp.get_suffixes():
        if s[1] == 'rb' and s[0][0] == '.':
            return s[0]

def get_module_location(modname, preferred_dir=None):
    if preferred_dir is not None and os.path.exists(preferred_dir):
        if modname in os.listdir(preferred_dir):
            return os.path.join(preferred_dir, modname)
        elif modname + '.py' in os.listdir(preferred_dir):
            return os.path.join(preferred_dir, modname + '.py')
    __import__(modname)
    module = sys.modules[modname]
    d, f = os.path.split(module.__file__)
    if f.endswith('.pyc'):
        f = f[:-1]
    if f.startswith('__init__'):
        return d
    return os.path.join(d, f)


def get_os():
    os_name = platform.system().lower()
    if not 'windows' in os_name and \
            not 'darwin' in os_name:
        try:  ## RedHat
            rf = open('/etc/redhat-release', 'r')
            rel_line = rf.readline()
            rf.close()
            begin = rel_line.find('release') + 8
            end = rel_line[begin:].find('.') + begin
            os_name = 'rhel' + rel_line[begin:end]
        except Exception:  # pylint: disable=W0703
            os_name = platform.system().lower()
    return os_name




def install_pyscript(website, name, locally=True):
    if not os.path.exists(options.download_dir):
        os.makedirs(options.download_dir)
    if locally:
        target_dir = os.path.join(os.path.abspath(options.target_build_dir),
                                  options.local_lib_dir)
    else:
        target_dir = get_python_lib()
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    fetch(website, name, name)
    if options.VERBOSE:
        sys.stdout.write('PREREQUISITE ' + name + ' ')
    try:
        shutil.copy(os.path.join(options.download_dir, name), target_dir)
    except IOError:
        raise ConfigError(name, 'Unable to install: ' + str(sys.exc_info()[1]))


def install_pypkg_process(cmd_line, environ, log, shell):
    try:
        p = subprocess.Popen(cmd_line, env=environ, stdout=log, stderr=log,
                             shell=shell)
        status = process_progress(p)
        log.close()
    except KeyboardInterrupt:
        p.terminate()
        log.close()
        raise
    return status


def install_pypkg_without_fetch(name, env=None, src_dir=None, locally=True,
                                patch=None, extra_cmds=None, extra_args=None):
    compiler = []
    if 'windows' in platform.system().lower():
        # TODO compiler=mingw32 iff windows is using mingw (handle vcpp also?)
        compiler.append('--compiler=mingw32')
    if src_dir is None:
        src_dir = name
    if extra_cmds is None:
        extra_cmds = []
    if extra_args is None:
        extra_args = []
    here = os.path.abspath(os.getcwd())
    target_dir = os.path.abspath(options.target_build_dir)
    target_lib_dir = os.path.join(target_dir, options.local_lib_dir)

    if patch:
        patch(os.path.join(target_dir, src_dir))

    if options.VERBOSE:
        sys.stdout.write('PREREQUISITE ' + name + ' ')
    if not os.path.exists(target_lib_dir):
        os.makedirs(target_lib_dir)
    try:
        os.chdir(os.path.join(target_dir, src_dir))
        environ = os.environ.copy()
        shell = False
        if 'windows' in platform.system().lower():
            shell = True
        if env:
            for e in env:
                (key, value) = e.split('=')
                environ[key] = value
        environ['LDFLAGS'] = '-shared'
        if locally:
            environ['PYTHONPATH'] = target_lib_dir
            cmd_line = [sys.executable, 'setup.py'] + extra_cmds + \
                ['build'] + compiler + ['install_lib',
                 '--install-dir=' + target_lib_dir,] + extra_args
        else:
            sudo_prefix = []
            if not as_admin():
                sudo_prefix = ['sudo']
            cmd_line = sudo_prefix + [sys.executable, 'setup.py'] + \
                extra_cmds + ['build'] + compiler + ['install'] + extra_args
        log_file = os.path.join(target_dir, name + '.log')
        log = open(log_file, 'w')
        log.write(str(cmd_line) + '\n')
        if options.VERBOSE:
            log.write('Env: ' + str(environ) + '\n')
        log.write('\n')
        log.flush()
        status = install_pypkg_process(cmd_line, environ, log, shell)
        failed = False
        if status != 0:
            log = open(log_file, 'r')
            prefix_error = False
            err = "error: must supply either home or prefix/exec-prefix -- not both"
            for line in log:
                if err in line:
                    prefix_error = True
                break
            log.close()
            failed = True
            if prefix_error:
                log = open(log_file, 'a')
                log.write("\nRETRYING\n")
                log.flush()
                cmd_line.append("--prefix=")
                status = install_pypkg_process(cmd_line, environ, log, shell)
                if status == 0:
                    failed = False
        if failed:
            sys.stdout.write(' failed; See ' + log_file)
            raise ConfigError(name, 'Required, but could not be ' +
                              'installed; See ' + log_file)
        else:
            if options.VERBOSE:
                sys.stdout.write(' done\n')
        if locally:
            if not target_lib_dir in sys.path:
                sys.path.insert(0, target_lib_dir)
        os.chdir(here)
    except Exception:  # pylint: disable=W0703
        os.chdir(here)
        raise ConfigError(name, 'Unable to install:\n' +
                          str(sys.exc_info()[1]) + '\n' +
                          traceback.format_exc())

    if locally:
        return target_lib_dir
    try:
        __import__(name)
        module = sys.modules[name]
        return os.path.dirname(module.__file__)
    except ImportError:
        return get_python_lib()




def install_pypkg(name, website, archive, env=None, src_dir=None, locally=True,
                  patch=None, extra_cmds=None, extra_args=None):
    if src_dir is None:
        src_dir = name
    if extra_cmds is None:
        extra_cmds = []
    if extra_args is None:
        extra_args = []

    fetch(website, archive, archive)
    unarchive(archive, src_dir)

    return install_pypkg_without_fetch(name, env, src_dir, locally,
                                       patch, extra_cmds, extra_args)



def autotools_install_without_fetch(environ, src_dir, locally=True,
                                    extra_cfg=None, addtnl_env=None):
    if extra_cfg is None:
        extra_cfg = []
    if addtnl_env is None:
        addtnl_env = dict()
    here = os.path.abspath(os.getcwd())

    if locally:
        prefix = os.path.abspath(options.target_build_dir)
        if not prefix in options.local_search_paths:
            options.add_local_search_path(prefix)
    else:
        prefix = options.global_prefix
    prefix = convert2unixpath(prefix)  ## MinGW shell strips backslashes

    build_dir = os.path.join(options.target_build_dir,
                             src_dir)  ## build in-place
    mkdir(build_dir)
    os.chdir(build_dir)
    log = open('build.log', 'w')
    try:
        if 'windows' in platform.system().lower():
            ## Assumes MinGW present, detected, and loaded in environment
            mingw_check_call(environ, ['./configure',
                                       '--prefix="' + prefix + '"'] +
                             extra_cfg, stdout=log, stderr=log,
                             addtnl_env=addtnl_env)
            mingw_check_call(environ, ['make'], stdout=log, stderr=log,
                             addtnl_env=addtnl_env)
            try:
                mingw_check_call(environ, ['make', 'install'],
                                 stdout=log, stderr=log, addtnl_env=addtnl_env)
            except subprocess.CalledProcessError:
                pass
        else:
            os_environ = os.environ.copy()
            os_environ = dict(list(os_environ.items()) +
                              list(addtnl_env.items()))
            check_call(['./configure', '--prefix=' + prefix] + extra_cfg,
                       stdout=log, stderr=log, env=os_environ)
            check_call(['make'], stdout=log, stderr=log, env=os_environ)
            try:
                if locally:
                    check_call(['make', 'install'], stdout=log, stderr=log,
                               env=os_environ)
                else:
                    admin_check_call(['make', 'install'], stdout=log,
                                     stderr=log, addtnl_env=addtnl_env)
            except subprocess.CalledProcessError:
                pass
    finally:
        log.close()
        os.chdir(here)


def autotools_install(environ, website, archive, src_dir, locally=True,
                      extra_cfg=None, addtnl_env=None):
    fetch(''.join(website), archive, archive)
    unarchive(archive, src_dir)
    autotools_install_without_fetch(environ, locally, extra_cfg, addtnl_env)


def system_uses_apt_get():
    if 'linux' in platform.system().lower():
        try:
            find_program('apt-get')
            return os.path.exists('/etc/apt/sources.list')
        except Exception:  # pylint: disable=W0703
            pass
    return False

def system_uses_yum():
    if 'linux' in platform.system().lower():
        try:
            find_program('yum')
            return os.path.exists('/etc/yum.conf')
        except Exception:  # pylint: disable=W0703
            pass
    return False

def system_uses_homebrew():
    if 'darwin' in platform.system().lower():
        try:
            find_program('brew')
            return True
        except Exception:  # pylint: disable=W0703
            pass
    return False

def system_uses_macports():
    if 'darwin' in platform.system().lower():
        try:
            find_program('port')
            return os.path.exists(macports_prefix() + '/etc/macports/macports.conf')
        except Exception:  # pylint: disable=W0703
            pass
    return False


def get_msvc_version():
    py_version = get_python_version()
    py_32bit = platform.architecture()[0] == '32bit'
    name = ''
    ms_id = None
    version = ('',)
    if py_version < ('2', '4'):
        raise Exception('sysdevel only supports Python 2.4 and up')
    if py_32bit:
        if py_version <= ('2', '5'):
            name = '.NET Framework version 1.1 redistributable package'
            ms_id = '26'
            version = ('7', '1')
        else:
            name = 'Visual C++ 2008 redistributable package (x86)'
            ms_id = '29'
            version = ('9', '0')
    else:
        if py_version >= ('2', '6'):
            name = 'Visual C++ 2008 redistributable package (x64)'
            ms_id = '15336'
            version = ('9', '0')

    return version, ms_id, name


def macports_prefix():
    path = find_program('port')
    return os.path.dirname(os.path.dirname(path))


def homebrew_prefix():
    p = subprocess.Popen(['brew', '--prefix'],
                         stdout=subprocess.PIPE)
    return p.communicate()[0].strip()


def global_install(what, website_tpl, winstaller=None,
                   brew=None, port=None, deb=None, rpm=None):
    sys.stdout.write('INSTALLING ' + what + ' in the system\n')
    sys.stdout.flush()
    mkdir(options.target_build_dir)
    if website_tpl is None:
        website_tpl = ('','')
    log = open(os.path.join(options.target_build_dir, what + '.log'), 'w')
    if 'windows' in platform.system().lower() and winstaller:
        fetch(''.join(website_tpl), winstaller, winstaller)
        installer = os.path.join(options.download_dir, winstaller)
        try:
            admin_check_call(installer, stdout=log, stderr=log)
        except subprocess.CalledProcessError:
            ## some installers do not exit cleanly
            pass

    elif 'darwin' in platform.system().lower():
        if system_uses_homebrew() and brew:
            check_call(['brew', 'install',] + brew.split(),
                                  stdout=log, stderr=log)

        elif system_uses_macports() and port:
            admin_check_call(['port', 'install',] + port.split(),
                             stdout=log, stderr=log)
        else:
            log.close()
            raise PrerequisiteError('Unsupported OSX pkg manager. Install ' +
                                    what + ' by hand. See ' + website_tpl[0])

    elif 'linux' in platform.system().lower():
        if system_uses_apt_get() and deb:
            admin_check_call(['apt-get', 'install',] + deb.split(),
                             stdout=log, stderr=log)
        elif system_uses_yum() and rpm:
            admin_check_call(['yum', 'install',] + rpm.split(),
                             stdout=log, stderr=log)
        else:
            log.close()
            raise PrerequisiteError('Unsupported Linux flavor. Install ' +
                                    what + ' by hand. See ' + website_tpl[0])
    else:
        log.close()
        raise PrerequisiteError('Unsupported platform (' + platform.system() +
                                '). Install ' + what + ' by hand. See ' +
                                website_tpl[0])
    log.close()


def as_admin():
    import ctypes
    try:
        return os.geteuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def call(cmd_line, *args, **kwargs):
    return subprocess.call(cmd_line, *args, **kwargs)
    

def check_call(cmd_line, *args, **kwargs):
    status = subprocess.call(cmd_line, *args, **kwargs)
    if status != 0:
        raise subprocess.CalledProcessError(status, cmd_line)
    

def admin_check_call(cmd_line, quiet=False, stdout=None, stderr=None,
                     addtnl_env=None):
    if addtnl_env is None:
        addtnl_env = dict()
    if 'windows' in platform.system().lower():
        if not is_string(cmd_line):
            cmd_line = ' '.join(cmd_line)
        if not as_admin():
            # pylint: disable=F0401,W0612
            from win32com.shell.shell import ShellExecuteEx
            from win32event import WaitForSingleObject, INFINITE
            from win32process import GetExitCodeProcess
            handle = ShellExecuteEx(lpVerb='runas', lpFile=cmd_line)['hProcess']
            WaitForSingleObject(handle, INFINITE)
            status = GetExitCodeProcess(handle)
            if status != 0:
                raise subprocess.CalledProcessError(status, cmd_line)
        else:
            check_call([cmd_line], stdout=stdout, stderr=stderr, env=addtnl_env)
    else:
        os_environ = os.environ.copy()
        os_environ = dict(list(os_environ.items()) + list(addtnl_env.items()))
        if is_string(cmd_line):
            cmd_line = cmd_line.split()
        sudo_prefix = []
        if not as_admin():
            sudo_prefix = ['sudo']
        if quiet:
            check_call(sudo_prefix + cmd_line, stdout=stdout, stderr=stderr,
                       env=os_environ)
        else:
            check_call(sudo_prefix + cmd_line,
                       stdout=sys.stdout, stderr=sys.stderr, env=os_environ)


# pylint: disable=W0613
def mingw_check_call(environ, cmd_line, stdin=None, stdout=None, stderr=None,
                     addtnl_env=None):
    if addtnl_env is None:
        addtnl_env = dict()
    path = os.path.join(environ['MSYS_DIR'], 'bin') + ';' + \
        os.path.join(environ['MINGW_DIR'], 'bin') + ';'
    os_environ = os.environ.copy()
    old_path = os_environ.get('PATH', '')
    os_environ['PATH'] = path.encode('ascii', 'ignore') + os.pathsep + old_path
    os_environ = dict(list(os_environ.items()) + list(addtnl_env.items()))
    shell = os.path.join(environ['MSYS_DIR'], 'bin', 'bash.exe')
    if not is_string(cmd_line):
        cmd_line = ' '.join(cmd_line)
    p = subprocess.Popen(shell + ' -c "' + cmd_line + '"',
                         env=os_environ, stdout=stdout, stderr=stderr)
    status = p.wait()
    if status != 0:
        raise subprocess.CalledProcessError(status, cmd_line)


def get_script_relative_rpath(pkg_name, argv):
    py_ver = 'python' + '.'.join(get_python_version())
    packages = 'site-packages'
    lib_dir = 'lib'
    if 'windows' in platform.system().lower():
        lib_dir = 'Lib'
        py_ver = ''
        for arg in argv:
            if arg.startswith('--user'):
                lib_dir = ''
                py_ver = 'Python' + ''.join(get_python_version())
            elif arg.startswith('--home'):
                lib_dir = 'lib'
                py_ver = 'python'
                packages = ''
    elif struct.calcsize('P') == 8:
        lib_dir += '64'
        for arg in argv:
            if arg.startswith('--home'):
                py_ver = 'python'
                packages = ''
    return os.path.join('..', lib_dir, py_ver, packages, pkg_name)


