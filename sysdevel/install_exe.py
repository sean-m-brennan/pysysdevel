"""
'install_data' command for installing shared libraries and executables
"""

import os
import struct

from distutils.command import install_lib
from distutils.util import change_root, convert_path


class install_exe(install_lib.install_lib):
    def run (self):
        '''
        Also install native executables
        '''
        install_lib.install_lib.run(self)

        build_exe = self.get_finalized_command('build_exe')
        install = self.get_finalized_command('install')

        if install.prefix is None:
            target_dir = os.path.join(install.install_base, 'bin')
        else:
            target_dir = os.path.join(install.prefix, 'bin')
        self.mkpath(target_dir)
        for exe in build_exe.install_executables:
            source = os.path.join(build_exe.build_temp, exe)
            self.copy_file(source, target_dir)
