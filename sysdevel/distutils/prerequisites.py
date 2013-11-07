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
import ast

try:
    import json
except ImportError:
    import simplejson as json

from .filesystem import mkdir
from .building import process_progress


default_path_prefixes = ['/usr', '/usr/local', '/opt/local',
                         ] + glob.glob('C:\\Python*\\')


local_lib_dir = 'python'
global_prefix = '/usr'
javascript_dir = 'javascript'
stylesheet_dir = 'stylesheets'
script_dir = 'scripts'
target_build_dir = 'build'
windows_postinstall = 'postinstall.py'

default_py2exe_library = 'library.zip'

environment_defaults = dict({
        'WX_ENABLED'   : False,
        'GTK_ENABLED'  : False,
        'QT4_ENABLED'  : False,
        'QT3_ENABLED'  : False,
        'FLTK_ENABLED' : False,
        'TK_ENABLED'   : False,
        })


VERBOSE = False
DEBUG = False

def set_verbose(b):
    global VERBOSE
    VERBOSE = b

def set_debug(b):
    global DEBUG
    DEBUG = b

def set_build_dir(dir):
    global target_build_dir
    target_build_dir = dir




class PrerequisiteError(Exception):
    pass


class RequirementsFinder(ast.NodeVisitor):
    def __init__(self, filepath=None):
        ast.NodeVisitor.__init__(self)
        self.variables = {}
        self.is_sysdevel_build = False
        self.requires_list = []
        if filepath:
            source = open(filepath, 'r')
            code = source.read()
            tree = ast.parse(code)
            self.visit(tree)

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
                        # elif type(node.value) == ast.Call:
                        #    FIXME evaluate ast.Call
    
    def visit_keyword(self, node):
        if self.is_sysdevel_build:
            return  ## will be ingoring these results anyway
        if node.arg == 'requires':
            if type(node.value) == ast.List:
                self.requires_list = ast.literal_eval(node.value)
            elif type(node.value) == ast.Name:
                if node.value.id != node.arg:
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

local_search_paths = []

def read_cache():
    global local_search_paths
    cache_file = os.path.join(target_build_dir, '.cache')
    if os.path.exists(cache_file):
        cache = open(cache_file, 'rb')
        cached = json.load(cache)
        local_search_paths = cached['local_search_paths']
        environ = cached['environment']
        cache.close()
        if len(local_search_paths) == 0:
            local_search_paths = [os.path.abspath(target_build_dir)]
        return environ
    return dict()

def save_cache(environ):
    cache_file = os.path.join(target_build_dir, '.cache')
    if not os.path.isdir(target_build_dir):
        if os.path.exists(target_build_dir):
            os.remove(target_build_dir)
        mkdir(target_build_dir)
    cache = open(cache_file, 'wb')
    cached = dict()
    cached['local_search_paths'] = local_search_paths
    cached['environment'] = environ
    json.dump(cached, cache)
    cache.close()

def delete_cache():
    cache = os.path.join(target_build_dir, '.cache')
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
        pathlist += path_env + local_search_paths
    for path in pathlist:
        if path != None and (os.path.exists(path) or glob.glob(path)):
            for p in [path, os.path.join(path, 'bin')]:
                if DEBUG:
                    print('Searching ' + p + ' for ' + name)
                full = os.path.join(p, name)
                if os.path.lexists(full):
                    if DEBUG:
                        print('Found ' + full)
                    return full
                if os.path.lexists(full + '.exe'):
                    if DEBUG:
                        print('Found ' + full + '.exe')
                    return full + '.exe'
                if os.path.lexists(full + '.bat'):
                    if DEBUG:
                        print('Found ' + full + '.bat')
                    return full + '.bat'
                if os.path.lexists(full + '.cmd'):
                    if DEBUG:
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
        pathlist += default_path_prefixes + local_search_paths
    filename = filepath
    for path in pathlist:
        if path != None and os.path.exists(path):
            for sub in subdirs:
                ext_paths = glob.glob(os.path.join(path, sub))
                for ext_path in ext_paths:
                    if DEBUG:
                        print('Searching ' + ext_path + ' for ' + filepath)
                    filename = os.path.basename(filepath)
                    dirname = os.path.dirname(filepath)
                    for root, dirnames, filenames in os.walk(ext_path):
                        rt = os.path.normpath(root)
                        for fn in filenames:
                            if dirname == '' and fnmatch.fnmatch(fn, filename):
                                if DEBUG:
                                    print('Found ' + os.path.join(root, filename))
                                return root.rstrip(os.sep)
                            elif fnmatch.fnmatch(os.path.basename(rt), dirname) \
                                    and fnmatch.fnmatch(fn, filename):
                                if DEBUG:
                                    print('Found ' + os.path.join(rt, filename))
                                return os.path.dirname(rt).rstrip(os.sep)
    raise Exception(filename + ' not found.')


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
    ## FIXME for Windows, separate definitions (*.dll.a, *.lib) from libs (*.dll, *.a) as libname_SHLIB_DIR
    default_lib_paths = ['lib64', 'lib', '']
    suffixes = ['.so', '.a']
    prefixes = ['', 'lib']
    definitions = []
    if 'windows' in platform.system().lower():
        def_suffixes = ['.dll.a', '.lib']
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
        pathlist += default_path_prefixes + local_search_paths
    for path in pathlist:
        if path != None and os.path.exists(path):
            for subpath in default_lib_paths:
                for sub in subdirs:
                    for root, dirnames, filenames in \
                            os.walk(os.path.join(path, subpath, sub)):
                        for prefix in prefixes:
                            if 'windows' in platform.system().lower():
                                for def_suffix in def_suffixes:
                                    if wildcard:
                                        filename = prefix + name + '*' + def_suffix
                                    else:
                                        filename = prefix + name + def_suffix
                                    if DEBUG:
                                        print('Searching ' + root + \
                                            ' for ' + filename)
                                    libs = []
                                    for fn in filenames:
                                        if fnmatch.fnmatch(fn, filename):
                                            definitions.append((root.rstrip(os.sep), fn))
                                    #FIXME return to caller
                            for suffix in suffixes:
                                if wildcard:
                                    filename = prefix + name + '*' + suffix
                                else:
                                    filename = prefix + name + suffix
                                if DEBUG:
                                    print('Searching ' + root + \
                                        ' for ' + filename)
                                libs = []
                                for fn in filenames:
                                    if fnmatch.fnmatch(fn, filename):
                                        if single:
                                            if DEBUG:
                                                print('Found at ' + root)
                                            return root.rstrip(os.sep), fn
                                        else:
                                            libs.append(fn)
                                if len(libs) > 0:
                                    if DEBUG:
                                        print('Found at ' + root)
                                    return root.rstrip(os.sep), libs
    raise Exception(name + ' library not found.')


def libraries_from_components(components, path):
    libs = []
    for comp in components:
        if DEBUG:
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
    #FIXME handle case where filepattern is a path
    for path in local_search_paths + pathlist:
        if path != None and os.path.exists(path):
            if DEBUG:
                print('Searching ' + path + ' for ' + filepattern)
            for fn in os.listdir(path):
                if fnmatch.fnmatch(fn, filepattern):
                    if DEBUG:
                        print('Found ' + os.path.join(path, fn))
                    return os.path.join(path, fn)
    raise Exception(filepattern + ' not found.')




def compare_versions(actual, requested):
    if isinstance(actual, float):
        actual = str(actual)
    if isinstance(requested, float):
        requested = str(requested)
    if is_string(actual):
        actual = actual.replace('_', '.')
        ver1 = tuple(actual.split('.'))
    else:
        ver1 = actual
    if is_string(requested):
        requested = requested.replace('_', '.')
        ver2 = tuple(requested.split('.'))
    else:
        ver2 = requested
    if ver2 is None:
        if ver1 is None:
            return 0
        return 1  ## None == latest
    while len(ver1) < len(ver2):
        ver1 = ver1 + ('0',)
    while len(ver1) > len(ver2):
        ver2 = ver2 + ('0',)
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
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    if locally:
        target_dir = os.path.join(os.path.abspath(target_build_dir), local_lib_dir)
    else:
        target_dir = get_python_lib()
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    fetch(website, name, name)
    if VERBOSE:
        sys.stdout.write('PREREQUISITE ' + name + ' ')
    try:
        shutil.copy(os.path.join(download_dir, name), target_dir)
    except Exception:
        e = sys.exc_info()[1]
        raise Exception('Unable to install ' + name + ': ' + str(e))


def install_pypkg(name, website, archive, env=None, src_dir=None, locally=True,
                  patch=None, extra_cmds=[], extra_args=[]):
    compiler = []
    if 'windows' in platform.system().lower():
        # FIXME on windows only if using mingw
        compiler.append('--compiler=mingw32')
    if src_dir is None:
        src_dir = name
    here = os.path.abspath(os.getcwd())
    target_dir = os.path.abspath(target_build_dir)
    target_lib_dir = os.path.join(target_dir, local_lib_dir)

    fetch(website, archive, archive)
    unarchive(archive, src_dir)
    if patch:
        patch(os.path.join(target_dir, src_dir))

    if VERBOSE:
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
            if VERBOSE:
                sys.stdout.write(' done\n')
        if locally:
            site.addsitedir(target_lib_dir)
            if not target_lib_dir in sys.path:
                sys.path.insert(0, target_lib_dir)
        os.chdir(here)
    except Exception:
        os.chdir(here)
        e = sys.exc_info()[1]
        raise Exception('Unable to install ' + name + ': ' + str(e))

    if locally:
        return target_lib_dir
    try:
        __import__(name)
        module = sys.modules[name]
        return os.path.dirname(module.__file__)
    except:
        return get_python_lib()



def autotools_install(environ, website, archive, src_dir, locally=True,
                      extra_cfg=[], addtnl_env=dict()):
    global local_search_paths
    here = os.path.abspath(os.getcwd())
    fetch(''.join(website), archive, archive)
    unarchive(archive, src_dir)

    if locally:
        prefix = os.path.abspath(target_build_dir)
        if not prefix in local_search_paths:
            local_search_paths.append(prefix)
    else:
        prefix = global_prefix
    prefix = convert2unixpath(prefix)  ## MinGW shell strips backslashes

    build_dir = os.path.join(target_build_dir, src_dir)  ## build in-place
    mkdir(build_dir)
    os.chdir(build_dir)
    log = open('build.log', 'w')
    if 'windows' in platform.system().lower():
        ## Assumes MinGW present, detected, and loaded in environment
        mingw_check_call(environ, ['./configure', '--prefix="' + prefix + '"'] +
                         extra_cfg, stdout=log, stderr=log,
                         addtnl_env=addtnl_env)
        mingw_check_call(environ, ['make'], stdout=log, stderr=log,
                         addtnl_env=addtnl_env)
        mingw_check_call(environ, ['make', 'install'], stdout=log, stderr=log,
                         addtnl_env=addtnl_env)
    else:
        os_environ = os.environ.copy()
        os_environ = dict(list(os_environ.items()) + list(addtnl_env.items()))
        check_call(['./configure', '--prefix=' + prefix] + extra_cfg,
                   stdout=log, stderr=log, env=os_environ)
        check_call(['make'], stdout=log, stderr=log, env=os_environ)
        if locally:
            check_call(['make', 'install'], stdout=log, stderr=log,
                       env=os_environ)
        else:
            admin_check_call(['make', 'install'], stdout=log, stderr=log,
                             addtnl_env=addtnl_env)
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
    mkdir(target_build_dir)
    log = open(os.path.join(target_build_dir, what + '.log'), 'w')
    if 'windows' in platform.system().lower() and winstaller:
        fetch(''.join(website_tpl), winstaller, winstaller)
        installer = os.path.join(download_dir, winstaller)
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
    os_environ['PATH'] = path.encode('ascii', 'ignore') #+ old_path #FIXME?
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


