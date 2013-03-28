#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find Perl headers and library
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

import os, platform

from sysdevel.util import *

environment = dict()
perl_found = False
DEBUG = False


def null():
    global environment
    environment['PERL'] = None
    environment['PERL_INCLUDE_DIR'] = None
    environment['PERL_LIB_DIR'] = None
    environment['PERL_LIBRARIES'] = []
    environment['PERL_LIBS'] = []


def is_installed(environ, version):
    global environment, perl_found
    if version is None:
        ver = '5'
    else:
        ver = version.split('.')[0]

    set_debug(DEBUG)
    base_dirs = []
    lib_ver = ''
    try:
        base_dirs.append(os.environ['PERL_CORE'])
    except:
        pass
    try:
        base_dirs.append(os.environ['PERL_ROOT'])
    except:
        pass
    if 'windows' in platform.system().lower():
        ## Strawberry Perl from http://strawberryperl.com
        base_dirs.append(os.path.join('c:', os.sep, 'strawberry', 'perl'))
        try:
            base_dirs.append(environ['MSYS_DIR'])  ## msys includes perl
        except:
            pass
    elif 'darwin' in platform.system().lower():
        base_dirs.append(os.path.join('/', 'System', 'Library', 'Perl',
                                      ver + '*', 'darwin-*'))

    try:
        perl_exe = find_program('perl', base_dirs)
        incl_dir = find_header('perl.h', base_dirs,
                               ['CORE', os.path.join('lib', 'CORE'),
                                os.path.join('perl', 'CORE'),
                                os.path.join('perl' + ver, 'CORE'),
                                os.path.join('lib', 'perl' + ver,
                                             ver + '.*', 'msys', 'CORE'),
                                ])
        lib_dir, perl_lib  = find_library('perl', base_dirs,
                                          [os.path.join('perl', 'bin'),
                                           incl_dir,])
        if 'windows' in platform.system().lower():
            lib_ver = perl_lib.split('.')[0].split('perl')[1]
        perl_found = True
    except Exception, e:
        if DEBUG:
            print e
        return perl_found

    environment['PERL'] = perl_exe
    environment['PERL_INCLUDE_DIR'] = incl_dir
    environment['PERL_LIB_DIR'] = lib_dir
    environment['PERL_LIBRARIES'] = [perl_lib]
    environment['PERL_LIBS'] = ['perl' + lib_ver]
    return perl_found


def install(environ, version, target='build', locally=True):
    if not perl_found:
        if version is None:
            version = '5.16.3'
        website = ('http://www.perl.org/',)
        if locally and not 'windows' in platform.system().lower():
            sys.stderr.write('Perl was not found, ' +
                             'but should be already installed by default.\n' +
                             'Installing locally anyway.\n')
            ## MinGW build is *not* straight-forward
            website = ('http://www.cpan.org/',
                       'src/' + version.split('.')[0] + '.0/')
            src_dir = 'perl-' + str(version)
            archive = src_dir + '.tar.gz'
            fetch(''.join(website), archive, archive)
            here = os.path.abspath(os.getcwd())
            unarchive(os.path.join(here, download_dir, archive),
                      target, src_dir)

            os.chdir(build_dir)
            subprocess.check_call(['./Configure', '-des', '-Dprefix=' + prefix])
            subprocess.check_call(['make'])
            subprocess.check_call(['make', 'install'])
            os.chdir(here)
        else:
            if 'windows' in platform.system().lower():
                website = ('http://strawberry-perl.googlecode.com/', 'files/')
                version = '5.16.2.2'
            global_install('Perl', website,
                           'strawberry-perl-' + str(version) + '-32bit.msi',
                           'perl' + str(version),
                           'libperl-dev',
                           'perl-devel')
        if not is_installed(environ, version):
            raise Exception('Perl installation failed.')
