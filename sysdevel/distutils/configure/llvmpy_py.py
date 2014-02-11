
from ..configuration import py_config
from ..prerequisites import install_pypkg, ConfigError

class configuration(py_config):
    """
    Find/install LLVM python wrapper
    """
    def __init__(self):
        py_config.__init__(self, 'llvmpy', '0.11.2',
                           dependencies=[('llvm_lib', '3.2'),],
                           debug=False)


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            website = 'https://pypi.python.org/packages/source/l/llvmpy/'
            if version is None:
                version = self.version
            src_dir = 'llvmpy-' + str(version)
            archive = src_dir + '.tar.gz'
            ## Requires LLVM_CONFIG_PATH from llvm_lib
            try:
                cfg_path = environ['LLVM_CONFIG_PATH']
            except KeyError:
                raise ConfigError('Python llvm package requires ' +
                                  'a custom-compiled LLVM library, ' +
                                  'which was not found.')
            install_pypkg(src_dir, website, archive,
                          env=['LLVM_CONFIG_PATH=' + cfg_path],
                          locally=locally)
            if not self.is_installed(environ, version, strict):
                raise Exception('LLVM python wrapper installation failed.')
