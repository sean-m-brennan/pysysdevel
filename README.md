SysDevel
--------

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


This package requires:
  * Python 2.4 or greater (http://www.python.org)
  * NumPy (http://www.numpy.org)

Using Python 2.4 or 2.5 may also require:
      (if you are downloading over https behind a proxy)
  * httpsproxy_urllib2 (http://pypi.python.org/pypi/httpsproxy_urllib2)


Build/Install (assuming admin privileges)
  ```
  python setup.py build
  python setup.py install
  ```



The 'HACKING.generic' file lists the minimum required software that
users of *your* package (that itself uses sysdevel) will need. Include
it in your own 'HACKING' file.

For information on using sysdevel, see the manual in the
'sysdevel/docs' directory.
