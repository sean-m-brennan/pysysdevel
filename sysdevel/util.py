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
Utilities for finding prerequisities
"""

import os
import sys
import site
import platform
import fnmatch
import warnings
import glob
import struct
import time
import shutil
import tarfile
import zipfile
import subprocess
import re
import distutils.sysconfig

try:
    import json
except ImportError:
    import simplejson as json


default_path_prefixes = ['/usr', '/usr/local', '/opt/local',
                         ] + glob.glob('C:\\Python*\\')

download_file = ''

local_lib_dir = 'python'
global_prefix = '/usr'
download_dir  = 'third_party'
local_search_paths = []
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


def in_prerequisites(item, prereqs):
    for p in prereqs:
         if not isinstance(p, basestring):
            if item == p[0]:
                return True
         elif item == p:
             return True
    return False


def sysdevel_support_path(filename):
    return os.path.join(os.path.dirname(__file__), 'support', filename)



########################################
## Duplicates of NumPy utilities (in case numpy is not used)

cxx_ext_match = re.compile(r'.*[.](cpp|cxx|cc)\Z',re.I).match
fortran_ext_match = re.compile(r'.*[.](f90|f95|f77|for|ftn|f)\Z',re.I).match
f90_ext_match = re.compile(r'.*[.](f90|f95)\Z',re.I).match
f90_module_name_match = re.compile(r'\s*module\s*(?P<name>[\w_]+)',re.I).match
def _get_f90_modules(source):
    """Return a list of Fortran f90 module names that
    given source file defines.
    """
    if not f90_ext_match(source):
        return []
    modules = []
    f = open(source,'r')
    f_readlines = getattr(f,'xreadlines',f.readlines)
    for line in f_readlines():
        m = f90_module_name_match(line)
        if m:
            name = m.group('name')
            modules.append(name)
            # break  # XXX can we assume that there is one module per file?
    f.close()
    return modules

def is_string(item):
    return isinstance(item, basestring)

def all_strings(lst):
    """Return True if all items in lst are string objects. """
    for item in lst:
        if not is_string(item):
            return False
    return True

def is_sequence(seq):
    if is_string(seq):
        return False
    try:
        len(seq)
    except:
        return False
    return True

def has_f_sources(sources):
    """Return True if sources contains Fortran files """
    for source in sources:
        if fortran_ext_match(source):
            return True
    return False

def has_cxx_sources(sources):
    """Return True if sources contains C++ files """
    for source in sources:
        if cxx_ext_match(source):
            return True
    return False

def filter_sources(sources):
    """Return four lists of filenames containing
    C, C++, Fortran, and Fortran 90 module sources,
    respectively.
    """
    c_sources = []
    cxx_sources = []
    f_sources = []
    fmodule_sources = []
    for source in sources:
        if fortran_ext_match(source):
            modules = _get_f90_modules(source)
            if modules:
                fmodule_sources.append(source)
            else:
                f_sources.append(source)
        elif cxx_ext_match(source):
            cxx_sources.append(source)
        else:
            c_sources.append(source)
    return c_sources, cxx_sources, f_sources, fmodule_sources

########################################


def glob_insensitive(directory, file_pattern):
    def either(c):
        return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c
    return glob.glob(os.path.join(directory, ''.join(map(either, file_pattern))))


def rcs_revision(rcs_type=None):
    if rcs_type is None:
        if os.path.exists('.git'):
            rcs_type = 'git'
        elif os.path.exists('.hg'):
            rcs_type = 'hg'
        elif os.path.exists('.svn'):
            rcs_type = 'svn'
        elif os.path.exists('CVS'):
            raise Exception('Unsupported Revision Control System.')
        else:  # tarball install
            return None

    if rcs_type.lower() == 'git':
        cmd_line = ['git', 'rev-list', 'HEAD']
    elif rcs_type.lower() == 'hg' or rcs_type.lower() == 'mercurial':
        cmd_line = ['hg', 'log', '-r', 'tip',
                    '--template "{latesttag}.{latesttagdistance}"']
    elif rcs_type.lower() == 'svn' or rcs_type.lower() == 'subversion':
        cmd_line = ['svnversion']
    else:
        raise Exception('Unknown Revision Control System.')

    shell=False
    if 'windows' in platform.system().lower():
        shell = True
    p = subprocess.Popen(cmd_line, stdout=subprocess.PIPE, shell=shell)
    out = p.communicate()[0].strip()
    if p.wait() != 0:
        raise Exception('Failed to get ' + rcs_type + ' version.')
    if rcs_type.lower() == 'git':
        return len(out.splitlines())
    elif rcs_type.lower() == 'hg' or rcs_type.lower() == 'mercurial':
        return int(out, 10)
    elif rcs_type.lower() == 'svn' or rcs_type.lower() == 'subversion':
        end = out.find('M')
        if end < 0:
            end = len(out)
        return int(out[out.find(':')+1:end], 10)
    else:
        return 0



def convert_ulist(str_list):
    ## distutils *might* not be able to handle unicode, convert it
    if str_list is None:
        return None
    converted = []
    for s in str_list:
        if isinstance(s, unicode):
            converted.append(''.join(chr(ord(c)) for c in s.decode('ascii')))
        else:
            converted.append(s)
    return converted


def uniquify(seq, id_fctn=None):
    if id_fctn is None:
        def id_fctn(x): return x
    result = []
    for item in seq:
        marker = id_fctn(item)
        if marker not in result:
            result.append(item)
    return result


def flatten(seq):
    result = []
    for elt in seq:
        if hasattr(elt, '__iter__') and not isinstance(elt, basestring):
            result.extend(flatten(elt))
        else:
            result.append(elt)
    return result


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
        if path != None and os.path.exists(path):
            for p in [path, os.path.join(path, 'bin')]:
                if DEBUG:
                    print 'Searching ' + p + ' for ' + name
                full = os.path.join(p, name)
                if os.path.lexists(full):
                    if DEBUG:
                        print 'Found ' + full
                    return full
                if os.path.lexists(full + '.exe'):
                    if DEBUG:
                        print 'Found ' + full + '.exe'
                    return full + '.exe'
                if os.path.lexists(full + '.bat'):
                    if DEBUG:
                        print 'Found ' + full + '.bat'
                    return full + '.bat'
                if os.path.lexists(full + '.cmd'):
                    if DEBUG:
                        print 'Found ' + full + '.cmd'
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
                        print 'Searching ' + ext_path + ' for ' + filepath
                    filename = os.path.basename(filepath)
                    dirname = os.path.dirname(filepath)
                    for root, dirnames, filenames in os.walk(ext_path):
                        rt = os.path.normpath(root)
                        for fn in filenames:
                            if dirname == '' and fnmatch.fnmatch(fn, filename):
                                if DEBUG:
                                    print 'Found ' + os.path.join(root, filename)
                                return root.rstrip(os.sep)
                            elif fnmatch.fnmatch(os.path.basename(rt), dirname) \
                                    and fnmatch.fnmatch(fn, filename):
                                if DEBUG:
                                    print 'Found ' + os.path.join(rt, filename)
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
                                        print 'Searching ' + root + \
                                            ' for ' + filename
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
                                    print 'Searching ' + root + \
                                        ' for ' + filename
                                libs = []
                                for fn in filenames:
                                    if fnmatch.fnmatch(fn, filename):
                                        if single:
                                            if DEBUG:
                                                print 'Found at ' + root
                                            return root.rstrip(os.sep), fn
                                        else:
                                            libs.append(fn)
                                if len(libs) > 0:
                                    if DEBUG:
                                        print 'Found at ' + root
                                    return root.rstrip(os.sep), libs
    raise Exception(name + ' library not found.')

def libraries_from_components(components, path):
    libs = []
    for comp in components:
        if DEBUG:
            print 'Searching ' + path + ' for ' + comp
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
                print 'Searching ' + path + ' for ' + filepattern
            for fn in os.listdir(path):
                if fnmatch.fnmatch(fn, filepattern):
                    if DEBUG:
                        print 'Found ' + os.path.join(path, fn)
                    return os.path.join(path, fn)
    raise Exception(filepattern + ' not found.')


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


def patch_c_only_header(filepath):
    orig = open(filepath, 'r')
    lines = orig.readlines()
    orig.close()
    shutil.move(filepath, filepath + '.orig')
    fixed = open(filepath, 'w')
    fixed.write('#ifdef __cplusplus\nextern "C" {\n#endif\n\n')
    for line in lines:
        fixed.write(line)
    fixed.write('\n#ifdef __cplusplus\n}\n#endif\n')
    fixed.close()
 

def process_progress(p):
    max_dots = 10
    prev = dots = 0
    status = p.poll()
    while status is None:
        if VERBOSE:
            prev = dots
            dots += 1
            dots %= max_dots
            if prev:
                sys.stdout.write('\b' * prev)
            sys.stdout.write('.' * dots)
            sys.stdout.flush()
        time.sleep(0.2)
        status = p.poll()
    if VERBOSE:
        sys.stdout.write('\b' * dots)
        sys.stdout.write('.' * max_dots)
        sys.stdout.flush()
    return status
 

def get_header_version(hdr_file, define_val):
    '''
    Given a C header file and a define macro, extract a version string.
    '''
    f = open(hdr_file, 'r')
    for line in f:
        if define_val in line and '#define' in line:
            f.close()
            return line[line.rindex(define_val) + len(define_val):].strip()
    f.close()
    raise Exception('No version information (' + define_val +
                    ') in ' + hdr_file)


def set_downloading_file(dlf):
    '''
    Set the global for the download_progress callback below.
    '''
    global download_file
    download_file = dlf

def download_progress(count, block_size, total_size):
    '''
    Callback for displaying progress for use with urlretrieve()
    '''
    percent = int(count * block_size * 100 / total_size)
    if VERBOSE:
        sys.stdout.write("\rFETCHING " + download_file + "  %2d%%" % percent)
        sys.stdout.flush()


def fetch(website, remote, local):
    mkdir(download_dir)
    set_downloading_file(remote)
    if not os.path.exists(os.path.join(download_dir, local)):
        urlretrieve(website + remote, os.path.join(download_dir, local),
                    download_progress)
        if VERBOSE:
            sys.stdout.write('\n')


def zipextractall(zip_file):
    ## zip_file.extractall not in 2.4
    for name in zip_file.namelist():
        (dirname, filename) = os.path.split(name)
        if not os.path.exists(dirname):
            mkdir(dirname)
        if not filename == '':
            f = open(name, 'w')
            f.write(zip_file.read(name))
            f.close()

    
def tarextractall(tar_file):
    ## tar_file.extractall not in 2.4
    for tarinfo in tar_file:
        tar_file.extract(tarinfo)

    
def unarchive(archive, target, archive_dir=download_dir):
    here = os.path.abspath(os.getcwd())
    if not os.path.exists(os.path.join(target_build_dir, target)):
        mkdir(target_build_dir)
        os.chdir(target_build_dir)
        if archive.endswith('.tgz') or archive.endswith('.tar.gz'):
            z = tarfile.open(os.path.join(here, archive_dir, archive), 'r:gz')
            tarextractall(z)
            z.close()
        elif archive.endswith('.tar.bz2'):
            z = tarfile.open(os.path.join(here, archive_dir, archive), 'r:bz2')
            tarextractall(z)
            z.close()
        elif archive.endswith('.zip'):
            z = zipfile.ZipFile(os.path.join(here, archive_dir, archive), 'r')
            zipextractall(z)
            z.close()
        else:
            raise Exception('Unrecognized archive compression: ' + archive)
        os.chdir(here)


def create_script_wrapper(pyscript, target_dir):
    pyscript = os.path.basename(pyscript)
    if 'windows' in platform.system().lower():
        dst_ext = '.bat'
    else:
        dst_ext = '.sh'
    dst_file = os.path.join(target_dir, os.path.splitext(pyscript)[0] + dst_ext)
    if not os.path.exists(dst_file):
        f = open(dst_file, 'w')
        if 'windows' in platform.system().lower():
            wexe = os.path.join(os.path.dirname(sys.executable), 'pythonw')
            exe = os.path.join(os.path.dirname(sys.executable), 'python')
            f.write('@echo off\nsetlocal\n' +
                    'set PATH=%~dp0..\\Lib;%PATH%\n' +
                    exe + ' "%~dp0' + pyscript + '" %*')
        else:
            f.write(
                '#!/bin/bash\n\n' + 
                'loc=`dirname "$0"`\n' + 
                'path=`cd "$loc/.."; pwd`\n' + 
                'export LD_LIBRARY_PATH=$path/lib:$path/lib64:$LD_LIBRARY_PATH\n' +
                'export DYLD_LIBRARY_PATH=$path/lib:$path/lib64:$DYLD_LIBRARY_PATH\n' +
                sys.executable + ' $path/bin/' + pyscript + ' $@\n')
        f.close()
        os.chmod(dst_file, 0777)
    return dst_file


def create_runscript(pkg, mod, target, extra):
    if not os.path.exists(target):
        if extra is None:
            extra = ''
        if DEBUG:
            print 'Creating runscript ' + target
        f = open(target, 'w')
        f.write("#!/usr/bin/env python\n" +
                "# -*- coding: utf-8 -*-\n\n" +
                "## In case the app is not installed in the standard location\n" + 
                "import sys\n" +
                "import os\n" +
                "import platform\n" + 
                "import struct\n\n" + 
                "if hasattr(sys, 'frozen'):\n" + 
                "    here = os.path.dirname(unicode(sys.executable,\n" +
                "                                   sys.getfilesystemencoding()))\n" + 
                "else:\n" +
                "    here = os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))\n" +
                "ver = 'python'+ str(sys.version_info[0]) +'.'+ str(sys.version_info[1])\n" +
                "bases = [here]\n" +
                "if 'windows' in platform.system().lower():\n" +
                "    bases.append(os.path.join(here, '..', 'Lib', 'site-packages'))\n" +
                "else:\n" +
                "    lib = 'lib'\n" +
                "    bases.append(os.path.join(here, '..', lib, ver, 'site-packages'))\n" +
                "    if struct.calcsize('P') == 8:\n" +
                "        lib = 'lib64'\n" +
                "        bases.append(os.path.join(here, '..', lib, ver, 'site-packages'))\n" +
                "for base in bases:\n" +
                "    sys.path.insert(0, os.path.abspath(base))\n\n" +
                "##############################\n\n" +
                extra +
                "from " + pkg + " import " + mod + "\n" +
                mod + ".main()\n")
        f.close()
        os.chmod(target, 0777)


def create_test_wrapper(pyscript, target_dir, lib_dirs):
    pyscript = os.path.basename(pyscript)
    if 'windows' in platform.system().lower():
        dst_ext = '.bat'
    else:
        dst_ext = '.sh'
    dst_file = os.path.join(target_dir, os.path.splitext(pyscript)[0] + dst_ext)
    f = open(dst_file, 'w')
    if 'windows' in platform.system().lower():
        wexe = os.path.join(os.path.dirname(sys.executable), 'pythonw')
        exe = os.path.join(os.path.dirname(sys.executable), 'python')
        dirlist = ''
        for d in lib_dirs:
            dirlist += os.path.abspath(d) + ';' 
        f.write('@echo off\nsetlocal\n' +
                'set PATH=' + dirlist + '%PATH%\n' +
                exe + ' "%~dp0' + pyscript + '" %*')
    else:
        dirlist = ''
        for d in lib_dirs:
            dirlist += os.path.abspath(d) + ':' 
        f.write('#!/bin/bash\n\n' +
                'loc=`dirname "$0"`\n' + 
                'export LD_LIBRARY_PATH=' + dirlist + '$LD_LIBRARY_PATH\n' +
                'export DYLD_LIBRARY_PATH=' + dirlist + '$DYLD_LIBRARY_PATH\n' +
                sys.executable + ' $loc/' + pyscript + ' $@\n')
    f.close()
    os.chmod(dst_file, 0777)
    return dst_file


def create_testscript(tester, units, target, pkg_dirs):
    if DEBUG:
        print 'Creating testscript ' + target
    f = open(target, 'w')
    f.write("#!/usr/bin/env python\n" +
            "# -*- coding: utf-8 -*-\n\n" +
            "## In case the app is not installed in the standard location\n" + 
            "import sys\n" +
            "import os\n" +
            "bases = [os.path.dirname(unicode(__file__, sys.getfilesystemencoding()))]\n"
            )
    for d in pkg_dirs:
        f.write("bases.append(r'" + d + "')\n")
    f.write("for base in bases:\n" +
            "    sys.path.insert(0, os.path.abspath(base))\n\n" +
            "##############################\n\n"
            )
    for unit in units:
        f.write("from " + tester + "." + unit + " import *\n")
    f.write("\nimport unittest\nunittest.main()\n")
    f.close()
    os.chmod(target, 0777)


def create_fruit_driver(unit, srcfile):
    test_functions = ''
    i = open(srcfile, 'r')
    for line in i:
        delim = 'subroutine'
        if delim in line:
            test_functions += 'call ' + line[len(delim)+1:] + '\n'
    i.close()
    test_driver = unit + '_fruit_driver.f90'
    o = open(test_driver, 'w')
    o.write('program ' + unit + '_fruit_driver\n' +
            'use fruit\n' +
            'use ' + unit + '\n' +
            'call init_fruit\n' +
            test_functions +
            'call fruit_summary\n' +
            'end program ' + unit + '_fruit_driver\n'
            )
    o.close()
    return test_driver


def create_cunit_driver(unit, srcfile):
    i = open(srcfile, 'r')
    lines = i.readlines()
    i.close()
    setup_fctn = ''
    if not 'setUp' in lines:
        setup_fctn = 'int setUp(void) {\n  return 0;\n}\n'
    teardown_fctn = ''
    if not 'tearDown' in lines:
        teardown_fctn = 'int tearDown(void) {\n  return 0;\n}\n'
    tests = []
    for line in lines:
        start = line.find('void ')
        end = line.find('(void)')
        if start >= 0 and end > 0:
            test_name = line[start+5:end-5]
            tests.append('       (NULL == CU_add_test(pSuite, "' + test_name +
                         '", ' + test_name + ')) ')
    test_driver = unit + '_cunit_driver.cpp'
    o = open(test_driver, 'w')
    o.write('#include <CUnit/Basic.h>\n' +
            setup_fctn + teardown_fctn + 
            'int main(int argc, char* argv[]) {\n' +
            '   CU_pSuite pSuite = NULL;\n' +
            '   if (CUE_SUCCESS != CU_initialize_registry())\n' +
            '      return CU_get_error();\n' +
            '   pSuite = CU_add_suite("' + unit + '", setup, teardown);\n' +
            '   if (NULL == pSuite) {\n' +
            '      CU_cleanup_registry();\n' +
            '      return CU_get_error();\n' +
            '   }\n' +
            '   if (\n' + 
            '||\n'.join(tests) + '\n' +
            '      ) {\n' +
            '      CU_cleanup_registry();\n' +
            '      return CU_get_error();\n' +
            '   }\n' +
            '   CU_basic_set_mode(CU_BRM_VERBOSE);\n' +
            '   CU_basic_run_tests();\n' +
            '   CU_cleanup_registry();\n' +
            '   return CU_get_error();\n' +
            '}\n'
            )
    o.close()
    return test_driver


def create_cppunit_driver(unit):
    test_driver = unit + '_cppunit_driver.cpp'
    o = open(test_driver, 'w')
    o.write('#include <cppunit/CompilerOutputter.h>\n' +
            '#include <cppunit/extensions/TestFactoryRegistry.h>\n' +
            '#include <cppunit/ui/text/TestRunner.h>\n' +
            'int main(int argc, char* argv[]) {\n' +
            '  CppUnit::Test *suite = CppUnit::TestFactoryRegistry::getRegistry().makeTest();\n' +

            '  CppUnit::TextUi::TestRunner runner;\n' +
            '  runner.addTest( suite );\n' +
            '  runner.setOutputter( new CppUnit::CompilerOutputter( &runner.result(), std::cerr ) );\n' +
            '  bool wasSucessful = runner.run();\n' +
            '  return wasSucessful ? 0 : 1;\n' +
            '}\n'
            )
    o.close()
    return test_driver


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


def symlink(original, target):
    if not os.path.lexists(target):
        if not os.path.isabs(original):
            levels = len(target.split(os.sep))-1
            for l in range(levels):
                original = os.path.join('..', original)
        try:
            os.symlink(original, target)
        except:
            shutil.copyfile(original, target)


def is_out_of_date(target, source, additional=[]):
    extra = False
    for addtnl in additional:
        if os.path.exists(target) and os.path.exists(addtnl):
            extra = extra or os.path.getmtime(addtnl) > os.path.getmtime(target)

    if (not os.path.exists(target)) or extra or \
            (os.path.getmtime(source) > os.path.getmtime(target)):
        return True
    return False
 

def configure_files(var_dict, directory_or_file_list,
                    pattern='*.in', target_dir=None, excludes=[]):
    '''
    Given a dictionary of environment variables,
    and either a list of files or a directory, an optional filename pattern
    (default '*.in') and an optional target directory,
    apply configure_file.
    '''
    if isinstance(directory_or_file_list, list):
        file_list = directory_or_file_list
        for filepath in file_list:
            configure_file(var_dict, filepath)
        return
    else:
        directory = directory_or_file_list
        matches = []
        for root, dirnames, filenames in os.walk(directory):
            for ex in excludes:
                if fnmatch.fnmatch(root, ex):
                    continue
            for filename in fnmatch.filter(filenames, pattern):
                matches.append((root, filename))
        remove_pattern = '.in'
        if not pattern.endswith('.in'):
            remove_pattern = None
        for path, filename in matches:
            subdir = path[len(directory)+1:]
            newpath = None
            if target_dir != None:
                newpath = os.path.join(target_dir, subdir, filename)
            configure_file(var_dict, os.path.join(path, filename),
                           newpath, remove_pattern)


def mkdir(newdir):
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("A *file* with the same name as the desired " +
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir(head)
        if tail:
            os.mkdir(newdir)


def copy_tree(src, dst, preserve_mode=1, preserve_times=1, preserve_symlinks=0,
              update=0, verbose=0, dry_run=0, excludes=[]):
    '''
    Extends distutils.dir_util.copy_tree to exclude given patterns
    '''
    from distutils import dir_util, file_util
    from distutils.errors import DistutilsFileError
    from distutils import log

    if not dry_run and not os.path.isdir(src):
        raise DistutilsFileError, \
              "cannot copy tree '%s': not a directory" % src
    try:
        names = os.listdir(src)
    except os.error, (errno, errstr):
        if dry_run:
            names = []
        else:
            raise DistutilsFileError, \
                  "error listing files in '%s': %s" % (src, errstr)

    if not dry_run:
        dir_util.mkpath(dst)

    outputs = []

    for n in names:
        exclude = False
        for excl in excludes:
            if fnmatch.fnmatch(n, excl):
                exclude = True
        if exclude:
            if verbose:
                log.info("excluding %s from copy", n)
            continue

        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)

        if preserve_symlinks and os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            log.info("linking %s -> %s", dst_name, link_dest)
            if not dry_run:
                os.symlink(link_dest, dst_name)
            outputs.append(dst_name)

        elif os.path.isdir(src_name):
            outputs.extend(
                copy_tree(src_name, dst_name, preserve_mode,
                          preserve_times, preserve_symlinks, update,
                          verbose, dry_run, excludes))
        else:
            file_util.copy_file(src_name, dst_name, preserve_mode,
                                preserve_times, update, None,
                                verbose=verbose, dry_run=dry_run)
            outputs.append(dst_name)

    return outputs


(DEFAULT_STYLE, AUTOMAKE_STYLE, AUTOCONF_STYLE) = range(3)

def nested_values(line, var_dict, d=0, style=DEFAULT_STYLE):
    var_dict = dict(environment_defaults, **var_dict)

    fr_delim = '@@{'
    bk_delim = '}'
    cmt_delim = '#'
    if style == AUTOCONF_STYLE:
        fr_delim = '$('
        bk_delim = ')'
    elif style == AUTOMAKE_STYLE:
        fr_delim = '@'
        bk_delim = '@'
    fr_len = len(fr_delim)
    
    cmt = line.find(cmt_delim)
    front = line.find(fr_delim)
    while front >= 0:  ## sequential
        back = line.find(bk_delim, front+fr_len)
        if back < 0 or (cmt >= 0 and cmt < front):
            break
        last = line.rfind(fr_delim, front+fr_len)
        while last >= 0 and last < back and last > front:  ## nested only
            back2 = line.rfind(bk_delim, front+fr_len)
            replacement = nested_values(line[front+fr_len:back2], var_dict, d+1)
            line = line.replace(line[front+fr_len:back2], replacement)
            last = line.rfind(fr_delim, front+fr_len)
        back = line.find(bk_delim, front+fr_len)
        valname = line[front+fr_len:back]
        if len(valname.split()) > 1:  ## disallow whitespace
            front = back
            continue
        value = var_dict[valname]
        line = line.replace(line[front:back+1], str(value))
        front = line.find(fr_delim)
    return line


def configure_file(var_dict, filepath, newpath=None, suffix='.in',
                   style=DEFAULT_STYLE):
    '''
    Given a dictionary of environment variables and a path,
    replace all occurrences of @@{VAR} with the value of the VAR key.
    If style is AUTOCONF_STYLE, use the style $(VAR).
    If style is AUTOMAKE_STYLE, use the style @VAR@.
    VAR may not have whitespace in the string.
    '''
    if newpath is None:
        newpath = filepath[:-(len(suffix))]
    if os.path.exists(newpath) and \
            (os.path.getmtime(filepath) < os.path.getmtime(newpath)):
        ## i.e. original is older than existing generated file
        return
    if VERBOSE:
        print 'Configuring ' + newpath
    orig = open(filepath, 'r')
    newdir = os.path.dirname(newpath)
    if not os.path.exists(newdir):
        mkdir(newdir)
    new = open(newpath, 'w')
    for line in orig:
        line = nested_values(line, var_dict, style=style)
        new.write(line)
    orig.close()
    new.close()


def recursive_chown(directory, uid, gid):
    for root, dirnames, filenames in os.walk(directory):
        for dirname in dirnames:
            os.chown(os.path.join(root, dirname), uid, gid)
        for filename in filenames:
            os.chown(os.path.join(root, filename), uid, gid)


def clean_generated_files():
    ## remove all but input files and test directory
    matches = []
    for root, dirnames, filenames in os.walk('gmat'):
        for filename in filenames:
            if filename.endswith('.in') and \
                    os.path.exists(os.path.join(root, filename[:-3])):
                matches.append(os.path.join(root, filename[:-3]))
            if filename.endswith('bindings.cpp'):
                matches.append(os.path.join(root, filename))
    for filepath in matches:
        try:
            os.unlink(filepath)
        except:
            pass


def get_python_version():
    return (str(sys.version_info[0]), str(sys.version_info[1]))


def major_minor_version(ver):
    sver = str(ver)
    tpl = sver.split('.')
    return '.'.join(tpl[:2])


def compare_versions(actual, requested):
    if isinstance(actual, float):
        actual = str(actual)
    if isinstance(requested, float):
        requested = str(requested)
    if isinstance(actual, basestring):
        actual = actual.replace('_', '.')
        ver1 = tuple(actual.split('.'))
    else:
        ver1 = actual
    if isinstance(requested, basestring):
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


class PrerequisiteError(Exception):
    pass


def install_pyscript(website, name, locally=True):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    if locally:
        target_dir = os.path.join(os.path.abspath(target_build_dir), local_lib_dir)
    else:
        target_dir = distutils.sysconfig.get_python_lib()
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    fetch(website, name, name)
    if VERBOSE:
        sys.stdout.write('PREREQUISITE ' + name + ' ')
    try:
        shutil.copy(os.path.join(download_dir, name), target_dir)
    except Exception,e:
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
        except KeyboardInterrupt,e:
            p.terminate()
            log.close()
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
    except Exception,e:
        os.chdir(here)
        raise Exception('Unable to install ' + name + ': ' + str(e))

    if locally:
        return target_lib_dir
    try:
        __import__(name)
        module = sys.modules[name]
        return os.path.dirname(module.__file__)
    except:
        return distutils.sysconfig.get_python_lib()


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
        os_environ = dict(os_environ.items() + addtnl_env.items())
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
        if not isinstance(cmd_line, basestring):
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
        os_environ = dict(os_environ.items() + addtnl_env.items())
        if isinstance(cmd_line, basestring):
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
    os_environ = dict(os_environ.items() + addtnl_env.items())
    shell = os.path.join(environ['MSYS_DIR'], 'bin', 'bash.exe')
    if not isinstance(cmd_line, basestring):
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


def safe_eval(stmt):
    ## TODO restrict possible functions/modules used
    safe_list = []  ## allowable modules and functions
    safe_builtins = []  ## allowable builtin functions
    safe_dict = dict([ (k, globals().get(k, None)) for k in safe_list ])
    safe_dict['__builtins__'] = safe_builtins
    #return eval(stmt, safe_dict)  #TODO not implemented
    return eval(stmt)

#FIXME unify argv, environ and options handling

def handle_arguments(argv, option_list=[]):
    if '--quiet' in argv:
        set_verbose(False)
    if '--debug' in argv:
        set_debug(True)
        argv.remove('--debug')

    option_plus_list = list(option_list)
    option_plus_list.append('doc')

    options = dict()
    options['bundle'] = False
    options['runscript'] = ''
    options['ziplib'] = None

    bundle = False
    if 'py2exe' in argv:
         bundle = True
    if 'py2app' in argv:
         bundle = True
    app = ''
    runscript = ''
    for arg in argv:
        if arg == '-b' or arg == '--build_base':
            idx = argv.index(arg)
            set_build_dir(argv[idx+1])

        if arg.startswith('--app='):
            app = runscript = arg[6:].lower()
            runscript = arg[6:].lower()
            if not runscript.endswith('.py'):
                runscript = runscript + '.py'
            for root, dirnames, filenames in os.walk('.'): ## source directory
                for filename in filenames:
                    if filename == runscript:
                        runscript = os.path.join(root, filename)
                        break
            argv.remove(arg)
            break
        if arg.startswith('--ziplib'):
            if '=' in arg:
                options['ziplib'] = arg[9:]
                if options['ziplib'][-4:] != '.zip':
                    options['ziplib'] += '.zip'
            else:
                options['ziplib'] = default_py2exe_library
            
    if bundle and app != '' and runscript != '':
        options['bundle'] = bundle
        options['runscript'] = runscript
        options['app'] = app

    options['install_dir'] = sys.prefix
    data_directory = 'share'
    data_override = False
    for idx, arg in enumerate(argv[:]):
        if arg.startswith('--prefix='):
            options['install_dir'] = arg[9:]
        elif arg.startswith('--home='):
            options['install_dir'] = arg[7:]
        elif arg.startswith('--user='):
            options['install_dir'] = arg[7:]
        elif arg.startswith('--install-data='):
            path = arg[15:]
            if os.path.isabs(path):
                options['data_install_dir'] = path
                data_override = True  ## always overrides the above prefixes
            else:
                data_directory = path
        elif arg.startswith('build_') and arg[6:] in option_plus_list:
            options[arg[6:]] = True
            if not 'build' in argv:
                argv.insert(idx, 'build')
            argv.remove(arg)
        elif arg.startswith('install_') and arg[8:] in option_plus_list:
            options[arg[8:]] = True
            if not 'install' in argv:
                argv.insert(idx, 'install')
            argv.remove(arg)
        elif arg.startswith('clean_') and arg[8:] in option_plus_list:
            options[arg[8:]] = True
            if not 'clean' in argv:
                argv.insert(idx, 'clean')
            argv.remove(arg)
    if not data_override:
        options['data_install_dir'] = os.path.join(options['install_dir'],
                                                   data_directory)

    build_all = True
    for opt in option_list:  ## do not build docs by default
        if opt in options:
            build_all = False
    if build_all:
        for opt in option_list:
            options[opt] = True
           
    if 'doc' in options:
        options['documentation'] = True
    else:
        options['documentation'] = False

    return options, argv


def get_options(pkg_config, options):
    '''
    pkg_config is a 'mydistutils.pkg_config' object.
    options from 'handle_arguments' above.
    '''
    target_os = platform.system().lower()  ## disallow cross-compile
    is_bundle = options['bundle']
    runscript = options['runscript']

    ##############################
    ## Windows plus py2exe
    if is_bundle and target_os == 'windows':
        warnings.simplefilter('ignore', DeprecationWarning)
        import py2exe
        warnings.resetwarnings()

        INCLUDE_GTK_WIN = False
        INCLUDE_TCLTK_WIN = False
        #os.environ['PATH'] += os.pathsep + 'gtk/lib' + os.pathsep + 'gtk/bin'

        package_name = pkg_config.PACKAGE
        icon_file = os.path.join(pkg_config.PACKAGE, pkg_config.image_dir,
                                 pkg_config.PACKAGE + '.ico')
    
        addtnl_files = []
        addtnl_files += pkg_config.get_data_files(options['app'])
        addtnl_files += pkg_config.get_extra_data_files(options['app'])
        addtnl_files += [('.', [icon_file])]
        addtnl_files += [('.', pkg_config.get_missing_libraries())]
        icon_res = [(0, icon_file)]

        if INCLUDE_GTK_WIN:
            gtk_includes = ['cairo', 'pango', 'pangocairo', 'atk',
                            'pygtk', 'gtk', 'gobject',]
        else:
            gtk_includes = []

        excludes = ['bsddb', 'curses', 'email',
                    'pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs',
                    ]
        dll_excludes = ['mswsock.dll', 'powrprof.dll',
                        'mpr.dll', 'msvcirt.dll', 'msvcrt.dll', 'netapi32.dll',
                        'netrap.dll', 'samlib.dll']

        if not INCLUDE_TCLTK_WIN:
            excludes += ['_gtkagg', '_tkagg', 'tcl', 'Tkconstants', 'Tkinter',]
            dll_excludes += ['tcl84.dll', 'tk84.dll',]
        if not INCLUDE_GTK_WIN:
            excludes += ['pygtk', 'gtk', 'gobject', 'gtkhtml2',]
            dll_excludes += ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll',]


        file_bundling = 1
        if 'app_type' in options and options['app_type'] == 'console':
            file_bundling = 3

        exe_opts = {'py2exe': {
                    'unbuffered': False,
                    'optimize': 2,
                    'includes': flatten(pkg_config.dynamic_modules.values()) + \
                        gtk_includes,
                    'packages': flatten(pkg_config.required_pkgs.values()) + \
                        pkg_config.extra_pkgs,
                    'ignores': [],
                    'excludes': excludes,
                    'dll_excludes': dll_excludes,
                    'dist_dir': os.path.join('bin_dist', options['app']),
                    'typelibs': [],
                    'compressed': False,
                    'xref': False,
                    'bundle_files': file_bundling,
                    'skip_archive': False,
                    'ascii': False,
                    'custom_boot_script': '',
                    }}

        exe_target = [{
                    'script': runscript,
                    'icon_resources': icon_res,
                    'bitmap_resources': [],
                    'other_resources': [],
                    'dest_base': options['app'],
                    'company_name': pkg_config.COMPANY,
                    }]

        pkgs = pkg_config.extra_pkgs
        pkg_data = dict({})
        p = pkg_config.PACKAGE
        while True:
            pkgs += [pkg_config.names[p]]
            pkg_data[pkg_config.names[p]] = pkg_config.package_files[p]
            p = pkg_config.parents[p]
            if p is None:
                break

        for lib in pkg_config.extra_libraries:
            os.environ['PATH'] += os.pathsep + lib[0]
            os.environ['PATH'] += os.pathsep + os.path.join(lib[0], '..', 'bin')

        if 'app_type' in options and options['app_type'] == 'console':
            specific_options = dict(
                console = exe_target,
                package_dir = {pkg_config.PACKAGE: pkg_config.PACKAGE},
                packages = pkgs,
                package_data = pkg_data,
                data_files = addtnl_files,
                options = exe_opts,
                zipfile = options['ziplib'],
                )
        else:
            specific_options = dict(
                windows = exe_target,
                package_dir = {pkg_config.PACKAGE: pkg_config.PACKAGE},
                packages = pkgs,
                package_data = pkg_data,
                data_files = addtnl_files,
                options = exe_opts,
                zipfile = options['ziplib'],
                )

        return specific_options

    ##############################
    ## Mac OS X plus py2app
    elif is_bundle and target_os == 'darwin':
        import py2app

        package_name = pkg_config.PACKAGE
        target = [runscript]
        addtnl_files = pkg_config.source_files
        addtnl_files += [('.', [os.path.join(pkg_config.image_path,
                                             pkg_config.PACKAGE + '.icns')])]
    
        plist = {'CFBundleName': package_name,
                 'CFBundleDisplayName': package_name,
                 'CFBundleIdentifier': pkg_config.ID,
                 'CFBundleVersion': pkg_config.VERSION,
                 'CFBundlePackageType': 'APPL',
                 'CFBundleExecutable': package_name.upper(),
                 'CFBundleShortVersionString': pkg_config.RELEASE,
                 'NSHumanReadableCopyright': pkg_config.COPYRIGHT,
                 'CFBundleGetInfoString': package_name + ' ' + pkg_config.VERSION,
                 }
        
        opts = {'py2app': {
            'optimize': 2,
            'includes': pkg_config.dynamic_modules,
            'packages': pkg_config.required_pkgs.values() + \
                pkg_config.extra_pkgs,
            'iconfile': os.path.join(pkg_config.PACKAGE, pkg_config.image_dir,
                                     pkg_config.PACKAGE + '.icns'),
            'excludes': ['tcl', 'Tkconstants', 'Tkinter', 'pytz',],
            'dylib_excludes': ['tcl84.dylib', 'tk84.dylib'],
            'datamodels': [],
            'resources': [],
            'frameworks': [],
            'plist': plist,
            'extension': '.app',
            'graph': False,
            'xref': False,
            #'no_strip': False,
            'no_strip': True,
            'no_chdir': True,
            'semi_standalone': False,
            'alias': False,
#            'argv_emulation': True,
            'argv_emulation': False,
            'argv_inject': [],
            'use_pythonpath': False,
            'bdist_base': pkg_config.build_dir,
            'dist_dir': 'bin_dist',
            'site_packages': True,
            #'strip': True,
            'strip': False,
            'prefer_ppc': False,
            'debug_modulegraph': False,
            'debug_skip_macholib': False,
            }}
    
        specific_options = dict(
            app = target,
            #packages = pkgs,
            #package_data = pkg_data,
            data_files = addtnl_files,
            options = opts,
            )
       
        return specific_options

    ##############################
    ## all others (assumes required packages are installed)
    else:
        directories = dict()
        data = dict()
        for p, h in pkg_config.hierarchy.items():
            pkg_name = pkg_config.names[p]
            directories[pkg_name] = os.path.join(pkg_config.PACKAGE,
                                                 pkg_config.directories[p])
            data[pkg_name] = pkg_config.package_files[p]
        specific_options = dict(
            package_dir = directories,
            packages = flatten(pkg_config.names.values()) + \
                pkg_config.extra_pkgs,
            package_data = data,
            create_scripts = pkg_config.generated_scripts,
            data_files = pkg_config.extra_data_files,
            tests = pkg_config.tests,
            )
        if target_os == 'windows':
            specific_options['bdist_wininst'] = {
                'bitmap': pkg_config.logo_bmp_path,
                'install_script': windows_postinstall,
                'keep_temp': True,
                'user_access_control': 'auto',
                }
            ## bdist_msi is incompatible with this build scheme

        return specific_options



def post_setup(pkg_config, options):
    bundled = options['bundle']
    if bundled:
        os_name = platform.system().lower()
        dist_dir = os.path.join('bin_dist', options['app'])
        current = os.getcwd()
        os.chdir(dist_dir)
        archive = options['app'] + '_' + os_name + '_' + pkg_config.RELEASE + '.zip'
        if pkg_config.PACKAGE != options['app']:
            archive = pkg_config.PACKAGE + '_' + archive
        z = zipfile.ZipFile(os.path.join(current, 'bin_dist', archive),
                            'w', zipfile.ZIP_DEFLATED)
        for root, dirnames, filenames in os.walk('.'):
            for filename in filenames:
                z.write(os.path.join(root, filename))
        z.close()
        os.chdir(current)



def urlretrieve(url, filename=None, progress=None, data=None, proxy=None):
    '''
    Identical to urllib.urlretrieve, except that it handles
    SSL, proxies ands redirects properly.
    '''
    import urllib
    import urllib2
    import tempfile
    import traceback

    proxy_url = proxy
    if proxy_url is None:
        try:
            proxy_url = os.environ['HTTP_PROXY']
        except:
            try:
                proxy_url = os.environ['http_proxy']
            except:
                raise Exception('No proxy specified. ' +
                                'Either call urlretrieve with a proxy ' +
                                "argument, or provide a 'http_proxy' " +
                                'environment variable.')

    proxies = urllib2.ProxyHandler({'http': proxy_url, 'https': proxy_url})
    opener = urllib2.build_opener(proxies)
    urllib2.install_opener(opener)

    try:
        req = urllib2.Request(url=url, data=data)
        fp = urllib2.urlopen(req)
        try:
            headers = fp.info()
            if filename:
                tfp = open(filename, 'wb')
            else:
                tfp = tempfile.NamedTemporaryFile(delete=False)
                filename = tfp.name

            try:
                result = filename, headers
                bs = 1024*8
                size = -1
                read = 0
                blocknum = 0
                if "content-length" in headers:
                    size = int(headers["Content-Length"])
                if progress:
                    progress(blocknum, bs, size)

                while True:
                    block = fp.read(bs)
                    if not block or block == "":
                        break
                    read += len(block)
                    tfp.write(block)
                    blocknum += 1
                    if progress:
                        progress(blocknum, bs, size)
            finally:
                tfp.close()
        finally:
            fp.close()
        del fp
        del tfp
    except urllib2.URLError, e:
        try:
            if hasattr(e, 'reason'):
                e.reason = url + ": " + e.reason
            elif hasattr(e, 'msg'):
                e.msg = url + ": " + e.msg
            else:
                sys.stderr.write("HTTP Error connecting to " + url + ":\n")
        except:
            sys.stderr.write("HTTP Error connecting to " + url + ":\n")
        raise e

    if size >= 0 and read < size:
        raise urllib.ContentTooShortError("%s: retrieval incomplete: "
                                          "got only %i out of %i bytes" %
                                          (url, read, size), result)

    return result


