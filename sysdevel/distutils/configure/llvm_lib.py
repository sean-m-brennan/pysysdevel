
import os
import platform

from ..prerequisites import autotools_install, global_install, find_program, ConfigError
from ..configuration import lib_config

class configuration(lib_config):
    """
    Find/install LLVM Library
    """
    def __init__(self):
        lib_config.__init__(self, "llvm", os.path.join('llvm', "User.h"),
                            debug=False)
        self.first = True


    def is_installed(self, environ, version=None, strict=False):
        self.found = lib_config.is_installed(self, environ, version, strict)
        if self.found:
            lib_dir = self.environment.get('LLVM_LIB_DIR', '')
            ## llvmpy *requires* RTTI flag, so system version will not work
            if lib_dir.endswith('llvm'):
                lib_dir = os.path.dirname(lib_dir)
            base_dir = os.path.dirname(lib_dir)
            if base_dir == '' or base_dir == '/usr':
                self.found = False
                return self.found
            ## LLVM_CONFIG_PATH is needed by llvmpy
            try:
                self.environment['LLVM_CONFIG_PATH'] = \
                    find_program('llvm-config',
                                 [os.path.dirname(lib_dir)], limit=True)
            except ConfigError:
                self.found = False
        return self.found


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            if version is None:
                version = '3.2'
            website = ('http://llvm.org/releases/' + str(version) + '/',)
            if locally or 'windows' in platform.system().lower():
                src_dir = 'llvm-' + str(version) + '.src'
                archive = src_dir + '.tar.gz'
                ## Compile with:  REQUIRES_RTTI=1 ./configure --enable-optimized
                autotools_install(environ, website, archive, src_dir, locally,
                                  ['--enable-optimized'],
                                  {'REQUIRES_RTTI': '1'})
            else:
                global_install('LLVM', website,
                               brew='llvm', port='llvm-devel',
                               deb='libllvm-dev', rpm='llvm-devel')
            if not self.is_installed(environ, version, strict):
                raise Exception('LLVM installation failed.')
