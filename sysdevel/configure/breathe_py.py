#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Find Breathe
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

from sysdevel.util import *

DEPENDENCIES = [('sphinx', '1.0.7'), 'uuid',]

environment = dict()
breathe_found = False


def null():
    pass


def is_installed(environ, version):
    global environment, breathe_found
    try:
        import breathe
        ver = breathe.__version__
        if compare_versions(ver, version) == -1:
            return breathe_found
        breathe_found = True
    except:
        pass
    return breathe_found


def install(environ, version, locally=True):
    if not breathe_found:
        website = 'https://pypi.python.org/packages/source/b/breathe/'
        version = '0.7.5'  ## Force version due to 2.4 patching
        src_dir = 'breathe-' + str(version)
        archive = src_dir + '.tar.gz' 
        install_pypkg(src_dir, website, archive, locally=locally, patch=patch)
        #if not is_installed(environ, version):
        #    raise Exception('Breathe installation failed.')


def patch(src_path):
    if sys.version_info < (2, 6):
        path = os.path.join(src_path, 'breathe', '__init__.py')
        patch_file(path, '(namespace, name) if namespace else name',
                   '            display_name = "%s::%s" % (namespace, name) if namespace else name',
                   '            if namespace:\n' +
                   '                display_name = "%s::%s" % (namespace, name)\n' +
                   '            else:\n' +
                   '                display_name = name')
        patch_file(path, '(namespace, name) if namespace else name',
                   '        xml_name = "%s::%s" % (namespace, name) if namespace else name',
                   '        if namespace:\n' +
                   '            xml_name = "%s::%s" % (namespace, name)\n' +
                   '        else:\n' +
                   '            xml_name = name')
        path = os.path.join(src_path, 'breathe', 'renderer', 'rst',
                            'doxygen', 'domain.py')
        patch_file(path, 'if data_object.explicit == ',
                   '        explicit = "explicit " if data_object.explicit == "yes" else ""',
                   '        explicit = ""\n' +
                   '        if data_object.explicit == "yes":\n' +
                   '            explicit = "explicit "')
        path = os.path.join(src_path, 'breathe', 'finder',
                            'doxygen', '__init__.py')
        patch_file(path, '(name) if name else AnyMatcher()',
                   '        return NameMatcher(name) if name else AnyMatcher()',
                   '        if name:\n' +
                   '          return NameMatcher(name)\n' +
                   '        return AnyMatcher()')
        patch_file(path, '    def create_ref_matcher_stack(self, class_, ref):',
                   '    def create_ref_matcher_stack(self, class_, ref):',
                   '    def create_ref_matcher_stack(self, class_, ref):\n' +
                   '        compound = AnyMatcher()\n' +
                   '        if class_:\n' +
                   '            compound = ItemMatcher(class_, "class")')
        patch_file(path, 'ItemMatcher(class_, "class") if class_ else AnyMatcher()',
                   '                "compound" : ItemMatcher(class_, "class") if class_ else AnyMatcher(),',
                   '                "compound" : compound,')
