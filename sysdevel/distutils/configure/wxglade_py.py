
import sys

from ..prerequisites import find_program, compare_versions, install_pypkg_without_fetch, ConfigError
from ..fetching import fetch, unarchive
from ..configuration import prog_config
from .. import options

class configuration(prog_config):
    """
    Find/install wxGlade
    """
    def __init__(self):
        prog_config.__init__(self, 'wxglade', debug=False)
        self.environment['WXGLADE'] = None


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        try:
            import wxglade.common
            ver = wxglade.common.version
            not_ok = (compare_versions(ver, version) == -1)
            if strict:
                not_ok = (compare_versions(ver, version) != 0)
            if not_ok:
                if self.debug:
                    print('Wrong version of wxGlade: ' +
                          str(ver) + ' vs ' + str(version))
                return self.found
            self.environment['WXGLADE'] = find_program('wxglade')
            self.found = True
        except (ImportError, ConfigError):
            if self.debug:
                print(sys.exc_info()[1])
        return self.found


    def download(self, environ, version, strict=False):
        if version is None:
            version = '0.6.5'
        website = 'http://downloads.sourceforge.net/project/wxglade/wxglade/' + version + '/'
        src_dir = 'wxGlade-' + str(version)
        archive = src_dir + '.tar.gz' 
        fetch(website, archive, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        if not self.found:
            self.download(environ, version, strict)
            install_pypkg_without_fetch('wxglade', locally=locally)
            if not self.is_installed(environ, version, strict):
                raise ConfigError('wxGlade', 'Installation failed.')
