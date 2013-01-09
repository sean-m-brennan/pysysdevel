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

from pydevel.util import *

environment = dict()
pyjamas_found = False

NEWEST = True


def null():
    global environment
    environment['PYJAMAS_ROOT'] = None
    environment['PYJSBUILD_EXECUTABLE'] = None


def is_installed(version=None):
    global environment, pyjamas_found
    try:
        pyjamas_root = os.environ['PYJAMAS_ROOT']
        environment['PYJAMAS_ROOT'] = pyjamas_root
        pyjs_bin = os.path.join(pyjamas_root, 'bin')
        pyjs_lib = os.path.join(pyjamas_root, 'build', 'lib')
        environment['PYJSBUILD_EXECUTABLE'] = find_program('pyjsbuild',
                                                           [pyjs_bin])
        sys.path.insert(0, pyjs_lib)
        pyjamas_found = True
    except:
        try:
            import pyjs
            environment['PYJSBUILD_EXECUTABLE'] = find_program('pyjsbuild')
            pyjamas_found = True
        except:
            pass
    return pyjamas_found


def install(target='build', version=None):
    global environment
    if not pyjamas_found:
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        try:
            import tarfile, zipfile, subprocess
            if NEWEST:
                if version is None:
                    version = '0.8.1a'
                website = 'https://github.com/pyjs/pyjs/zipball/0.8.1a'
                download_file = ''
                archive = 'pyjs-' + version + '.zip'
            else:
                if version is None:
                    version = '0.8.1~+alpha'
                website = 'http://downloads.sourceforge.net/project/pyjamas/pyjamas/' + version[:5] + '/'
                download_file = 'pyjamas-' + version + '.tar.gz'
                archive = download_file
            environment['PYJAMAS_VERSION'] = version
            here = os.path.abspath(os.getcwd())
            set_downloading_file(archive)
            if not os.path.exists(target):
                os.makedirs(target)
            download_path = os.path.abspath(os.path.join(download_dir, archive))
            if not os.path.exists(download_path):
                urlretrieve(website + download_file, download_path,
                            download_progress)
            working_dir = os.path.abspath(os.path.join(target,
                                                       'pyjamas-' + version))
            if not os.path.exists(working_dir):
                os.chdir(target)
                if download_path[-3:] == 'zip':
                    z = zipfile.ZipFile(download_path, 'r')
                    z.extractall()
                    os.rename(z.namelist()[0], 'pyjamas-' + version)
                else:
                    z = tarfile.open(download_path, 'r:gz')
                    z.extractall()

            os.chdir(working_dir)
            if os.path.exists(os.path.join('library',
                                           'HTTPRequest.browser.py')):
                patch_file(os.path.join('library', 'HTTPRequest.browser.py'),
                           'onProgress', 'localHandler', 'handler')
            elif os.path.exists(os.path.join('library', 'pyjamas', 
                                           'HTTPRequest.browser.py')):
                patch_file(os.path.join('library', 'pyjamas', 
                                        'HTTPRequest.browser.py'),
                           'onProgress', 'localHandler', 'handler')

            log_file = 'pyjamas.log'
            log = open(log_file, 'w')
            cmd_line = ['python', 'bootstrap.py',]
            sys.stdout.write('PREREQUISITE pyjamas ')
            try:
                p = subprocess.Popen(cmd_line, stdout=log, stderr=log)
                status = process_progress(p)
            except KeyboardInterrupt,e:
                p.terminate()
                log.close()
                raise e
            if status != 0:
                log.close()
                sys.stdout.write(' failed; See ' + log_file + '\n')
                raise Exception('Pyjamas is required, but could not be ' +
                                'installed locally; See ' + log_file)

            cmd_line = ['python', 'run_bootstrap_first_then_setup.py', 'build']
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
                raise Exception('Pyjamas is required, but could not be ' +
                                'installed locally; See ' + log_file)
            sys.stdout.write(' done\n')
            os.chdir(here)
            environment['PYJAMAS_ROOT'] = working_dir
            environment['PYJSBUILD_EXECUTABLE'] = find_program('pyjsbuild',
                                                               [working_dir])
            sys.path.insert(0, os.path.join(working_dir, 'build', 'lib'))
        except Exception,e:
            raise Exception('Unable to install Pyjamas: ' + str(e))
