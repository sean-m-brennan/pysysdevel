
import os
import platform

from ..prerequisites import convert2unixpath, mingw_check_call, check_call, admin_check_call, global_install
from ..fetching import fetch, unarchive
from ..filesystem import mkdir
from ..configuration import lib_config
from .. import options


class configuration(lib_config):
    """
    Find/install ATLAS library (includes libblas)
    """
    def __init__(self):
        lib_config.__init__(self, "atlas", "atlas_type.h", debug=False)


    def download(self, environ, version, strict=False):
        if version is None:
            version = '3.10.1'
        website = 'http://downloads.sourceforge.net/project/math-atlas/' + \
                  'Stable/' + version + '/'
        src_dir = 'atlas'
        archive = src_dir + str(version) + '.tar.bz2'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if locally or 'windows' in platform.system().lower():
                ## NB: broken on Windows!
                src_dir = self.download(environ, version, strict)
                here = os.path.abspath(os.getcwd())
                if locally:
                    prefix = os.path.abspath(options.target_build_dir)
                    if not prefix in options.local_search_paths:
                        options.add_local_search_path(prefix)
                else:
                    prefix = options.global_prefix
                prefix = convert2unixpath(prefix)  ## MinGW shell strips backslashes
                build_dir = os.path.join(options.target_build_dir,
                                         src_dir, '_build')
                mkdir(build_dir)
                os.chdir(build_dir)
                log = open('build.log', 'w')
                if 'windows' in platform.system().lower():
                    # Assumes MinGW present, detected, and loaded in environment
                    mingw_check_call(environ, ['../configure',
                                               '--prefix="' + prefix + '"',
                                               '--shared', #'-O ',
                                               '-b 32', '-Si nocygin 1'],
                                     stdout=log, stderr=log)
                    mingw_check_call(environ, ['make'], stdout=log, stderr=log)
                    mingw_check_call(environ, ['make', 'install'],
                                     stdout=log, stderr=log)
                else:
                    check_call(['../configure', '--prefix=' + prefix,
                                '--shared'], stdout=log, stderr=log)
                    check_call(['make'], stdout=log, stderr=log)
                    if locally:
                        check_call(['make', 'install'], stdout=log, stderr=log)
                    else:
                        admin_check_call(['make', 'install'],
                                         stdout=log, stderr=log)
                log.close()
                os.chdir(here)
            else:
                global_install('ATLAS', None,
                               ## part of XCode
                               deb='libatlas-dev', rpm='atlas-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('ATLAS installation failed.')
