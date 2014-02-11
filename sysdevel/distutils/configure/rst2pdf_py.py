
from ..prerequisites import install_pypkg
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install rst2pdf
    """
    ##TODO should be PyPI, seriously messed up
    def __init__(self):
        py_config.__init__(self, 'rst2pdf', '0.93',
                           dependencies=['docutils', 'reportlab',
                                         'pygments', 'pdfrw'],
                           debug=False)


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            website = 'http://rst2pdf.googlecode.com/files/'
            if version is None:
                version = self.version
            src_dir = 'rst2pdf-' + str(version)
            archive = src_dir + '.tar.gz' 
            install_pypkg(src_dir, website, archive, locally=locally)
            if not self.is_installed(environ, version, strict):
                raise Exception('rst2pdf installation failed.')
