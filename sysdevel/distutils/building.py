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
import fnmatch
import time

from ..util import is_string
from .filesystem import mkdir
from . import options


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
        os.chmod(dst_file, int('777', 8))
    return dst_file


def create_runscript(pkg, mod, target, extra):
    if not os.path.exists(target):
        if extra is None:
            extra = ''
        if options.DEBUG:
            print('Creating runscript ' + target)
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
