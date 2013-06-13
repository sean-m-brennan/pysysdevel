"""
'install_data' command for installing shared libraries and executables
"""

import os
import util

try:
    from numpy.distutils.command.install_data import install_data as old_data
except:
    from distutils.command.install_data import install_data as old_data


class install_data(old_data):
    def initialize_options(self):
        old_data.initialize_options(self)
        self.data_dirs = self.distribution.data_dirs
        if self.data_files is None:
            self.data_files = []

 
    def finalize_options(self):
        install = self.get_finalized_command('install')
        if not hasattr(install, 'install_data'):
            if install.prefix is None:
                self.data_install_dir = os.path.join(install.install_base, 'share')
            else:
                self.data_install_dir = os.path.join(install.prefix, 'share')
        else:
            self.data_install_dir = install.install_data
        old_data.finalize_options(self)


    def run (self):
        old_data.run(self)
        util.mkdir(self.data_install_dir)
        if (not hasattr(self.distribution, 'using_py2exe') or \
                not self.distribution.using_py2exe) and self.data_dirs:
           for tpl in self.data_dirs:
                target = os.path.join(self.data_install_dir, tpl[0])
                for d in tpl[1]:
                    util.copy_tree(d, target, excludes=['.svn*', 'CVS*',
                                                        'Makefile*'])
