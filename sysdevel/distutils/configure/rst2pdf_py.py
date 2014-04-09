
from ..fetching import fetch, unarchive
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


    def download(self, environ, version, strict=False):
        website = 'http://rst2pdf.googlecode.com/files/'
        if version is None:
            version = self.version
        src_dir = 'rst2pdf-' + str(version)
        archive = src_dir + '.tar.gz' 
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir
