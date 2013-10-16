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

"""
Fetch pysysdevel if neccessary.
This is mainly intended for users who want to keep the sysdevel package *out*
 of their default site-packages.
Either import this script, or fetch/install sysdevel by running:
`python -c "$(curl -fsSL https://raw.github.com/sean-m-brennan/pysysdevel/master/get_sysdevel.py)"`
"""

import os
import platform

website = 'https://github.com/sean-m-brennan/pysysdevel'

shell = False
if 'windows' in platform.system().lower():
    shell = True


def _import_sysdevel(where, feedback=False):
    if where == '':
        where = os.getcwd()
    else:
        where = os.path.abspath(where)
    try:
        import sysdevel
    except:
        import sys
        import subprocess
        from distutils.spawn import find_executable

        if not os.path.exists(os.path.join(where, 'pysysdevel')):
            if feedback:
                print('Fetching SysDevel from ' + website)
            here = os.path.abspath(os.getcwd())
            os.chdir(where)
            if find_executable('git') is None:
                import zipfile
                website_zipfile = website + '/archive/master.zip'
                archive = 'pysysdevel.zip'
                if not os.path.exists(archive):
                    if find_executable('wget') is None:
                        print("WARNING: if you are behind a proxy, " +\
                            "this download will hang.")
                        try:
                            from urllib.request import urlretrieve
                        except ImportError:
                            from urllib import urlretrieve
                        urlretrieve(website_zipfile, archive)
                    else:  ## wget is available
                        subprocess.check_call(['wget', website_zipfile,
                                               '-O', archive], shell=shell)
                z = zipfile.ZipFile(archive, 'r')
                z.extractall()
                z.close()
                os.rename('pysysdevel-master', 'pysysdevel')
            else:  ## git is available
                subprocess.check_call(['git', 'clone', website + '.git'],
                                      shell=shell)
            os.chdir(here)

        sys.path.insert(0, os.path.join(where, 'pysysdevel'))
        import sysdevel


def _install_sysdevel(where):
    import sys
    import shutil
    import subprocess
    if where == '':
        where = os.getcwd()
    else:
        where = os.path.abspath(where)
    here = os.path.abspath(os.getcwd())
    os.chdir(where)
    subprocess.check_call([sys.executable, 'setup.py', 'install'], shell=shell)
    os.chdir(here)
    shutil.rmtree(where)




if __name__ == "__main__":
    print('Installing SysDevel\n')
    try:
        import sysdevel
        print('SysDevel found at ' + os.path.dirname(sysdevel.__file__))
    except:
        print('Enter the full path where you want SysDevel to reside locally')
        msg = '    or just hit enter if you are going to install it globally:'
        try:
            where = raw_input(msg)
        except NameError:
            where = eval(input(msg))
        _import_sysdevel(where, True)
        msg2 = 'Do you want to install SysDevel into your default ' + \
               'Python site-packages? (y/N):'
        try:
            which = raw_input(msg2)
        except NameError:
            which = eval(input(msg2))
        if which.lower() == 'y' or which.lower() == 'yes':
            _install_sysdevel(os.path.join(where, 'pysysdevel'))
        import sysdevel
        print('SysDevel is now at ' + os.path.dirname(sysdevel.__file__))

else:
    _import_sysdevel(os.path.abspath(os.path.dirname(__file__)))
