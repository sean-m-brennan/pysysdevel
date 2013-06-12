"""
modified 'build' command
"""

import os
import sys

try:
    from numpy.distutils.command.build import build as old_build
except ImportError, e:
    from distutils.command.build import build as old_build

from recur import process_subpackages


class build(old_build):
    '''
    Subclass build command to support new commands.
    '''
    def has_pure_modules(self):
        return self.distribution.has_pure_modules() or \
            self.distribution.has_antlr_extensions() or \
            self.distribution.has_sysdevel_support()

    def has_scripts(self):
        return self.distribution.has_scripts()

    def has_c_libraries(self):
        return self.distribution.has_c_libraries()

    def has_shared_libraries(self):
        return self.distribution.has_shared_libs()

    def has_pypp_extensions(self):
        return self.distribution.has_pypp_extensions()

    def has_web_extensions(self):
        return self.distribution.has_web_extensions()

    def has_documents(self):
        return self.distribution.has_documents()

    def has_executables(self):
        return self.distribution.has_executables()

    def has_data(self):
        return self.distribution.has_data_files() or \
            self.distribution.has_data_directories()


    ## Order is important
    sub_commands = [('config_cc',      lambda *args: True),
                    ('config_fc',      lambda *args: True),
                    ('build_src',      old_build.has_ext_modules),
                    ('build_py',       has_pure_modules),
                    ('build_js',       has_web_extensions),
                    ('build_clib',     has_c_libraries),
                    ('build_shlib',    has_shared_libraries),
                    ('build_ext',      old_build.has_ext_modules),
                    ('build_pypp_ext', has_pypp_extensions),
                    ('build_scripts',  has_scripts),
                    ('build_doc',      has_documents),
                    ('build_exe',      has_executables),
                    ]


    def run(self):
        if self.distribution.subpackages != None:
            if self.get_finalized_command('install').ran:
                return  ## avoid build after install
            try:
                os.makedirs(self.build_base)
            except:
                pass
            for idx in range(len(sys.argv)):
                if 'setup.py' in sys.argv[idx]:
                    break
            argv = list(sys.argv[idx+1:])
            if 'install' in argv:
                argv.remove('install')
            if 'clean' in argv:
                argv.remove('clean')

            process_subpackages(self.distribution.parallel_build, 'build',
                                self.build_base, self.distribution.subpackages,
                                argv, self.distribution.quit_on_error)

            if self.has_pure_modules() or self.has_c_libraries() or \
                    self.has_ext_modules() or self.has_shared_libraries() or \
                    self.has_pypp_extensions() or self.has_web_extensions() or \
                    self.has_documents() or self.has_executables() or \
                    self.has_scripts() or self.has_data():
                old_build.run(self)
        else:
            old_build.run(self)

