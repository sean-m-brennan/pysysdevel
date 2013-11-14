
from ..prerequisites import install_pypkg
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install Py++/PyGCCXML
    """
    def __init__(self):
        py_config.__init__(self, 'pyplusplus', '1.0.0',
                           dependencies=['gccxml'], debug=False)


    def is_installed(self, environ, version):
        try:
            import pyplusplus
            self.found = True
        except Exception:
            if self.debug:
                print(sys.exc_info()[1])
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = self.version
            major = '.'.join(version.split('.')[:2])
            mainsite = 'http://downloads.sourceforge.net/project/pygccxml/'
            website = mainsite + 'pygccxml/pygccxml-' + major + '/'
            src_dir = 'pygccxml-' + str(version)
            archive = src_dir + '.zip'
            install_pypkg(src_dir, website, archive, locally=locally)

            website = mainsite + 'pyplusplus/pyplusplus-' + major + '/'
            src_dir = 'Py++-' + str(version)
            archive = 'pyplusplus-' + str(version) + '.zip'
            install_pypkg(src_dir, website, archive, locally=locally)
            if not self.is_installed(environ, version):
                raise Exception('Py++ installation failed.')
