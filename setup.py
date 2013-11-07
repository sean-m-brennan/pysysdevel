#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build and install sysdevel
"""

import os
import sys
from distutils.core import setup

# Just in case we are being called from a different directory
cwd = os.path.dirname(__file__)
if cwd:
    os.chdir(cwd)

from sysdevel.util import rcs_revision
rev = rcs_revision()
if rev is None:
    rev = '6.12'


if not 'clean' in sys.argv:
    ## In-place build
    from sysdevel.distutils.build_org import make_doc as make_org
    from sysdevel.distutils.build_docbook import make_doc as make_docbook
        
    xml_file = make_org(os.path.join('sysdevel', 'doc', 'sysdevel_book.org'))
    try:
        make_docbook(xml_file, stylesheet='docbook_custom.xsl')
    except Exception:
        print("Could not build the manual. Requires emacs and docbook.")
        e = sys.exc_info()[1]
        print(e)

if 'docs' in sys.argv:
    argv.remove('docs')
    if len(argv) < 2:
        exit(0)

setup(name         = 'pysysdevel',
      version      = '0.' + str(rev),
      description  = 'Simulation and Model Development with Python',
      author       = 'Sean M. Brennan',
      author_email = 'brennan@lanl.gov',
      url          = 'https://github.com/sean-m-brennan/pysysdevel',
      packages     = ['sysdevel',
                      'sysdevel.distutils', 'sysdevel.distutils.configure',
                      ],
      package_data = {'sysdevel': [os.path.join('distutils',
                                                'sphinx_conf.py.in'),
                                   os.path.join('distutils',
                                                'win_postinstall.py.in'),
                                   os.path.join('doc', '*.pdf'),
                                   os.path.join('ui', '*.in'),
                                   os.path.join('ui', '*.sh'),
                                   os.path.join('ui', '*.py'),
                                   os.path.join('ui', '*.php'),
                                   os.path.join('ui', '*.js'),
                                   os.path.join('ui', '*.xrc'),
                                   ]},
      classifiers  = [
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Science/Research',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)',
          'Operating System :: POSIX',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Programming Language :: Python',
          'Programming Language :: C',
          'Programming Language :: C++',
          'Programming Language :: Fortran',
          'Topic :: Scientific/Engineering',
          'Topic :: Software Development :: Build Tools',
          ],
     )
