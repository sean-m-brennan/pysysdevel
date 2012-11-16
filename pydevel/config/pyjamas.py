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


def is_installed():
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


def install(target='build'):
    global environment
    if not pyjamas_found:
        ## easy_install does not install pyjsbuild
        try:
            import urllib, tarfile, subprocess
            ## TODO: latest download
            #website = 'https://github.com/pyjs/pyjs/archive'
            #ver = '0.8.1a'
            website = 'http://prdownloads.sourceforge.net/pyjamas/'
            ver = '0.8.1~+alpha'
            environment['PYJAMAS_VERSION'] = ver
            here = os.path.abspath(os.getcwd())
            #download_file = 'pyjs-master.tar.gz'
            download_file = 'pyjamas-' + ver + '.tar.gz'
            set_downloading_file(website + download_file)
            if not os.path.exists(target):
                os.makedirs(target)
            os.chdir(target)
            if not os.path.exists(download_file):
                urllib.urlretrieve(website + download_file, download_file,
                                   download_progress)
            z = tarfile.open(download_file, 'r:gz')
            z.extractall()
            os.chdir(here)
            working_dir = os.path.join(target, 'pyjamas-' + ver)
            os.chdir(working_dir)
            util.patch_file('library/HTTPRequest.browser.py',
                            'onProgress', 'localHandler', 'handler')
            cmd_line = ['python', 'bootstrap.py',]
            status = subprocess.call(cmd_line)
            if status != 0:
                raise Exception("Command '" + str(cmd_line) +
                                "' returned non-zero exit status "
                                + str(status))
            cmd_line = ['python', 'run_bootstrap_first_then_setup.py', 'build']
            status = subprocess.call(cmd_line)
            if status != 0:
                raise Exception("Command '" + str(cmd_line) +
                                "' returned non-zero exit status "
                                + str(status))
            os.chdir(here)
            environment['PYJAMAS_ROOT'] = working_dir
            environment['PYJSBUILD_EXECUTABLE'] = find_program('pyjsbuild',
                                                               [working_dir])
            sys.path.insert(0, os.path.join(working_dir, 'build', 'lib'))
        except Exception,e:
            raise Exception('Unable to install Pyjamas: ' + str(e))
