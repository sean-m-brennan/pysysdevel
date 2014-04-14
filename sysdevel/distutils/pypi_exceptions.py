"""
Copyright 2013.  Los Alamos National Security, LLC.
This material was produced under U.S. Government contract
DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which is
operated by Los Alamos National Security, LLC for the U.S. Department
of Energy. The U.S. Government has rights to use, reproduce, and
distribute this software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS
NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should be
clearly marked, so as not to confuse it with the version available
from LANL.

Licensed under the Mozilla Public License, Version 2.0 (the
"License"); you may not use this file except in compliance with the
License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/2.0/

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.
"""
# pylint: disable=W0105
"""
Packages that exist in PyPI, but are inobvious or with external deps.
Note that some PyPI listings do *not* have code on PyPI, those won't work here.
"""

## Q: what does pip do for these?
## A: nothing - tough luck if you don't know the *PyPI* name or
##     if dependencies are not listed in setup's 'requires' entry

## Dictionary organized as:
##  Package name (as used), PyPI name, dependencies
pypi_exceptions = {
    'argparse':    ('argparse', ()),  #TODO why does argparse break the dependency checker AST?
    'cython':      ('Cython', None),
    'dateutil':    ('python-dateutil', ('six',)),
    'ephem':       ('pyephem', None),
    'fuzzy':       ('Fuzzy', None),
    'jinja2':      ('Jinja2', None),
    'numba':       ('numba', ('numpy (==1.7.1)', ## due to bug in numba
                              'cython', 'llvmpy', 'llvmmath')),
    'pygments':    ('Pygments', None),

    'pyyaml':      ('PyYAML', ('libyaml',)),

    'qunitsuite':  ('QUnitSuite', None),

    'scipy':       ('scipy', ('gfortran',)), #'atlas',)), #'lapack',?)),

    'serial':      ('pyserial', None),

    'shapely':     ('Shapely', ('geos',)),
    'sphinx':      ('Sphinx', ('docutils', 'jinja2', 'pygments',
                               'roman',)), # 'rst2pdf,)), #TODO rst2pdf is broken
    'sqlalchemy':  ('SQLAlchemy', None),
    'usb':         ('pyusb', ('libusb',)),
}
