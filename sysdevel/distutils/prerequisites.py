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
Utilities for prerequisite library and build-tool installation
"""

import os
import sys
import platform
import subprocess
import fnmatch
import struct
import glob
import time
import traceback
import site
import ast
import re

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


class RequirementsFinder(ast.NodeVisitor):
    req_keywords = ['requires', #'install_requires',
                    ]
    cfg_keyword = 'configure_system'

    def __init__(self, filepath=None, filedescriptor=None, codestring=None):
        ast.NodeVisitor.__init__(self)
        self.variables = {}
        self.is_sysdevel_build = False
        self.needs_early_config = False
        self.requires_list = []
        if filepath:
            self._load_from_path(filepath)
        elif filedescriptor:
            self._load_from_file(filedescriptor)
        elif codestring:
            self._load_from_string(codestring)


    def _load_from_string(self, code):
        tree = ast.parse(code)
        self.visit(tree)
        required = list(self.requires_list)
        self.requires_list = []
        for r in required:
            if '=' in r:
                idx = r.find('>')
                if idx < 0:
                    idx = r.find('=')
                self.requires_list.append((r[:idx], r[idx+2:]))
            else:
                self.requires_list.append(r)


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
                        #   TODO evaluate ast.Call for assignment
            if type(node.value) == ast.Call:
                if type(node.value.func) == ast.Name:
                    if node.value.func.id == self.cfg_keyword:
                        self.needs_early_config = True


    def visit_keyword(self, node):
        if self.is_sysdevel_build:
            return  ## will be ingoring these results anyway
        for kw in self.req_keywords:
            if node.arg == kw:
                if type(node.value) == ast.List:
                    self.requires_list = ast.literal_eval(node.value)
                elif type(node.value) == ast.Name:
                    self.requires_list = ast.literal_eval(
                        self.variables[node.value.id])  ## fails on ast.Call
        

    def visit_Import(self, node):
        for name in node.names:
            if name.name.startswith('sysdevel'):
                self.is_sysdevel_build = True

    def visit_ImportFrom(self, node):
        if node.module.startswith('sysdevel'):
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
        except:
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


def find_program(name, pathlist=[], limit=False):
    '''
    Find the path of an executable.
    '''
    try:
        path_env = os.environ['PATH'].split(os.pathsep)
    except:
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
    raise Exception(name + ' not found.')



def find_header(filepath, extra_paths=[], extra_subdirs=[], limit=False):
    '''
    Find the containing directory of the specified header file.
    extra_subdir may be a pattern. For Windows, it is important to not
    have a trailing path separator.
    '''
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
                    for root, dirnames, filenames in os.walk(ext_path):
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
    raise Exception(filename + ' not found.')


def find_definitions(name, extra_paths=[], extra_subdirs=[],
                     limit=False, single=False, wildcard=True):
    '''
    Find the containing directory and definitions filenames of
    the given library. Windows only.
    '''
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
                for root, dirnames, filenames in \
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
    raise Exception(name + ' library definitions not found.')


def find_library(name, extra_paths=[], extra_subdirs=[],
                 limit=False, wildcard=True):
    '''
    Find the containing directory and proper filename (returned as a tuple)
    of the given library.
    '''
    return find_libraries(name, extra_paths, extra_subdirs,
                          limit, True, wildcard=wildcard)


def find_libraries(name, extra_paths=[], extra_subdirs=[],
                   limit=False, single=False, wildcard=True):
    '''
    Find the containing directory and proper filenames (returned as a tuple)
    of the given library. For Windows, it is important to not have a
    trailing path separator.
    '''
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
                    for root, dirnames, filenames in \
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
    raise Exception(name + ' library not found.')


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


def find_file(filepattern, pathlist=[]):
    '''
    Find the full path of the specified file.
    '''
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
    raise Exception(filepattern + ' not found.')



def version_str_split(v):
    pattern = re.compile('(\d+)[_\.]?(\d+)*[_\.]?(\d+)*[\-_\.]?(\S+)*')
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
        except:
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
    except:
        pass
    os.unlink(tempsrc)
    try:
        os.unlink(tempobj)
    except:
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
        except Exception:  ## others not supported
            os_name = platform.system().lower()
            pkg.allow_network_updates = False
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
    except Exception:
        e = sys.exc_info()[1]
        raise Exception('Unable to install ' + name + ': ' + str(e))


def install_pypkg_without_fetch(name, env=None, src_dir=None, locally=True,
                                patch=None, extra_cmds=[], extra_args=[]):
    compiler = []
    if 'windows' in platform.system().lower():
        # TODO iff windows is using mingw:
        compiler.append('--compiler=mingw32')
    if src_dir is None:
        src_dir = name
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
                ['build'] + compiler + ['install', '--home=' + target_dir,
                 '--install-lib=' + target_lib_dir] + extra_args
        else:
            sudo_prefix = []
            if not as_admin():
                sudo_prefix = ['sudo']
            cmd_line = sudo_prefix + [sys.executable, 'setup.py'] + \
                extra_cmds + ['build'] + compiler + ['install'] + extra_args
        log_file = os.path.join(target_dir, name + '.log')
        log = open(log_file, 'w')
        log.write(str(cmd_line) + '\n\n')
        log.flush()
        try:
            p = subprocess.Popen(cmd_line, env=environ, stdout=log, stderr=log,
                                 shell=shell)
            status = process_progress(p)
            log.close()
        except KeyboardInterrupt:
            p.terminate()
            log.close()
            e = sys.exc_info()[1]
            raise e
        if status != 0:
            sys.stdout.write(' failed; See ' + log_file)
            raise Exception(name + ' is required, but could not be ' +
                            'installed; See ' + log_file)
        else:
            if options.VERBOSE:
                sys.stdout.write(' done\n')
        if locally:
            site.addsitedir(target_lib_dir)
            if not target_lib_dir in sys.path:
                sys.path.insert(0, target_lib_dir)
        os.chdir(here)
    except Exception:
        os.chdir(here)
        raise Exception('Unable to install ' + name + ':\n' +
                        str(sys.exc_info()[1]) + '\n' + traceback.format_exc())

    if locally:
        return target_lib_dir
    try:
        __import__(name)
        module = sys.modules[name]
        return os.path.dirname(module.__file__)
    except:
        return get_python_lib()




def install_pypkg(name, website, archive, env=None, src_dir=None, locally=True,
                  patch=None, extra_cmds=[], extra_args=[]):
    if src_dir is None:
        src_dir = name

    fetch(website, archive, archive)
    unarchive(archive, src_dir)

    return install_pypkg_without_fetch(name, env, src_dir, locally,
                                       patch, extra_cmds, extra_args)



def autotools_install(environ, website, archive, src_dir, locally=True,
                      extra_cfg=[], addtnl_env=dict()):
    here = os.path.abspath(os.getcwd())
    fetch(''.join(website), archive, archive)
    unarchive(archive, src_dir)

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
            except:
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
            except:
                pass
    finally:
        log.close()
        os.chdir(here)


def system_uses_apt_get():
    if 'linux' in platform.system().lower():
        try:
            find_program('apt-get')
            return os.path.exists('/etc/apt/sources.list')
        except:
            pass
    return False

def system_uses_yum():
    if 'linux' in platform.system().lower():
        try:
            find_program('yum')
            return os.path.exists('/etc/yum.conf')
        except:
            pass
    return False

def system_uses_homebrew():
    if 'darwin' in platform.system().lower():
        try:
            find_program('brew')
            return True
        except:
            pass
    return False

def system_uses_macports():
    if 'darwin' in platform.system().lower():
        try:
            find_program('port')
            return os.path.exists(macports_prefix() + '/etc/macports/macports.conf')
        except:
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
    log = open(os.path.join(options.target_build_dir, what + '.log'), 'w')
    if 'windows' in platform.system().lower() and winstaller:
        fetch(''.join(website_tpl), winstaller, winstaller)
        installer = os.path.join(options.download_dir, winstaller)
        try:
            admin_check_call(installer, stdout=log, stderr=log)
        except:
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
                     addtnl_env=dict()):
    if 'windows' in platform.system().lower():
        if not is_string(cmd_line):
            cmd_line = ' '.join(cmd_line)
        if not as_admin():
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


def mingw_check_call(environ, cmd_line, stdin=None, stdout=None, stderr=None,
                     addtnl_env=dict()):
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


