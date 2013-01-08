#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build and install pydevel
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
from distutils.core import setup


# Just in case we are being called from a different directory
cwd = os.path.dirname(__file__)
if cwd:
    os.chdir(cwd)


def main(argv=None):
    if argv is None:
        argv = sys.argv

    #FIXME documentation

    setup(name        = 'pydevel',
          version     = '0.5.2',
          description = 'Enhanced Python build options (based on distutils)',
          requires    = ['numpy',],
          packages    = ['pydevel', 'pydevel.config',],
          classifiers = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: Other/Proprietary License :: Official Use Only',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Topic :: Software Development :: Build Tools',
            ],
          )


if __name__ == '__main__':
    main()
