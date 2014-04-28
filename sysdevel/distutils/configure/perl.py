
import os
import sys
import platform

from sysdevel.distutils.prerequisites import find_program, find_header, find_library, check_call, global_install, ConfigError
from sysdevel.distutils.configuration import lib_config
from sysdevel.distutils.fetching import fetch, unarchive
from sysdevel.distutils. import options

class configuration(lib_config):
    """
    Find/install Perl interpreter, headers and library
    """
    def __init__(self):
        lib_config.__init__(self, "perl", "perl.h", debug=False)


    def is_installed(self, environ, version=None, strict=False):
        if version is None:
            ver = '5'
        else:
            ver = version.split('.')[0]

        options.set_debug(self.debug)
        lib_ver = ''
        base_dirs = []
        limit = False
        if 'PERL_LIB_DIR' in environ and environ['PERL_LIB_DIR']:
            base_dirs.append(environ['PERL_LIB_DIR'])
            limit = True
            if 'PERL_INCLUDE_DIR' in environ and environ['PERL_INCLUDE_DIR']:
                base_dirs.append(environ['PERL_INCLUDE_DIR'])

        if not limit:
            try:
                base_dirs += os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
                base_dirs += os.environ['CPATH'].split(os.pathsep)
            except KeyError:
                pass
            try:
                base_dirs.append(os.environ['PERL_CORE'])
            except KeyError:
                pass
            try:
                base_dirs.append(os.environ['PERL_ROOT'])
            except KeyError:
                pass
            if 'windows' in platform.system().lower():
                ## Strawberry Perl from http://strawberryperl.com
                base_dirs.append(os.path.join('C:', os.sep,
                                              'strawberry', 'perl'))
                try:
                    base_dirs.append(environ['MSYS_DIR'])  ## msys includes perl
                except KeyError:
                    pass
            elif 'darwin' in platform.system().lower():
                base_dirs.append(os.path.join('/', 'System', 'Library', 'Perl',
                                              ver + '*', 'darwin-*'))

        try:
            perl_exe = find_program('perl', base_dirs)
            incl_dir = find_header(self.hdr, base_dirs,
                                   ['CORE', os.path.join('lib', 'CORE'),
                                    os.path.join('perl', 'CORE'),
                                    os.path.join('perl' + ver, 'CORE'),
                                    os.path.join('lib', 'perl' + ver,
                                                 ver + '.*', 'msys', 'CORE'),
                                    ])
            lib_dir, perl_lib  = find_library(self.lib, base_dirs,
                                              [os.path.join('perl', 'bin'),
                                               incl_dir,])
            if 'windows' in platform.system().lower():
                lib_ver = perl_lib[0].split('.')[0].split('perl')[1]
            self.found = True
        except ConfigError:
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        self.environment['PERL'] = perl_exe
        self.environment['PERL_INCLUDE_DIR'] = incl_dir
        self.environment['PERL_LIB_DIR'] = lib_dir
        self.environment['PERL_LIBRARIES'] = ['perl' + lib_ver]
        self.environment['PERL_LIB_FILES'] = [perl_lib]
        return self.found


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if version is None:
                version = '5.16.3'
            website = ('http://www.perl.org/',)
            if locally and not 'windows' in platform.system().lower():
                sys.stderr.write('Perl was not found, ' +
                                 'but should be already installed by default.' +
                                 '\nInstalling locally anyway.\n')
                ## MinGW build is *not* straight-forward - hence not implemented
                website = ('http://www.cpan.org/',
                           'src/' + version.split('.')[0] + '.0/')
                src_dir = 'perl-' + str(version)
                archive = src_dir + '.tar.gz'
                fetch(''.join(website), archive, archive)
                unarchive(archive, src_dir)

                if locally:
                    prefix = os.path.abspath(options.target_build_dir)
                    if not prefix in options.local_search_paths:
                        options.add_local_search_path(prefix)
                else:
                    prefix = options.global_prefix
                here = os.path.abspath(os.getcwd())
                os.chdir(options.target_build_dir)
                log = open('build.log', 'w')
                check_call(['./Configure', '-des',
                            '-Dprefix=' + prefix],
                           stdout=log, stderr=log)
                check_call(['make'], stdout=log, stderr=log)
                check_call(['make', 'install'], stdout=log, stderr=log)
                log.close()
                os.chdir(here)
            else:
                if 'darwin' in platform.system().lower():
                    raise Exception('Perl is included with OSX. What happened?')
                if 'windows' in platform.system().lower():
                    website = ('http://strawberry-perl.googlecode.com/',
                               'files/')
                    version = '5.16.2.2'
                global_install('Perl', website,
                               'strawberry-perl-' + str(version) + '-32bit.msi',
                               deb='libperl-dev', rpm='perl-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('Perl installation failed.')
