
import platform

from sysdevel.util import *
from sysdevel.configuration import lib_config

class configuration(lib_config):
    """
    Find/install Graphviz library
    """
    def __init__(self):
        lib_config.__init__(self, "cgraph", "cgraph.h",
                            dependencies=[], #FIXME lots of dependencies
                            debug=False)


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '2.30.1'
            website = ('http://www.graphviz.org/',
                       'pub/graphviz/stable/SOURCES/')
            if locally or 'windows' in platform.system().lower():
                src_dir = 'graphviz-' + str(version)
                archive = src_dir + '.tar.gz'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('Graphviz', website,
                               brew='graphviz', port='graphviz-devel',
                               deb='graphviz-dev', rpm='graphviz-devel')
            if not self.is_installed(environ, version):
                raise Exception('Graphviz installation failed.')
