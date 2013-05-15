# -*- coding: utf-8 -*-
"""
Package specification
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
import platform

import util


class pkg_config(object):
    '''
    Package configuration class for use with sysdevel.

    To create you custom configuration:
    create a config.py module wherein you subclass this object
    (eg. 'class subclass_config(pkg_config)'),
    then create an instance of your subclass named 'pkg'
    (eg. 'pkg = subclass_config(...)').
    '''
    def __init__(self, name, package_tree,
                 pkg_id, version, author, email, website, company,
                 copyright, srcs, runscripts,
                 data_files=[], extra_data=[], req_pkgs=[], dyn_mods=[],
                 extra_pkgs=[], extra_libs=[], environ=dict(), prereq=[],
                 redistrib=[], img_dir='', build_dir='', description=''):
        if package_tree is not None:
            self.PACKAGE       = package_tree.root()
        else:
            self.PACKAGE       = name.lower()
        self.NAME              = name
        self.VERSION           = version[:version.rindex('.')]
        self.RELEASE           = version
        self.COPYRIGHT         = copyright
        self.AUTHOR            = author
        self.AUTHOR_CONTACT    = email
        self.WEBSITE           = website
        self.COMPANY           = company
        self.ID                = pkg_id
        self.PACKAGE_TREE      = package_tree
        self.DESCRIPTION       = description
        self.REQUIRED          = req_pkgs

        self.source_files      = srcs
        self.runscripts        = runscripts
        self.generated_scripts = []
        self.tests             = []
        self.package_files     = dict({self.PACKAGE: data_files})
        self.extra_data_files  = extra_data
        self.required_pkgs     = dict({self.PACKAGE: req_pkgs})
        self.dynamic_modules   = dict({self.PACKAGE: dyn_mods})
        self.logo_bmp_path     = None
        self.environment       = environ
        self.prerequisites     = prereq
        self.redistributed     = redistrib
        self.image_dir         = img_dir
        self.build_dir         = build_dir
        self.build_config      = 'release'
        self.extra_pkgs        = extra_pkgs
        self.extra_libraries   = extra_libs
        self.missing_libraries = []
        self.has_extension     = False

        if package_tree is not None:
            self.package_names = dict((tree.root(),
                                       '_'.join(list(reversed(tree.flatten()))))
                                      for tree in self.PACKAGE_TREE.inverted())
            self.names         = dict((tree.root(),
                                       '.'.join(list(reversed(tree.flatten()))))
                                      for tree in self.PACKAGE_TREE.subtrees())
            self.parents       = dict((node, self.PACKAGE_TREE.parent(node))
                                      for node in self.PACKAGE_TREE.flatten())
            self.hierarchy     = dict((tree.root(),
                                       list(reversed(tree.flatten())))
                                      for tree in self.PACKAGE_TREE.subtrees())
            self.directories   = dict((tree.root(),
                                       os.path.join(*(list(reversed(tree.flatten()))[1:]))) \
                                          for tree in self.PACKAGE_TREE.subtrees() if len(tree) > 1)
            self.directories[self.PACKAGE] = '.'
        else:
            self.package_names = dict()
            self.names         = dict()
            self.parents       = dict()
            self.hierarchy     = dict()
            self.directories   = dict()

        self.environment['PACKAGE'] = self.PACKAGE
        self.environment['NAME'] = self.NAME
        self.environment['VERSION'] = self.VERSION
        self.environment['RELEASE'] = self.RELEASE
        self.environment['COPYRIGHT'] = self.COPYRIGHT
        self.environment['AUTHOR'] = self.AUTHOR
        self.environment['COMPANY'] = self.COMPANY
        self.environment['COMPILER'] = 'gcc'


    def get_prerequisites(self, argv):
        if 'windows' in platform.system().lower():
            environ = util.read_cache()
            if 'COMPILER' in environ:
                compiler = environ['COMPILER']
            else:
                compiler = 'msvc'  ## distutils default on Windows
            for a in range(len(argv)):
                if argv[a].startswith('--compiler='):
                    compiler = argv[a][11:]
                elif argv[a] == '-c':
                    compiler = argv[a+1]
            if compiler == 'mingw32':
                self.prerequisites = ['mingw'] + self.prerequisites
            elif compiler.startswith('msvc'):
                self.prerequisites = ['msvc'] + self.prerequisites
            else:
                raise Exception("Unknown compiler specified: " + compiler)
            self.environment['COMPILER'] = compiler
        if self.environment['COMPILER'] == 'gcc':
            self.prerequisites = ['gcc'] + self.prerequisites
        return self.prerequisites, argv

    def additional_env(self, envir):
        self.environment = dict(envir.items() + self.environment.items())
        return self.environment

    def get_source_files(self, *args):
        return self.source_files

    def get_data_files(self, *args):
        return [('', self.package_files[self.PACKAGE])]

    def get_extra_data_files(self, *args):
        return self.extra_data_files

    def get_missing_libraries(self, *args):
        '''
        List of libraries for explicit inclusion in py2exe build.
        See the list of DLLs at the end of py2exe processing.
        '''
        msvcrt_extra = []
        if self.has_extension:
            msvcrt_release_path = self.environment['MSVCRT_DIR']
            msvcrt_debug_path = self.environment['MSVCRT_DEBUG_DIR']
            if self.build_config.lower() == 'debug':
                msvc_glob = os.path.join(msvcrt_debug_path, '*.*')
                sys.path.append(msvcrt_debug_path)
            else:
                msvc_glob = os.path.join(msvcrt_release_path, '*.*')
                sys.path.append(msvcrt_release_path)
            msvcrt_extra += glob.glob(msvc_glob)

        missing = []
        for lib in self.missing_libraries + msvcrt_extra:
            missing.append(lib.encode('ascii', 'ignore'))
        return missing
