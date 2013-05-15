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


def main(argv=None):
    if argv is None:
        argv = sys.argv

    setup(name         = 'sysdevel',
          version      = '0.5.2',
          description  = 'Simulation and Model Development with Python',
          author       = 'Sean M. Brennan',
          author_email = 'brennan@lanl.gov',
          url          = 'https://github.com/pysysdevel',
          packages     = ['sysdevel', 'sysdevel.configure',],
          package_data = {'sysdevel': ['sphinx_conf.py.in',
                                       'win_postinstall.py.in',
                                       os.path.join('doc', '*.pdf'),
                                       os.path.join('support', '*.in'),
                                       os.path.join('support', '*.sh'),
                                       os.path.join('support', '*.php'),
                                       os.path.join('support', '*.js'),
                                       os.path.join('support', '*.xrc'),
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


if __name__ == '__main__':
    main()
