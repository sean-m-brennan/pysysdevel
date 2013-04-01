#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Utilities for finding prerequisities
"""
#**************************************************************************
# 
# This material was prepared by the Los Alamos National Security, LLC 
# (LANS), under Contract DE-AC52-06NA25396 with the U.S. Department of 
# Energy (DOE). All rights in the material are reserved by DOE on behalf 
# of the Government and LANS pursuant to the contract. You are authorized 
# to use the material for Government purposes but it is not to be released 
# or distributed to the public. NEITHER THE UNITED STATES NOR THE UNITED 
# STATES DEPARTMENT OF ENERGY, NOR LOS ALAMOS NATIONAL SECURITY, LLC, NOR 
# ANY OF THEIR EMPLOYEES, MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR 
# ASSUMES ANY LEGAL LIABILITY OR RESPONSIBILITY FOR THE ACCURACY, 
# COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, PRODUCT, OR 
# PROCESS DISCLOSED, OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE 
# PRIVATELY OWNED RIGHTS.
# 
#**************************************************************************

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
import urllib
import urllib2
import httplib
import socket
import tempfile
import tarfile
import zipfile
import subprocess
import ctypes
import shelve
import distutils.sysconfig



default_path_prefixes = ['/usr', '/usr/local',
                         '/opt/local',
                         'C:\\MinGW', 'C:\\MinGW\\msy\1.0'] + \
                         glob.glob('C:\\Python*\\')

download_file = ''

local_lib_dir = 'python'
global_prefix = '/usr'
download_dir  = 'third_party'
local_search_paths = []
javascript_dir = 'javascript'
target_build_dir = 'build'

default_py2exe_library = 'library.zip'

environment_defaults = dict({
        'WX_ENABLED'   : False,
        'GTK_ENABLED'  : False,
        'QT4_ENABLED'  : False,
        'QT3_ENABLED'  : False,
        'FLTK_ENABLED' : False,
        'TK_ENABLED'   : False,
        })

_sep_ = ':'
if 'windows' in platform.system().lower():
    _sep_ = ';'

VERBOSE = True
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
        cache = shelve.open(cache_file)
        local_search_paths += cache['local_search_paths']
        cache.close()

def save_cache():
    cache_file = os.path.join(target_build_dir, '.cache')
    if not os.path.isdir(target_build_dir):
        if os.path.exists(target_build_dir):
            os.remove(target_build_dir)
        mkdir(target_build_dir)
    cache = shelve.open(cache_file)
    cache['local_search_paths'] = local_search_paths
    cache.close()

def delete_cache():
    cache = os.path.join(target_build_dir, '.cache')
    if os.path.exists(cache):
        os.remove(cache)


def sysdevel_support_path(filename):
    return os.path.join(os.path.dirname(__file__), 'support', filename)


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


def find_program(name, pathlist=[]):
    '''
    Find the path of an executable.
    '''
    try:
        path_env = os.environ['PATH'].split(_sep_)
    except:
        path_env = []
    for path in local_search_paths + pathlist + path_env:
        if path != None and os.path.exists(path):
            if DEBUG:
                print 'Searching ' + path + ' for ' + name
            for p in [path, os.path.join(path, 'bin')]:
                full = os.path.join(p, name)
                if os.path.exists(full):
                    if DEBUG:
                        print 'Found ' + full
                    return full
                if os.path.exists(full + '.exe'):
                    if DEBUG:
                        print 'Found ' + full + '.exe'
                    return full + '.exe'
                if os.path.exists(full + '.bat'):
                    if DEBUG:
                        print 'Found ' + full + '.bat'
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
        pathlist += default_path_prefixes
    for path in local_search_paths + pathlist:
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


def find_library(name, extra_paths=[], extra_subdirs=[], limit=False):
    '''
    Find the containing directory and proper filename (returned as a tuple)
    of the given library.
    '''
    return find_libraries(name, extra_paths, extra_subdirs, limit, True)


def find_libraries(name, extra_paths=[], extra_subdirs=[],
                   limit=False, single=False):
    '''
    Find the containing directory and proper filenames (returned as a tuple)
    of the given library. For Windows, it is important to not have a
    trailing path separator.
    '''
    default_lib_paths = ['lib64', 'lib', '']
    suffixes = ['.so', '.a']
    prefixes = ['', 'lib']
    if 'windows' in platform.system().lower():
        suffixes = ['.lib', '.a', '.dll']
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
        pathlist += default_path_prefixes
    for path in local_search_paths + pathlist:
        if path != None and os.path.exists(path):
            for subpath in default_lib_paths:
                for sub in subdirs:
                    for root, dirnames, filenames in \
                            os.walk(os.path.join(path, subpath, sub)):
                        for prefix in prefixes:
                            for suffix in suffixes:
                                filename = prefix + name + '*' + suffix
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
    

def process_progress(p):
    max_dots = 10
    prev = dots = 0
    status = p.poll()
    while status is None:
        prev = dots
        dots += 1
        dots %= max_dots
        if prev:
            sys.stdout.write('\b' * prev)
        sys.stdout.write('.' * dots)
        sys.stdout.flush()
        time.sleep(0.2)
        status = p.poll()
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
        sys.stdout.write("\r" + download_file + "  %d%%" % percent)
        sys.stdout.flush()


def fetch(website, remote, local):
    mkdir(download_dir)
    set_downloading_file(remote)
    if not os.path.exists(os.path.join(download_dir, local)):
        urlretrieve(website + remote, os.path.join(download_dir, local),
                    download_progress)
        sys.stdout.write('\n')


def unarchive(archive, target, archive_dir=download_dir):
    here = os.path.abspath(os.getcwd())
    if not os.path.exists(os.path.join(target_build_dir, target)):
        mkdir(target_build_dir)
        os.chdir(target_build_dir)
        if archive.endswith('.tgz') or archive.endswith('.tar.gz'):
            z = tarfile.open(os.path.join(here, archive_dir, archive), 'r:gz')
            z.extractall()
        elif archive.endswith('.tar.bz2'):
            z = tarfile.open(os.path.join(here, archive_dir, archive), 'r:bz2')
            z.extractall()
        elif archive.endswith('.zip'):
            z = zipfile.ZipFile(os.path.join(here, archive_dir, archive), 'r')
            z.extractall()
        else:
            raise Exception('Unrecognized archive compression: ' + archive)
        os.chdir(here)


def create_script_wrapper(pyscript, target_dir):
    dst_file = os.path.join(target_dir, )
    if not os.path.exists(dst_file):
        f = open(dst_file, 'w')
        if 'windows' in platform.system().lower():
            wexe = os.path.join(os.path.dirname(sys.executable), 'pythonw')
            exe = os.path.join(os.path.dirname(sys.executable), 'python')
            f.write('@echo off\n' +
                    exe + ' "%~dp0' + pyscript + '" %*')
        else:
            f.write('#!/bin/bash\n\n' + 
                    'loc=`dirname "$0"`\n' + 
                    'path=`cd "$loc/.."; pwd`\n' + 
                    'export LD_LIBRARY_PATH=$path/lib:$path/lib64:' +
                    '$LD_LIBRARY_PATH\n' +
                    sys.executable + ' $path/bin/' + pyscript + ' $@\n')
        f.close()

def create_runscript(pkg, mod, target):
    if not os.path.exists(target):
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
                "##############################\n\n"
                "from " + pkg + " import " + mod + "\n" +
                mod + ".main()\n")
        f.close()

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
                    pattern='*.in', target_dir=None):
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
    return '.'.join(tpl[0], tpl[1])


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

    sys.stdout.write('PREREQUISITE ' + name + ' ')
    fetch(website, name, name)
    try:
        shutil.copy(os.path.join(download_dir, name), target_dir)
    except Exception,e:
        raise Exception('Unable to install ' + name + ': ' + str(e))


def install_pypkg(name, website, archive, env=None, src_dir=None, locally=True):
    if src_dir is None:
        src_dir = name
    here = os.path.abspath(os.getcwd())
    target_dir = os.path.abspath(target_build_dir)
    target_lib_dir = os.path.join(target_dir, local_lib_dir)

    sys.stdout.write('PREREQUISITE ' + name + ' ')
    sys.stdout.flush()
    fetch(website, archive, archive)
    unarchive(archive, src_dir)
    if not os.path.exists(target_lib_dir):
        os.makedirs(target_lib_dir)
    try:
        os.chdir(os.path.join(target_dir, src_dir))
        environ = os.environ.copy()
        if env:
            for e in env:
                (key, value) = e.split('=')
                environ[key] = value
        if locally:
            environ['PYTHONPATH'] = target_lib_dir
            cmd_line = [sys.executable, 'setup.py', 'build', 'install',
                        '--home=' + target_dir,
                        '--install-lib=' + target_lib_dir]
        else:
            sudo_prefix = []
            if not as_admin():
                sudo_prefix = ['sudo']
            cmd_line = sudo_prefix + [sys.executable,
                                      'setup.py', 'build', 'install']
        log_file = os.path.join(target_dir, name + '.log')
        log = open(log_file, 'w')
        log.write(str(cmd_line) + '\n\n')
        log.flush()
        try:
            p = subprocess.Popen(cmd_line, env=environ, stdout=log, stderr=log)
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
            sys.stdout.write(' done')
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


def autotools_install(environ, website, archive, src_dir, locally=True,
                      extra_cfg=[]):
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

    build_dir = os.path.join(target_build_dir, src_dir, '_build')
    mkdir(build_dir)
    os.chdir(build_dir)
    if 'windows' in platform.system().lower():
        ## Assumes MinGW present, detected, and loaded in environment
        mingw_check_call(environ, ['../configure', '--prefix=' + prefix] +
                         extra_cfg)
        mingw_check_call(environ, ['make'])
        mingw_check_call(environ, ['make', 'install'])
    else:
        subprocess.check_call(['../configure', '--prefix=' + prefix] +
                              extra_cfg)
        subprocess.check_call(['make'])
        if locally:
            subprocess.check_call(['make', 'install'])
        else:
            admin_check_call(['make', 'install'])
    os.chdir(here)


def _uses_apt_get():
    try:
        find_program('apt-get')
        return os.path.exists('/etc/apt/sources.list')
    except:
        pass
    return False

def _uses_yum():
    try:
        find_program('yum')
        return os.path.exists('/etc/yum.conf')
    except:
        pass
    return False


def global_install(what, website_tpl, winstaller, port, apt, yum):
    if 'windows' in platform.system().lower() and winstaller:
        fetch(''.join(website_tpl), winstaller, winstaller)
        installer = os.path.join(download_dir, winstaller)
        admin_check_call(installer)

    elif 'darwin' in platform.system().lower() and port:
        ## assumes macports installed
        print '\nInstalling ' + ', '.join(port.split()) + ' in the system:'
        admin_check_call(['port', 'install',] + port.split())

    elif 'linux' in platform.system().lower():
        if _uses_apt_get() and apt:
            print '\nInstalling ' + ', '.join(apt.split()) + ' in the system:'
            admin_check_call(['apt-get', 'install',] + apt.split())

        elif _uses_yum() and yum:
            print '\nInstalling ' + ', '.join(yum.split()) + ' in the system:'
            admin_check_call(['yum', 'install',] + yum.split())

        else:
            raise PrerequisiteError('Unsupported Linux flavor. Install ' +
                                    what + 'by hand. See ' + website_tpl[0])
    else:
        raise PrerequisiteError('Unsupported platform. Install ' + what +
                                'by hand. See ' + website_tpl[0])


def as_admin():
    try:
        return os.geteuid() == 0
    except AttributeError:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0


def admin_check_call(cmd_line, quiet=False):
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
            subprocess.check_call([cmd_line])
    else:
        if isinstance(cmd_line, basestring):
            cmd_line = cmd_line.split()
        sudo_prefix = []
        if not as_admin():
            sudo_prefix = ['sudo']
        if quiet:
            subprocess.check_call(sudo_prefix + cmd_line)
        else:
            subprocess.check_call(sudo_prefix + cmd_line,
                                  stdout=sys.stdout, stderr=sys.stderr)


def mingw_check_call(environ, cmd_line, stdin=None, stdout=None, stderr=None):
    path = os.path.join(environ['MSYS_DIR'], 'bin') + ';' + \
        os.path.join(environ['MINGW_DIR'], 'bin') + ';'
    os_environ = os.environ.copy()
    old_path = os_environ.get('PATH', '')
    os_environ['PATH'] = path #+ old_path
    shell = os.path.join(environ['MSYS_DIR'], 'bin', 'bash.exe')
    if not isinstance(cmd_line, basestring):
        cmd_line = ' '.join(cmd_line)
    p = subprocess.Popen(shell + ' -c "' + cmd_line + '"',
                         env=os_environ)
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
        #os.environ['PATH'] += _sep_ + 'gtk/lib' + _sep_ + 'gtk/bin'

        msvc_version = '9.0'  ## boost-python requires MSVC 9.0
        msvc_path = os.path.join(os.environ['ProgramFiles(x86)'],
                                 'Microsoft Visual Studio ' + msvc_version,
                                 'VC', 'redist')
        msvc_release_path = os.path.join(msvc_path, 'x86', 'Microsoft.VC90.CRT')
        msvc_debug_path = os.path.join(msvc_path, 'Debug_NonRedist',
                                       'x86', 'Microsoft.VC90.DebugCRT')

        if not os.path.exists(msvc_release_path):  ## use MingW
            # FIXME MinGW msvc*90.dll??
            msvc_release_path = os.path.join('sysdevel', 'win_release')
            msvc_debug_path = os.path.join('sysdevel', 'win_debug')

        if pkg_config.build_config.lower() == 'debug':
            msvc_glob = os.path.join(msvc_debug_path, '*.*')
            sys.path.append(msvc_debug_path)
        else:
            msvc_glob = os.path.join(msvc_release_path, '*.*')
            sys.path.append(msvc_release_path)

        package_name = pkg_config.PACKAGE
        icon_file = os.path.join(pkg_config.PACKAGE, pkg_config.image_dir,
                                 pkg_config.PACKAGE + '.ico')
    
        addtnl_files = []
        addtnl_files += pkg_config.get_data_files(options['app'])
        addtnl_files += pkg_config.get_extra_data_files(options['app'])
        addtnl_files += [('.', [icon_file])]
        #addtnl_files += [('.', glob.glob(msvc_glob))] FIXME?
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
            'packages': pkg_config.required_pkgs + pkg_config.extra_pkgs + \
                packages_present,
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
            scripts = pkg_config.runscripts,
            data_files = pkg_config.extra_data_files,
            )
        if target_os == 'windows':
            specific_options['bdist_wininst'] = {
                'bitmap': os.path.join('gpstools', 'img', 'cxd_logo.bmp'),
                'install_script': 'gpstools_postinstall.py',
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

    if size >= 0 and read < size:
        raise urllib.ContentTooShortError("retrieval incomplete: "
                                          "got only %i out of %i bytes" %
                                          (read, size), result)

    return result


