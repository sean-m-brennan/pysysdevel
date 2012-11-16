#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find/install GMAT
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

import os, sys, shutil, traceback

from pydevel.util import *

environment   = dict()
gmat_found    = False

## latest release or current svn checkout
(R2012a, SVN) = range(2)
version_strs  = {R2012a: 'R2012a', SVN: 'svn'}
version_zfill = 6

VERSION = R2012a


def is_installed():
    global environment, gmat_found
    try:
        gmat_root = os.environ['GMAT_ROOT']
        try:
            gmat_version = os.environ['GMAT_VERSION']
        except:
            try:
                import pysvn
                rev_num = pysvn.Client().info(gmat_root).revision.number
                gmat_version = 'svn-' + str(rev_num).zfill(version_zfill)
            except:
                gmat_version = 'R2012a' 
        environment['GMAT_ROOT'] = gmat_root
        environment['GMAT_VERSION'] = gmat_version
        try:
            environment['GMAT_DATA'] = os.environ['GMAT_DATA']
        except:
            ## WARNING: enforcing the svn convention on release data location
            environment['GMAT_DATA'] = os.path.join(gmat_root, 'application')
        _set_environment(gmat_root, gmat_version)
        gmat_found = True
    except Exception, e:
        pass
    return gmat_found


def install(target='build'):
    global environment

    try:
        if VERSION == SVN:
            import pysvn
            svn_repo = 'https://gmat.svn.sourceforge.net/svnroot/gmat/trunk'
            client = pysvn.Client()
            src_dir = os.path.join(target, 'gmat-svn-src')
            data_dir = os.path.join(src_dir, 'application')
            if not os.path.exists(src_dir):
                client.checkout(svn_repo, src_dir)
            rev_num = client.info(src_dir).revision.number
            ver = version_strs[VERSION] +'-'+ str(rev_num).zfill(version_zfill)
        else:
            import urllib, tarfile, zipfile
            here = os.path.abspath(os.getcwd())
            website = 'http://prdownloads.sourceforge.net/gmat/'
            ver = version_strs[VERSION]
            archive = '.zip'
            archive_dir = 'gmat-src-' + ver + '-Beta'
            data_archive_dir = 'gmat-datafiles-' + ver + '-Beta'
            src_dir = os.path.join(target, archive_dir)
            data_dir = os.path.join(target, data_archive_dir)

            download_file = archive_dir + archive
            set_downloading_file(website + download_file)
            if not os.path.exists(target):
                os.makedirs(target)
            os.chdir(target)
            if not os.path.exists(download_file):
                urllib.urlretrieve(website + download_file, download_file,
                                   reporthook=download_progress)
                sys.stdout.write('\n')
            if not os.path.exists(archive_dir):
                if archive == '.zip':
                    z = zipfile.ZipFile(download_file)
                    z.extractall()
                else:
                    tgz = tarfile.open(download_file, 'r:gz')
                    tgz.extractall()
        
            download_file = data_archive_dir + archive
            set_downloading_file(website + download_file)
            if not os.path.exists(download_file):
                urllib.urlretrieve(website + download_file, download_file,
                                   reporthook=download_progress)
                sys.stdout.write('\n')
            if not os.path.exists(data_archive_dir):
                if archive == '.zip':
                    z = zipfile.ZipFile(download_file)
                    z.extractall()
                else:
                    tgz = tarfile.open(download_file, 'r:gz')
                    tgz.extractall()
            os.chdir(here)
        environment['GMAT_VERSION'] = ver
        environment['GMAT_ROOT'] = src_dir
        environment['GMAT_DATA'] = data_dir
        _set_environment(src_dir, ver)
        print 'Using GMAT version ' + ver
    except Exception,e:
        print 'Unable to install GMAT sources: ' + str(e)
        #traceback.print_exc(file=sys.stderr)



def _do_patching(gmat_root, gmat_version):
    ## modify faulty MessageReceiver.hpp
    msg_rcvr = os.path.join(gmat_root, 'src', 'base', 'util',
                            'MessageReceiver.hpp')
    if not os.path.exists(msg_rcvr + '.orig'):
        old_file = msg_rcvr + '.orig'
        os.rename(msg_rcvr, old_file)
        old = open(old_file, 'r')
        new = open(msg_rcvr, 'w')
        for line in old:
            if not 'GmatGlobal' in line:
                new.write(line)
        old.close()
        new.close()


def _is_lib_dir(parent, name):
    return name != 'include' and not 'svn' in name and not 'CVS' in name \
        and not 'cvs' in name and os.path.isdir(os.path.join(parent, name))


def _set_environment(gmat_root, gmat_version):
    global environment

    _do_patching(gmat_root, gmat_version)

    excludes = ['Spice*.?pp', 'SPKPropagator.?pp',
                'RunSimulator.?pp', 'OpenGlPlot.?pp',
                'SocketServer.?pp', 'Cowell.?pp', 'TableTemplate.?pp',
                'ArrayTemplate.?pp',
                ]

    environment['GMAT_PLUGIN_DIR'] = os.path.join(gmat_root, 'plugins')
    environment['GMAT_SRC_DIR'] = os.path.join(gmat_root, 'src')
    environment['GMAT_DATA_DIRS'] = []

    ## C Interface
    environment['GMAT_C_DIR'] = os.path.join(environment['GMAT_PLUGIN_DIR'],
                                             'CInterfacePlugin', 'src')
    environment['GMAT_C_INCLUDE_DIRS'] = [
        os.path.join(environment['GMAT_C_DIR'], 'include'),
        os.path.join(environment['GMAT_C_DIR'], 'command'),
        os.path.join(environment['GMAT_C_DIR'], 'factory'),
        os.path.join(environment['GMAT_C_DIR'], 'plugin'),
        ]
    environment['GMAT_C_EXT_HEADERS'] = [
        os.path.join(environment['GMAT_C_DIR'],
                     'command', 'PrepareMissionSequence.hpp'),
        os.path.join(environment['GMAT_C_DIR'],
                     'factory', 'CCommandFactory.hpp'),
        os.path.join(environment['GMAT_C_DIR'],
                     'plugin', 'CInterfacePluginFunctions.hpp'),
        os.path.join(environment['GMAT_C_DIR'],
                     'include', 'GmatCFunc_defs.hpp'),
        os.path.join(environment['GMAT_SRC_DIR'],
                     'base', 'include', 'gmatdefs.hpp'),
        ]
    environment['GMAT_C_EXT_SOURCES'] = [
        os.path.join(environment['GMAT_C_DIR'],
                     'command', 'PrepareMissionSequence.cpp'),
        os.path.join(environment['GMAT_C_DIR'],
                     'factory', 'CCommandFactory.cpp'),
        os.path.join(environment['GMAT_C_DIR'],
                     'plugin', 'CInterfacePluginFunctions.cpp'),
         ]

    ## Console
    environment['GMAT_CONSOLE_DIR'] = os.path.join(environment['GMAT_SRC_DIR'],
                                                   'console')
    environment['GMAT_CONSOLE_HEADERS'] = [
        os.path.join(environment['GMAT_SRC_DIR'],
                     'console', 'ConsoleAppException.hpp'),
        os.path.join(environment['GMAT_SRC_DIR'],
                     'console', 'ConsoleMessageReceiver.hpp'),
        os.path.join(environment['GMAT_SRC_DIR'],
                     'console', 'driver.hpp'),
        os.path.join(environment['GMAT_SRC_DIR'],
                     'console', 'PrintUtility.hpp'),
        os.path.join(environment['GMAT_SRC_DIR'],
                     'base', 'include', 'gmatdefs.hpp'),
        ]
    environment['GMAT_CONSOLE_EXTRA_SOURCES'] = [
        os.path.join(environment['GMAT_SRC_DIR'],
                     'console', 'PrintUtility.cpp'),
        os.path.join(environment['GMAT_SRC_DIR'],
                     'console', 'ConsoleMessageReceiver.cpp'),
    ]
    environment['GMAT_CONSOLE_SOURCES'] = [
        os.path.join(environment['GMAT_SRC_DIR'],
                     'console', 'driver.cpp'),
        os.path.join(environment['GMAT_SRC_DIR'],
                     'console', 'ConsoleAppException.cpp'),
    ] + environment['GMAT_CONSOLE_EXTRA_SOURCES']

    ## Base
    base_dir = os.path.join(environment['GMAT_SRC_DIR'], 'base')
    environment['GMAT_BASE_DIR'] = base_dir
    dirs = []
    environment['GMAT_BASE_LIBS'] = [name for name in os.listdir(base_dir)
                                     if _is_lib_dir(base_dir, name)]
    environment['GMAT_BASE_INCLUDE_DIRS'] = [os.path.join(base_dir, 'include'),]
    #if gmat_version == 'R2012a' or \
    #        gmat_version >= 'svn-' + '9623'.zfill(version_zfill):
    #    environment['GMAT_BASE_INCLUDE_DIRS'] += [
    #        os.path.join(base_dir, 'forcemodel', 'harmonic'),]
    base_srcs = []
    base_hdrs = []
    for lib in environment['GMAT_BASE_LIBS']:
        include_dirs = [os.path.join(base_dir, lib)]
        environment['GMAT_BASE_' + lib + '_HDRS'] = []
        for root, dirnames, filenames in os.walk(os.path.join(base_dir, lib)):
            for filename in fnmatch.filter(filenames, '*.cpp'):
                exclude = False
                for pattern in excludes:
                    if fnmatch.fnmatch(filename, pattern):
                        exclude = True
                if not exclude:
                    base_srcs.append(os.path.join(root, filename))
            for filename in fnmatch.filter(filenames, '*.hpp'):
                exclude = False
                for pattern in excludes:
                    if fnmatch.fnmatch(filename, pattern):
                        exclude = True
                if not exclude:
                    path = os.path.join(root, filename)
                    if not root in include_dirs:
                        include_dirs += [root]
                    environment['GMAT_BASE_' + lib + '_HDRS'].append(path)
                    base_hdrs.append(path)
        environment['GMAT_BASE_INCLUDE_DIRS'] += include_dirs
    base_srcs.append(os.path.join(base_dir, 'solarsys', 'msise90_sub.for'))
    environment['GMAT_BASE_HDRS'] = base_hdrs
    environment['GMAT_BASE_SRCS'] = base_srcs

    ## Plugins
    environment['GMAT_PLUGINS'] = ['EphemPropagator', 'Estimation',
                                   'FminconOptimizer',]  ## ignore Matlab
    plugin_dir = environment['GMAT_PLUGIN_DIR']
    for plugin in environment['GMAT_PLUGINS']:
        plugin_srcs = []
        plugin_hdrs = []
        include_dirs = [os.path.join(plugin_dir, plugin + 'Plugin', 'src')]
        for root, dirnames, filenames in os.walk(include_dirs[0]):
            for filename in fnmatch.filter(filenames, '*.cpp'):
                exclude = False
                for pattern in excludes:
                    if fnmatch.fnmatch(filename, pattern):
                        exclude = True
                if not exclude:
                    plugin_srcs.append(os.path.join(root, filename))
            for filename in fnmatch.filter(filenames, '*.hpp'):
                exclude = False
                for pattern in excludes:
                    if fnmatch.fnmatch(filename, pattern):
                        exclude = True
                if not exclude:
                    path = os.path.join(root, filename)
                    if not root in include_dirs:
                        include_dirs += [root]
                    plugin_hdrs.append(path)
        environment['GMAT_' + plugin + '_INCLUDE_DIRS'] = include_dirs
        environment['GMAT_' + plugin + '_HDRS'] = plugin_hdrs
        environment['GMAT_' + plugin + '_SRCS'] = plugin_srcs



    ## GUI
    gui_dir = os.path.join(environment['GMAT_SRC_DIR'], 'gui')
    environment['GMAT_GUI_DIR'] = gui_dir
    environment['GMAT_GUI_LIBS'] = [name for name in os.listdir(gui_dir)
                                     if _is_lib_dir(gui_dir, name)]
    gui_include = os.path.join(gui_dir, 'include')
    environment['GMAT_GUI_INCLUDE_DIRS'] = [gui_include]
    for sub in os.listdir(gui_include):
        if _is_lib_dir(gui_include, sub):
            environment['GMAT_GUI_INCLUDE_DIRS'] += [os.path.join(gui_include,
                                                                  sub)]
    gui_srcs = []
    gui_hdrs = []
    for lib in environment['GMAT_GUI_LIBS']:
        environment['GMAT_GUI_INCLUDE_DIRS'] += [os.path.join(gui_dir, lib)]
        for root, dirnames, filenames in os.walk(os.path.join(gui_dir, lib)):
            for filename in fnmatch.filter(filenames, '*.cpp'):
                exclude = False
                for pattern in excludes:
                    if fnmatch.fnmatch(filename, pattern):
                        exclude = True
                if not exclude:
                    gui_srcs.append(os.path.join(root, filename))
            for filename in fnmatch.filter(filenames, '*.hpp'):
                exclude = False
                for pattern in excludes:
                    if fnmatch.fnmatch(filename, pattern):
                        exclude = True
                if not exclude:
                    gui_hdrs.append(os.path.join(root, filename))
    environment['GMAT_GUI_HDRS'] = gui_hdrs
    environment['GMAT_GUI_SRCS'] = gui_srcs


    environment['GMAT_INCLUDE_DIRS'] = environment['GMAT_BASE_INCLUDE_DIRS'] + \
        environment['GMAT_GUI_INCLUDE_DIRS'] 
