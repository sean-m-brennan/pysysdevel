#!/usr/bin/env python
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
import sys
import platform
import shutil

website = 'https://github.com/sean-m-brennan/pysysdevel'
default_build_dir = 'build'
default_dnld_dir = 'third_party'

shell = False
if 'windows' in platform.system().lower():
    shell = True


def _check_call(cmd, *args, **kwargs):
    import subprocess
    p = subprocess.Popen(cmd, *args, **kwargs)
    retcode = p.wait()
    if retcode != 0:
        ex = subprocess.CalledProcessError(retcode, cmd, None)
        raise ex


def _extract_zip_archive(archive_path):
    import zipfile
    z = zipfile.ZipFile(archive_path, 'r')
    z.extractall()
    z.close()


def _import_sysdevel(where, feedback=False, force_archive=False):
    if where == '':
        where = os.path.abspath(os.getcwd())
    else:
        where = os.path.abspath(where)
    try:
        import sysdevel
    except:
        import sys
        from distutils.spawn import find_executable

        build_dir = os.path.join(where, default_build_dir)
        download_dir = os.path.join(where, default_dnld_dir)
        for arg in list(sys.argv):
            if arg == '-b' or arg == '--build_base':
                idx = sys.argv.index(arg) + 1
                build_dir = os.path.abspath(sys.argv[idx])
            if arg == '-d' or arg == '--download-dir':
                idx = sys.argv.index(arg) + 1
                download_dir = os.path.abspath(sys.argv[idx])

        if not os.path.exists(os.path.join(build_dir, 'pysysdevel')):
            if feedback:
                print('Fetching SysDevel from ' + website)
            here = os.path.abspath(os.getcwd())
            if not os.path.exists(build_dir):
                os.mkdir(build_dir)
            os.chdir(build_dir)
            archive = 'pysysdevel.zip'
            archive_path = os.path.join(here, download_dir, archive)
            if not force_archive and os.path.exists(archive_path):
                ## exists, just extract
                _extract_zip_archive(archive_path)
                os.rename('pysysdevel-master', 'pysysdevel')
            elif force_archive or find_executable('git') is None:
                ## download the archive
                if not os.path.exists(download_dir):
                    os.mkdir(download_dir)
                website_zipfile = website + '/archive/master.zip'
                if find_executable('wget') is None:
                    print("WARNING: if you are behind a proxy, " +\
                          "this download will hang.")
                    try:
                        from urllib.request import urlretrieve
                    except ImportError:
                        from urllib import urlretrieve
                    urlretrieve(website_zipfile, archive_path)
                else:  ## wget is available
                    _check_call(['wget', website_zipfile, '-O', archive_path],
                                shell=shell)
                try:
                    shutil.rmtree('pysysdevel', ignore_errors=True)
                except:
                    pass
                _extract_zip_archive(archive_path)
                os.rename('pysysdevel-master', 'pysysdevel')
            else:  ## git is available
                _check_call(['git', 'clone', website + '.git'],
                            shell=shell)
            os.chdir(here)

        sys.path.insert(0, os.path.join(build_dir, 'pysysdevel'))
        import sysdevel


def _install_sysdevel(where):
    import sys
    import shutil
    if where == '':
        where = os.path.abspath(os.getcwd())
    else:
        where = os.path.abspath(where)
    here = os.path.abspath(os.getcwd())
    os.chdir(where)
    _check_call([sys.executable, 'setup.py', 'install'], shell=shell)
    os.chdir(here)
    shutil.rmtree(where)




if __name__ == "__main__":
    print('Installing SysDevel\n')
    try:
        import sysdevel
        print('SysDevel found at ' + os.path.dirname(sysdevel.__file__))
    except:
        force_archive = False
        install = False
        where = ''
        last_idx = 0
        for arg in list(sys.argv):
            if arg == '-f' or arg == '--force':
                force_archive = True
            elif arg == '-I' or arg == '--install':
                install = True
            elif arg == '-C' or arg == '--local-dir':
                idx = sys.argv.index(arg) + 1
                where = sys.argv[idx]
            elif arg == '-h' or arg == '--help':
                print("Usage: " + +
                      " [-d | --download-dir download_dir]" +
                      " [-f | --force]" +
                      " [-I | --install]" +
                      " [-C | --local-dir user_installation_path]")

        if where == '':
            where = os.path.abspath(os.getcwd())
        _import_sysdevel(where, True, force_archive)
        if install:
            _install_sysdevel(os.path.join(where, 'pysysdevel'))
        import sysdevel
        print('SysDevel is now at ' + os.path.dirname(sysdevel.__file__))

else:
    _import_sysdevel(os.path.abspath(os.path.dirname(__file__)))
