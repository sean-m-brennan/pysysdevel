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
Utilities for package installation
"""

import os
import sys
import platform
import inspect
import fnmatch
import time
from glob import glob
from distutils.errors import DistutilsSetupError, DistutilsError, DistutilsFileError
from distutils.dep_util import newer_group

have_numpy = False
# pylint: disable=W0201
try:
    from numpy.distutils.command.build_clib import build_clib  # pylint: disable=F0401,W0611
    from numpy.distutils.misc_util import get_numpy_include_dirs
    from numpy.distutils import log
    have_numpy = True
except ImportError:
    from distutils.command.build_clib import build_clib  # pylint: disable=W0611
    from distutils import log

from sysdevel.util import is_string
from sysdevel.distutils.filesystem import mkdir
from sysdevel.distutils.numpy_utils import filter_sources, is_sequence
from sysdevel.distutils import options


environment_defaults = dict({
        'WX_ENABLED'   : False,
        'GTK_ENABLED'  : False,
        'QT4_ENABLED'  : False,
        'QT3_ENABLED'  : False,
        'FLTK_ENABLED' : False,
        'TK_ENABLED'   : False,
        })

(DEFAULT_STYLE, AUTOMAKE_STYLE, AUTOCONF_STYLE) = list(range(3))



def process_progress(p):
    max_dots = 10
    prev = dots = 0
    status = p.poll()
    while status is None:
        if options.VERBOSE:
            prev = dots
            dots += 1
            dots %= max_dots
            if prev:
                sys.stdout.write('\b' * prev)
            sys.stdout.write('.' * dots)
            sys.stdout.flush()
        time.sleep(0.2)
        status = p.poll()
    if options.VERBOSE:
        sys.stdout.write('\b' * dots)
        sys.stdout.write('.' * max_dots)
        sys.stdout.flush()
    return status
 


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
            #wexe = os.path.join(os.path.dirname(sys.executable), 'pythonw')
            exe = os.path.join(os.path.dirname(sys.executable), 'python')
            f.write('@echo off\nsetlocal\n' +
                    'set LOCAL_BIN_PATH=%~dp0\n' +
                    'set PATH=%~dp0..\\Lib;%PATH%\n' +
                    exe + ' "%~dp0' + pyscript + '" %*')
        else:
            f.write(
                '#!/bin/bash\n\n' + 
                'loc=`dirname "$0"`\n' + 
                'path=`cd "$loc/.."; pwd`\n' + 
                'export LD_LIBRARY_PATH=$path/lib:$path/lib64:$LD_LIBRARY_PATH\n' +
                'export DYLD_LIBRARY_PATH=$path/lib:$path/lib64:$DYLD_LIBRARY_PATH\n' +
                'export LOCAL_BIN_PATH=$path/bin\n' +
                sys.executable + ' $path/bin/' + pyscript + ' $@\n')
        f.close()
        os.chmod(dst_file, int('777', 8))
    return dst_file


def set_python_site(where=None):
    from inspect import getfile
    if not where:
        if hasattr(sys, 'frozen'):
            where = os.path.dirname(unicode(sys.executable,
                                            sys.getfilesystemencoding()))
        else:
            where = os.path.dirname(unicode(getfile(sys._getframe(1)),
                                            sys.getfilesystemencoding()))
    elif not os.path.isabs(where):
        if hasattr(sys, 'frozen'):
            where = os.path.abspath(os.path.join(
                os.path.dirname(unicode(sys.executable,
                                        sys.getfilesystemencoding())),
                where))
        else:
            where = os.path.abspath(os.path.join(
                os.path.dirname(unicode(__file__, sys.getfilesystemencoding())),
                where))
    lib_dirs = []
    python_version = sys.version[:3]
    if os.name == "posix":
        lib_dirs = [os.path.join(where, "lib",
                                 "python" + python_version, "site-packages"),
                    os.path.join(where, "lib64",
                                 "python" + python_version, "site-packages")]
    elif os.name == "nt" and python_version < "2.2":
        lib_dirs = [where]
    else:
        lib_dirs = [os.path.join(where, "Lib", "site-packages")]
    for base in lib_dirs:
        if not base in sys.path:
            sys.path.insert(0, base)


def get_python_site_code():
    return "import sys\nimport os\n" + \
        "".join(inspect.getsourcelines(set_python_site)[0])


def create_runscript(pkg, mod, target, extra):
    if not os.path.exists(target):
        if extra is None:
            extra = ''
        if options.DEBUG:
            print('Creating runscript ' + target)
        script = "#!/usr/bin/env " + os.path.basename(sys.executable) + "\n" + \
                "# -*- coding: utf-8 -*-\n\n" + \
                "## In case the app is not installed in the standard location\n" + \
                get_python_site_code() + "\n" + \
                "set_python_site('..')\n" + \
                "##############################\n\n" + \
                extra + \
                "from " + pkg + " import " + mod + "\n" + \
                mod + ".main()\n"
        f = open(target, 'w')
        f.write(script)
        f.close()
        os.chmod(target, int('777', 8))




def convert_ulist(str_list):
    ## distutils *might* not be able to handle unicode, convert it
    if str_list is None:
        return None
    converted = []
    for s in str_list:
        if is_string(s):
            converted.append(''.join(chr(ord(c)) for c in s.decode('ascii')))
        else:
            converted.append(s)
    return converted


def find_documentation(docbase=None, extra_suffixes=None):
    if docbase is None:
        docbase = '.'
    suffixes = ['.org', '.xml', '.rst']
    if extra_suffixes:
        suffixes += extra_suffixes
    directories = []
    for root, _, filenames in os.walk(docbase):
        for sfx in suffixes:
            if fnmatch.filter(filenames, '*' + sfx):
                directories.append(root)
    return directories



def configure_files(var_dict, directory_or_file_list,
                    pattern='*.in', target_dir=None, excludes=()):
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
        for root, _, filenames in os.walk(directory):
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




def nested_values(line, var_dict, d=0, style=DEFAULT_STYLE):
    var_dict = dict(environment_defaults, **var_dict)  # pylint: disable=W0142

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
    if options.VERBOSE:
        print('Configuring ' + newpath)
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



def safe_eval(stmt):
    safe_list = []  ## allowable modules and functions
    safe_builtins = []  ## allowable builtin functions
    safe_dict = dict([ (k, globals().get(k, None)) for k in safe_list ])
    safe_dict['__builtins__'] = safe_builtins
    #return eval(stmt, safe_dict)  #TODO restrict possible functions/modules used
    return eval(stmt)



def clean_generated_files():
    ## remove all but input files and test directory
    matches = []
    for root, _, filenames in os.walk('.'):
        for filename in filenames:
            if filename.endswith('.in') and \
                    os.path.exists(os.path.join(root, filename[:-3])):
                matches.append(os.path.join(root, filename[:-3]))
            if filename.endswith('bindings.cpp'):
                matches.append(os.path.join(root, filename))
    for filepath in matches:
        try:
            os.unlink(filepath)
        except OSError:
            pass



############################################################

SHARED_LIBRARY, EXECUTABLE = range(2)

def _get(obj, what, default=None):
    try:
        ## Dictionary
        return obj.get(what, default)
    except AttributeError:
        ## Attribute
        return getattr(obj, what, default)

def _put(obj, what, val):
    try:
        setattr(obj, what, val)
    except AttributeError:
        obj[what] = val


def build_target(builder, target, name, mode):
    """
    Common function for build_* commands
    """
    target_name = name
    if mode == SHARED_LIBRARY:
        target_name = builder.compiler.library_filename(name, lib_type='shared',
                                                        output_dir='')

    #libraries = convert_ulist(_get(target, 'libraries', []))  ## unused
    library_dirs = convert_ulist(_get(target, 'library_dirs', []))
    runtime_library_dirs = convert_ulist(_get(target,
                                               'runtime_library_dirs', []))
    extra_preargs = _get(target, 'extra_compile_args', [])
    extra_postargs = _get(target, 'extra_link_args', [])

    ## include libraries built by build_shlib and/or build_clib
    library_dirs.append(builder.build_temp)

    ## Conditional recompile
    build_directory = builder.build_clib
    target_path = os.path.join(build_directory, name)
    recompile = False
    if not os.path.exists(target_path) or builder.force:
        recompile = True
    else:
        for src in _get(target, 'sources', []):
            if os.path.getmtime(target_path) < os.path.getmtime(src):
                recompile = True
                break
    if not recompile:
        return
    library_dirs += [builder.build_clib]

    ########################################
    ## Copied from numpy.distutils.command.build_clib

    # default compilers
    compiler = builder.compiler
    fcompiler = getattr(builder, '_f_compiler', builder.fcompiler)

    sources = _get(target, 'sources')
    if sources is None or not is_sequence(sources):
        raise DistutilsSetupError(("in 'libraries' option (library '%s'), " +
                                   "'sources' must be present and must be " +
                                   "a list of source filenames") % name)
    sources = list(sources)

    c_sources, cxx_sources, f_sources, fmodule_sources = filter_sources(sources)
    requiref90 = not not fmodule_sources or \
                 (_get(target, 'language', 'c') == 'f90')

    # save source type information so that build_ext can use it.
    source_languages = []
    if c_sources:
        source_languages.append('c')
    if cxx_sources:
        source_languages.append('c++')
    if requiref90:
        source_languages.append('f90')
    elif f_sources:
        source_languages.append('f77')
    _put(target, 'source_languages', source_languages)

    lib_file = compiler.library_filename(name, output_dir=build_directory)
    if mode == SHARED_LIBRARY:
        lib_file = compiler.library_filename(name, lib_type='shared',
                                             output_dir=build_directory)

    depends = sources + (_get(target, 'depends', []))
    if not (builder.force or newer_group(depends, lib_file, 'newer')):
        log.debug("skipping '%s' library (up-to-date)", name)
        return
    else:
        log.info("building '%s' library", name)

    if have_numpy:
        config_fc = _get(target, 'config_fc', {})
        if fcompiler is not None and config_fc:
            log.info('using additional config_fc from setup script '\
                     'for fortran compiler: %s' % (config_fc,))
            from numpy.distutils.fcompiler import new_fcompiler
            fcompiler = new_fcompiler(compiler=fcompiler.compiler_type,
                                      verbose=builder.verbose,
                                      dry_run=builder.dry_run,
                                      force=builder.force,
                                      requiref90=requiref90,
                                      c_compiler=builder.compiler)
            if fcompiler is not None:
                dist = builder.distribution
                base_config_fc = dist.get_option_dict('config_fc').copy()
                base_config_fc.update(config_fc)
                fcompiler.customize(base_config_fc)

        # check availability of Fortran compilers
        if (f_sources or fmodule_sources) and fcompiler is None:
            ver = '77'
            if requiref90:
                ver = '90'
            raise DistutilsError("target %s has Fortran%s sources" \
                                 " but no Fortran compiler found" % (name, ver))

    macros = _get(target, 'define_macros')
    include_dirs = convert_ulist(_get(target, 'include_dirs'))
    if include_dirs is None:
        include_dirs = []
    extra_postargs = _get(target, 'extra_compiler_args') or []

    if have_numpy:
        include_dirs.extend(get_numpy_include_dirs())
    # where compiled F90 module files are:
    module_dirs = _get(target, 'module_dirs', [])
    module_build_dir = os.path.dirname(lib_file)
    if requiref90:
        builder.mkpath(module_build_dir)

    if compiler.compiler_type=='msvc':
        # this hack works around the msvc compiler attributes
        # problem, msvc uses its own convention :(
        c_sources += cxx_sources
        cxx_sources = []

    objects = []
    if c_sources:
        log.info("compiling C sources")
        objects = compiler.compile(c_sources,
                                   output_dir=builder.build_temp,
                                   macros=macros,
                                   include_dirs=include_dirs,
                                   debug=builder.debug,
                                   extra_postargs=extra_postargs)

    if cxx_sources:
        log.info("compiling C++ sources")
        cxx_compiler = compiler.cxx_compiler()
        cxx_objects = cxx_compiler.compile(cxx_sources,
                                           output_dir=builder.build_temp,
                                           macros=macros,
                                           include_dirs=include_dirs,
                                           debug=builder.debug,
                                           extra_postargs=extra_postargs)
        objects.extend(cxx_objects)

    if f_sources or fmodule_sources:
        if not have_numpy:
            raise Exception("Fortran sources, but no NumPy to compile them.")
        extra_postargs = []
        f_objects = []

        if requiref90:
            if fcompiler.module_dir_switch is None:
                existing_modules = glob('*.mod')
            extra_postargs += fcompiler.module_options(
                module_dirs,module_build_dir)

        if fmodule_sources:
            log.info("compiling Fortran 90 module sources")
            f_objects += fcompiler.compile(fmodule_sources,
                                           output_dir=builder.build_temp,
                                           macros=macros,
                                           include_dirs=include_dirs,
                                           debug=builder.debug,
                                           extra_postargs=extra_postargs)

        if requiref90 and fcompiler.module_dir_switch is None:
            # move new compiled F90 module files to module_build_dir
            for f in glob('*.mod'):
                if f in existing_modules:
                    continue
                t = os.path.join(module_build_dir, f)
                if os.path.abspath(f)==os.path.abspath(t):
                    continue
                if os.path.isfile(t):
                    os.remove(t)
                try:
                    builder.move_file(f, module_build_dir)
                except DistutilsFileError:
                    log.warn('failed to move %r to %r' % (f, module_build_dir))

        if f_sources:
            log.info("compiling Fortran sources")
            f_objects += fcompiler.compile(f_sources,
                                           output_dir=builder.build_temp,
                                           macros=macros,
                                           include_dirs=include_dirs,
                                           debug=builder.debug,
                                           extra_postargs=extra_postargs)
    else:
        f_objects = []

    objects.extend(f_objects)

    # assume that default linker is suitable for
    # linking Fortran object files
    ########################################

    if _get(target, 'link_with_fcompiler', False): # if using PROGRAM
        link_compiler = fcompiler
    else:
        link_compiler = compiler
    if cxx_sources:
        link_compiler = cxx_compiler
    extra_postargs = _get(target, 'extra_link_args') or []

    ## May be dependent on other libs we're builing
    shlib_libraries = []
    for libinfo in _get(target, 'libraries', []):
        if is_string(libinfo):
            shlib_libraries.append(convert_ulist([libinfo])[0])
        else:
            shlib_libraries.append(libinfo[0])

    if mode == EXECUTABLE:
        if not hasattr(link_compiler, 'linker_exe') or \
           link_compiler.linker_exe is None:
            link_compiler.linker_exe = [link_compiler.linker_so[0]]
        target_desc = link_compiler.EXECUTABLE
    elif mode == SHARED_LIBRARY:
        target_desc = link_compiler.SHARED_LIBRARY
                

    linker_args = dict(
        target_desc          = target_desc,
        objects              = objects,
        output_filename      = target_name,
        output_dir           = build_directory,
        libraries            = shlib_libraries,
        library_dirs         = library_dirs,
        debug                = builder.debug,
        extra_preargs        = extra_preargs,
        extra_postargs       = extra_postargs,
    )
    if not _get(target, 'link_with_fcompiler', False):
        linker_args['runtime_library_dirs'] = runtime_library_dirs

    link_compiler.link(**linker_args)  # pylint: disable=W0142
