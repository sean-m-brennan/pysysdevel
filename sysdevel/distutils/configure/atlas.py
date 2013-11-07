
import platform

from ..prerequisites import *
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install ATLAS library (includes libblas)
    """
    def __init__(self):
        lib_config.__init__(self, "atlas", "atlas_type.h", debug=False)


    def install(self, environ, version, locally=True):
        global local_search_paths
        if not self.found:
            if version is None:
                version = '3.10.1'
            website = ('http://downloads.sourceforge.net/project/math-atlas/',
                       'Stable/' + version + '/',)
            if locally or 'windows' in platform.system().lower():
                ## NB: broken on Windows!
                src_dir = 'atlas'
                archive = src_dir + str(version) + '.tar.bz2'

                here = os.path.abspath(os.getcwd())
                fetch(''.join(website), archive, archive)
                unarchive(archive, src_dir)

                if locally:
                    prefix = os.path.abspath(target_build_dir)
                    if not prefix in local_search_paths:
                        local_search_paths.append(prefix)
                else:
                    prefix = global_prefix
                prefix = convert2unixpath(prefix)  ## MinGW shell strips backslashes

                build_dir = os.path.join(target_build_dir, src_dir, '_build')
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
                global_install('ATLAS', website,
                               ## part of XCode
                               deb='libatlas-dev', rpm='atlas-devel')
            if not self.is_installed(environ, version):
                raise Exception('ATLAS installation failed.')
