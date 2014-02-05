
import os
import sys
import platform

from ..prerequisites import programfiles_directories, find_program, system_uses_homebrew, convert2unixpath, check_call, mingw_check_call, admin_check_call, major_minor_version, global_install, ConfigError
from ..filesystem import mkdir
from ..configuration import prog_config
from .. import options

class configuration(prog_config):
    """
    Find/install GCC-XML
    """
    def __init__(self):
        prog_config.__init__(self, 'gccxml',
                             dependencies=['git', 'cmake'], debug=False)


    def is_installed(self, environ, version=None):
        options.set_debug(self.debug)
        limit = False
        base_dirs = []
        if 'GCCXML' in environ and environ['GCCXML']:
            base_dirs.append(os.path.dirname(environ['GCCXML']))
            limit = True

        if not limit:
            for d in programfiles_directories():
                base_dirs.append(os.path.join(d, 'GCC_XML'))
            try:
                base_dirs.append(environ['MINGW_DIR'])
                base_dirs.append(environ['MSYS_DIR'])
            except KeyError:
                pass
        try:
            self.environment['GCCXML'] = find_program('gccxml', base_dirs,
                                                      limit=limit)
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            if locally or ('darwin' in platform.system().lower() and
                           system_uses_homebrew()):
                here = os.path.abspath(os.getcwd())
                if locally:
                    prefix = os.path.abspath(options.target_build_dir)
                    if not prefix in options.local_search_paths:
                        options.add_local_search_path(prefix)
                else:
                    prefix = options.global_prefix
                ## MinGW shell strips backslashes
                prefix = convert2unixpath(prefix)

                src_dir = 'gccxml'
                if not os.path.exists(os.path.join(here, options.download_dir,
                                                   src_dir)):
                    os.chdir(options.download_dir)
                    gitsite = 'https://github.com/gccxml/gccxml.git'
                    check_call([environ['GIT'], 'clone', gitsite, src_dir])
                    os.chdir(here)
                build_dir = os.path.join(options.download_dir,
                                         src_dir, '_build')
                mkdir(build_dir)
                os.chdir(build_dir)
                log = open('build.log', 'w')
                if 'windows' in platform.system().lower():
                    if 'MSVC' in environ:
                        config_cmd = [environ['CMAKE'], '..',
                                      '-G', '"NMake Makefiles"',
                                      '-DCMAKE_INSTALL_PREFIX=' + prefix]
                        ##FIXME probably wrong
                        check_call([environ['MSVC_VARS']],
                                   stdout=log, stderr=log)
                        check_call(config_cmd, stdout=log, stderr=log)
                        check_call([environ['NMAKE']], stdout=log, stderr=log)
                        check_call([environ['NMAKE'], 'install'],
                                   stdout=log, stderr=log)
                    else:  ## MinGW
                        config_cmd = [environ['CMAKE'], '..',
                                      '-G', '"MSYS Makefiles"',
                                      '-DCMAKE_INSTALL_PREFIX=' + prefix,
                                      '-DCMAKE_MAKE_PROGRAM=/bin/make.exe']
                        mingw_check_call(environ, config_cmd,
                                         stdout=log, stderr=log)
                        mingw_check_call(environ, ['make'],
                                         stdout=log, stderr=log)
                        mingw_check_call(environ, ['make', 'install'],
                                         stdout=log, stderr=log)
                else:
                    config_cmd = [environ['CMAKE'], '..',
                                  '-G', 'Unix Makefiles',
                                  '-DCMAKE_INSTALL_PREFIX=' + prefix]
                    check_call(config_cmd, stdout=log, stderr=log)
                    check_call(['make'], stdout=log, stderr=log)
                    if locally:
                        check_call(['make', 'install'], stdout=log, stderr=log)
                    else:
                        admin_check_call(['make', 'install'],
                                         stdout=log, stderr=log)
                log.close()
                os.chdir(here)
            else:
                if version is None:
                    version = '0.6.0'
                website = ('http://www.gccxml.org/',
                           'files/v' + major_minor_version(version) + '/')
                global_install('GCCXML', website,
                               winstaller='gccxml-' + str(version) + '-win32.exe',
                               brew=None, port='gccxml-devel',
                               deb='gccxml', rpm='gccxml')
            if not self.is_installed(environ, version):
                raise Exception('GCC-XML installation failed.')
