#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find F2C
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

from sysdevel.util import *

environment = dict()
f2c_found = False

USING_GFORTRAN = True #FIXME detect?

def null():
    global environment
    environment['F2C_INCLUDE_DIR'] = None


def is_installed(version=None):
    global environment, f2c_found
    ## look for it
    try:
        incl_dir = find_header('f2c.h')
        environment['F2C_INCLUDE_DIR'] = incl_dir
        if not USING_GFORTRAN:
            try:
                environment['F2C_LIB_DIR'], lib = find_library('g2c')
            except:
                environment['F2C_LIB_DIR'], lib = find_library('f2c')
            environment['F2C_LIBRARY'] = lib
        f2c_found = True
    except Exception,e:
        f2c_found = False
    return f2c_found


def install(target='build', version=None):
    global environment

    website = 'http://www.netlib.org/f2c/'
    here = os.path.abspath(os.getcwd())
    abs_target = os.path.abspath(target)
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    if not os.path.exists(target):
        os.makedirs(target)
    if not f2c_found:
        try:
            import tarfile, shutil
            download_file = 'f2c.h'
            set_downloading_file(download_file)
            if not os.path.exists(os.path.join(download_dir, download_file)):
                urlretrieve(website + download_file,
                            os.path.join(download_dir, download_file),
                            download_progress)
                sys.stdout.write('\n')
            shutil.copy(os.path.join(download_dir, download_file), target)
            environment['F2C_INCLUDE_DIR'] = target

            if not USING_GFORTRAN:
                import subprocess
                website += 'src/'
                f2c_srcs = ['cds.c', 'data.c', 'defines.h', 'defs.h', 'equiv.c',
                            'error.c', 'exec.c', 'expr.c', 'f2c.1', 'f2c.1t',
                            'f2c.h', 'format.c', 'format.h', 'formatdata.c',
                            'ftypes.h', 'gram.c', 'gram.dcl', 'gram.exec',
                            'gram.expr', 'gram.head', 'gram.io', 'init.c',
                            'intr.c', 'io.c', 'iob.h', 'lex.c', 'machdefs.h',
                            'main.c', 'makefile.u', 'makefile.vc', 'malloc.c',
                            'mem.c', 'memset.c', 'misc.c', 'mkfile.plan9',
                            'names.c', 'names.h', 'niceprintf.c',
                            'niceprintf.h', 'notice', 'output.c', 'output.h',
                            'p1defs.h', 'p1output.c', 'parse.h', 'parse_args.c',
                            'pccdefs.h', 'pread.c', 'proc.c', 'put.c',
                            'putpcc.c', 'sysdep.c', 'sysdep.h', 'sysdeptest.c',
                            'tokens', 'tokdefs.h', 'usignal.h', 'vax.c',
                            'version.c', 'xsum.c', 'xsum0.out', 'readme',]
                f2c_dir = os.path.join(download_dir, 'f2c')
                if not os.path.exists(f2c_dir):
                    os.makedirs(f2c_dir)
                os.chdir(f2c_dir)
                for src in f2c_srcs:
                    set_downloading_file(src)
                    if not os.path.exists(src):
                        urlretrieve(website + src, src, download_progress)
                        sys.stdout.write('\n')
                os.chdir(here)
                f2c_build_dir = os.path.join(target, 'f2c')
                shutil.copytree(f2c_dir, f2c_build_dir)
                os.chdir(f2c_build_dir)
                if 'windows' in platform.system().lower():
                    ## TODO only for MSVC
                    shutil.copy('makefile.vc', 'makefile')
                    subprocess.check_call(['nmake'])  # TODO log output
                else:
                    shutil.copy('makefile.u', 'makefile')
                    subprocess.check_call(['make'])  # TODO log output
                environment['F2C_LIB_DIR'] = f2c_build_dir      
                environment['F2C_LIBRARY'] = find_library('f2c',
                                                          [f2c_build_dir],
                                                          limit=True)
                os.chdir(here)
        except Exception, e:
            os.chdir(here)
            raise Exception('F2C not found. (include=' +
                            str(environment['F2C_INCLUDE_DIR']) + ') ' + str(e))
