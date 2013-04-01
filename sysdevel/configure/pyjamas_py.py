#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install Pyjamas
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

from sysdevel.util import *

environment = dict()
pyjamas_found = False
DEBUG = False


def null():
    global environment
    environment['PYJSBUILD'] = None


def is_installed(environ, version):
    global environment, pyjamas_found
    set_debug(DEBUG)
    try:
        pyjamas_root = os.environ['PYJAMAS_ROOT']
        pyjs_bin = os.path.join(pyjamas_root, 'bin')
        pyjs_lib = os.path.join(pyjamas_root, 'build', 'lib')
        environment['PYJSBUILD'] = find_program('pyjsbuild', [pyjs_bin])
        sys.path.insert(0, pyjs_lib)
        pyjamas_found = True
    except Exception, e:
        if DEBUG:
            print e
        try:
            import pyjs
            environment['PYJSBUILD'] = find_program('pyjsbuild')
            pyjamas_found = True
        except Exception, e:
            if DEBUG:
                print e
    return pyjamas_found


def install(environ, version, locally=True):
    global environment
    if not pyjamas_found:
        if version is None:
            version = '0.8.1a'
        website = 'https://github.com/pyjs/pyjs/zipball/0.8.1a'
        archive = 'pyjs-' + version + '.zip'
        src_dir = 'pyjamas-' + version
        fetch(website, '', archive)
        unarchive(archive, src_dir)

        working_dir = os.path.join(target_build_dir, src_dir)
        if not os.path.exists(working_dir):
            os.rename(glob.glob(os.path.join(target_build_dir, '*pyjs*'))[0],
                      working_dir)

        ## Unique two-step installation
        log_file = os.path.join(target_build_dir, 'pyjamas.log')
        log = open(log_file, 'w')
        sys.stdout.write('PREREQUISITE pyjamas ')
        here = os.path.abspath(os.getcwd())
        os.chdir(working_dir)

        cmd_line = [sys.executable, 'bootstrap.py',]
        try:
            p = subprocess.Popen(cmd_line, stdout=log, stderr=log)
            status = process_progress(p)
        except KeyboardInterrupt,e:
            p.terminate()
            log.close()
            raise e
        check_install(status, log, log_file)

        cmd_line = [sys.executable, 'run_bootstrap_first_then_setup.py', 'build']
        if not locally:
            sudo_prefix = []
            if not as_admin():
                sudo_prefix = ['sudo']
            cmd_line = sudo_prefix + cmd_line + ['install']
        try:
            p = subprocess.Popen(cmd_line, stdout=log, stderr=log)
            status = process_progress(p)
            log.close()
        except KeyboardInterrupt,e:
            p.terminate()
            log.close()
            raise e
        check_install(status, log, log_file)

        sys.stdout.write(' done')
        os.chdir(here)
        search_path = []
        if locally:
            search_path.append(working_dir)
            sys.path.insert(0, os.path.join(working_dir, 'build', 'lib'))
        environment['PYJSBUILD'] = find_program('pyjsbuild', search_path)



def check_install(status, log, log_file):
    if status != 0:
        log.close()
        sys.stdout.write(' failed; See ' + log_file)
        raise Exception('Pyjamas is required, but could not be ' +
                        'installed; See ' + log_file)
