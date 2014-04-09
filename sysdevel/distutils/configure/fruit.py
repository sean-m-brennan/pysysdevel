
import os
import shutil

from ..fetching import fetch, unarchive
from ..filesystem import mkdir
from ..configuration import config
from .. import options


class configuration(config):
    """
    Find/fetch/install FoRtran UnIt Testing framework
    """
    def __init__(self):
        config.__init__(self, debug=False)
        self.install_dir = os.path.abspath(options.target_build_dir,
                                           'src', 'fruit')
        self.sources = ['fruit_util.f90', 'fruit.f90']


    def null(self):
        self.environment['FRUIT_SOURCE_DIR'] = None
        self.environment['FRUIT_SOURCE_FILES'] = []


    def is_installed(self, environ, version=None, strict=False):
        for src in self.sources:
            if not os.path.exists(os.path.join(self.install_dir, src)):
                return self.found
        self.found = True
        self.environment['FRUIT_SOURCE_DIR'] = self.install_dir
        self.environment['FRUIT_SOURCE_FILES'] = self.sources


    def download(self, environ, version, strict=False):
        if version is None:
            version = '3.2.0'
        website = 'http://downloads.sourceforge.net/project/fortranxunit' + \
                  '/fruit_' + version + '/'
        src_dir = 'fruit_' + str(version)
        archive = src_dir + '.tgz'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            src_dir = self.download(environ, version, strict)
            source_dir = os.path.join(options.target_build_dir, src_dir, 'src')
            install_dir = os.path.abspath(options.target_build_dir,
                                          'src', 'fruit')
            mkdir(install_dir)
            for src in self.sources:
                shutil.copy(os.path.join(source_dir, src),
                            os.path.join(install_dir, src))

            if not self.is_installed(environ, version, strict):
                raise Exception('FRUIT installation failed.')
