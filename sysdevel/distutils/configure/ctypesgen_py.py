
import os
import sys

from sysdevel.distutils.prerequisites import find_program, install_pypkg_without_fetch, ConfigError
from sysdevel.distutils.fetching import fetch, unarchive
from sysdevel.distutils.configuration import prog_config
from sysdevel.distutils import options

class configuration(prog_config):
    """
    Find/install ctypesgen package (not using pypi due to compilications)
    """
    def __init__(self):
        prog_config.__init__(self, 'ctypesgen.py', debug=False)


    def null(self):
        self.environment['CTYPESGEN'] = None
        self.environment['CTYPESGEN_PATH'] = None


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        limit = False
        locations = []
        if 'CTYPESGEN' in environ and environ['CTYPESGEN']:
            locations.append(os.path.dirname(environ['CTYPESGEN']))
            limit = True

        try:
            exe = find_program('ctypesgen.py', locations, limit=limit)
            import ctypesgencore
            lib = os.path.dirname(os.path.dirname(ctypesgencore.__file__))
            self.found = True
        except (ConfigError, ImportError):
            if self.debug:
                print(sys.exc_info()[1])
            return self.found

        self.environment['CTYPESGEN'] = exe
        self.environment['CTYPESGEN_PATH'] = lib
        return self.found


    def download(self, environ, version, strict=False):
        website = 'http://pypi.python.org/packages/source/c/ctypesgen/'
        if version is None:
            version = '0.r125'
        src_dir = 'ctypesgen-' + version
        archive = src_dir + '.tar.gz'
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            src_dir = self.download(environ, version, strict)
            install_pypkg_without_fetch('ctypesgen', src_dir=src_dir,
                                        locally=locally)
            if locally:
                prefix = os.path.abspath(options.target_build_dir)
                if not prefix in options.local_search_paths:
                    options.add_local_search_path(prefix)
            if not self.is_installed(environ, version, strict):
                raise Exception('ctypesgen installation failed.')
