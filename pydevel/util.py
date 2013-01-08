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

import os, sys

## Prefer local implementations (urllib2, httplib) over global
here = os.path.dirname(__file__)
sys.path.insert(0, os.path.abspath(here))

import platform, fnmatch, warnings, glob, struct, time, shutil
import urllib2, httplib
import urllib, socket, tempfile
import tarfile, zipfile, subprocess


default_path_prefixes = ['/usr','/usr/local','/opt/local','C:\\MinGW'] + glob.glob('C:\\Python*')

download_file = ''

local_lib_dir = 'python'
download_dir  = 'third_party'

default_py2exe_library = 'library.zip'


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
    for path in pathlist + path_env:
        if path != None and os.path.exists(path):
            if DEBUG:
                print 'Searching ' + path + ' for ' + name
            for p in [path, os.path.join(path, 'bin')]:
                full = os.path.join(p, name)
                if os.path.exists(full):
                    return full
                if os.path.exists(full + '.exe'):
                    return full + '.exe'
                if os.path.exists(full + '.bat'):
                    return full + '.bat'
    raise Exception(name + ' not found.')



def find_header(filepath, extra_paths=[], extra_subdirs=[], limit=False):
    '''
    Find the containing directory of the specified header file.
    extra_subdir may be a pattern.
    '''
    subdirs = ['include',]
    for sub in extra_subdirs:
        subdirs += [os.path.join('include', sub), sub]
    subdirs += ['']  ## lastly, widen search
    pathlist = extra_paths
    if not limit:
        pathlist += default_path_prefixes
    for path in pathlist:
        if path != None and os.path.exists(path):
            for sub in subdirs:
                ext_path = os.path.join(path, sub)
                if DEBUG:
                    print 'Searching ' + ext_path + ' for ' + filepath
                filename = os.path.basename(filepath)
                dirname = os.path.dirname(filepath)
                for root, dirnames, filenames in os.walk(ext_path):
                    rt = os.path.normpath(root)
                    for fn in filenames:
                        if dirname == ''and fnmatch.fnmatch(fn, filename):
                            return root
                        elif fnmatch.fnmatch(os.path.basename(rt), dirname) \
                                and fnmatch.fnmatch(fn, filename):
                            return os.path.dirname(rt)
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
    of the given library.
    '''
    default_lib_paths = ['', 'lib', 'lib64']
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
    pathlist = extra_paths
    if not limit:
        pathlist += default_path_prefixes
    for path in pathlist:
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
                                            return root, fn
                                        else:
                                            libs.append(fn)
                                if len(libs) > 0:
                                    return root, libs
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
    for path in pathlist:
        if path != None and os.path.exists(path):
            if DEBUG:
                print 'Searching ' + path + ' for ' + filepattern
            for fn in os.listdir(path):
                if fnmatch.fnmatch(fn, filepattern):
                    return os.path.join(path, fn)
    raise Exception(filepattern + ' not found.')


def patch_file(filepath, match, original, replacement):
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


def install_pyscript_locally(website, name, build_dir):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    target_dir = os.path.join(build_dir, local_lib_dir)
    try:
        sys.stdout.write('PREREQUISITE ' + name + ' ')
        set_downloading_file(name)
        if not os.path.exists(name):
            urlretrieve(website + name, os.path.join(download_dir, name),
                        download_progress)
            sys.stdout.write('\n')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        shutil.copy(os.path.join(download_dir, name), target_dir)
    except Exception,e:
        raise Exception('Unable to install ' + name + ' locally: ' + str(e))


def install_pypkg_locally(name, website, archive, build_dir, env=None):
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    here = os.path.abspath(os.getcwd())
    target_dir = os.path.abspath(build_dir)
    try:
        set_downloading_file(archive)
        if not os.path.exists(os.path.join(download_dir, archive)):
            urlretrieve(website + archive, os.path.join(download_dir, archive),
                        download_progress)
            sys.stdout.write('\n')
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        os.chdir(target_dir)
        sys.stdout.write('PREREQUISITE ' + name + ' ')
        sys.stdout.flush()
        if not os.path.exists(name):
            if archive.endswith('.tgz') or archive.endswith('.tar.gz'):
                z = tarfile.open(os.path.join(here, download_dir, archive),
                                 'r:gz')
                z.extractall()
            elif archive.endswith('.tar.bz2'):
                z = tarfile.open(os.path.join(here, download_dir, archive),
                                 'r:bz2')
                z.extractall()
            elif archive.endswith('.zip'):
                z = zipfile.ZipFile(os.path.join(here, download_dir, archive),
                                    'r')
                z.extractall()
            else:
                raise Exception('Unrecognized archive compression: ' + archive)
        os.chdir(name)
        if env:
            for e in env:
                (key, value) = e.split('=')
                os.environ[key] = value
        os.environ['PYTHONPATH'] = os.path.join(target_dir, local_lib_dir)
        cmd_line = ['python', 'setup.py', 'build', 'install',
                    '--home=' + target_dir,
                    '--install-lib=' + os.path.join(target_dir, local_lib_dir),
                    ]
        log_file = name + '.log'
        log = open(log_file, 'w')
        log.write(str(cmd_line) + '\n\n')
        log.flush()
        try:
            p = subprocess.Popen(cmd_line, stdout=log, stderr=log)
            status = process_progress(p)
            log.close()
        except KeyboardInterrupt,e:
            p.terminate()
            log.close()
            raise e
        if status != 0:
            sys.stdout.write(' failed; See ' + log_file + '\n')
            raise Exception(name + ' is required, but could not be ' +
                            'installed locally; See ' + log_file)
        else:
            sys.stdout.write(' done\n')
        #if not os.path.join(target_dir, local_lib_dir) in sys.path:
        #    sys.path.insert(0, os.path.join(target_dir, local_lib_dir))
        os.chdir(here)
    except Exception,e:
        os.chdir(here)
        raise Exception('Unable to install ' + name + ' locally: ' + str(e))



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


def get_script_relative_rpath(pkg_name, argv):
    py_ver = 'python' + str(sys.version_info[0]) +'.'+ str(sys.version_info[1])
    packages = 'site-packages'
    lib_dir = 'lib'
    if 'windows' in platform.system().lower():
        lib_dir = 'Lib'
        py_ver = ''
        for arg in argv:
            if arg.startswith('--user'):
                lib_dir = ''
                py_ver = 'Python' + str(sys.version_info[0]) + \
                    str(sys.version_info[1])
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
    ver = 'python'+ str(sys.version_info[0]) +'.'+ str(sys.version_info[1])
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
    if preferred_dir is not None:
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
        os.environ['PATH'] += _sep_ + 'gtk/lib' + _sep_ + 'gtk/bin'

        msvc_version = '9.0'  ## boost-python requires MSVC 9.0
        msvc_path = os.path.join(os.environ['ProgramFiles(x86)'],
                                 'Microsoft Visual Studio ' + msvc_version,
                                 'VC', 'redist')
        msvc_release_path = os.path.join(msvc_path, 'x86', 'Microsoft.VC90.CRT')
        msvc_debug_path = os.path.join(msvc_path, 'Debug_NonRedist',
                                       'x86', 'Microsoft.VC90.DebugCRT')

        if not os.path.exists(msvc_release_path):  ## use MingW
            # FIXME MinGW msvc*90.dll??
            msvc_release_path = os.path.join('pydevel', 'win_release')
            msvc_debug_path = os.path.join('pydevel', 'win_debug')

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
                    'bundle_files': 1,
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

        specific_options = dict(
            windows = exe_target,
            package_dir = {pkg_config.PACKAGE: pkg_config.PACKAGE},
            packages = pkgs,
            package_data = pkg_data,
            data_files = addtnl_files + pkg_config.extra_libraries,
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


