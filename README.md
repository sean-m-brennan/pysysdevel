SysDevel
--------

TL;DR: Install with
  ```
  python -c "$(curl -fsSL https://raw.github.com/sean-m-brennan/pysysdevel/master/get_sysdevel.py)"
  ```

SysDevel is a Python package that assists software development in
three related areas: model development, data visualization, and
collaboration and distribution. This package facilitates multi-model
simulation development by implementing a generic Model-View-Controller
interface. The View portion of this interface handles data
visualization by unifying both web-based and desktop UI tools. For
package distribution, SysDevel extends the distutils package to handle
external libraries and application freezing.

All code in SysDevel is released under the Mozilla Public License 2.0
(see the 'LICENSE' file).
Copyright 2013, Los Alamos National Security, LLC (see the 'COPYING' file).


This package requires:
  * Python 2.6 or greater (http://www.python.org)

If Fortran is at all involved in your project:
  * NumPy (http://www.numpy.org)


Build/Install (assuming admin privileges)
  ```
  python setup.py build
  python setup.py install
  ```


The 'HACKING.generic' file lists the minimum required software that
users of *your* project (that itself uses sysdevel) will need. Include
it in your own 'HACKING' file.

For information on using sysdevel, see the manual in the
'sysdevel/docs' directory. (Yeah, it don't exist yet.)
