"""
modified 'install' command
"""

import os

try:
    from numpy.distutils.command.install import install as old_install
except ImportError, e:
    from distutils.command.install import install as old_install

from recur import process_subpackages


class install(old_install):
    '''
    Subclass install command to support new commands.
    '''
    def initialize_options (self):
        old_install.initialize_options(self)
        self.ran = False

    def has_lib(self):
        return old_install.has_lib(self) or self.distribution.has_shared_libs()

    def has_exe(self):
        return self.distribution.has_executables()

    def has_data(self):
        return self.distribution.has_data_files() or \
            self.distribution.has_data_directories()

    sub_commands = [('install_exe', has_exe),
                    ('install_data', has_data),
                    ('install_lib', has_lib),
                    ('install_headers', old_install.has_headers),
                    ('install_scripts', old_install.has_scripts),
                    #('install_egg_info', lambda self:True),
                    ]

    def run(self):
        if self.distribution.subpackages != None:
            self.ran = True
            build = self.get_finalized_command('build')
            try:
                os.makedirs(build.build_base)
            except:
                pass
            for idx in range(len(sys.argv)):
                if 'setup.py' in sys.argv[idx]:
                    break
            argv = list(sys.argv[idx+1:])
            if 'build' in argv:
                argv.remove('build')
            if 'clean' in argv:
                argv.remove('clean')

            process_subpackages(build.distribution.parallel_build, 'install',
                                build.build_base, self.distribution.subpackages,
                                argv, build.distribution.quit_on_error)

            if build.has_pure_modules() or build.has_c_libraries() or \
                    build.has_ext_modules() or build.has_shared_libraries() or \
                    build.has_pypp_extensions() or \
                    build.has_web_extensions() or \
                    build.has_documents() or build.has_executables() or \
                    build.has_scripts() or build.has_data():
                old_install.run(self)
        else:
            old_install.run(self)
