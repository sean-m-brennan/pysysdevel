
from ..prerequisites import *
from ..configuration import prog_config

class configuration(prog_config):
    """
    Find/install wxGlade
    """
    def __init__(self):
        prog_config.__init__(self, 'wxglade', debug=False)
        self.environment['WXGLADE'] = None


    def is_installed(self, environ, version):
        set_debug(self.debug)
        try:
            import wxglade.common
            ver = wxglade.common.version
            if compare_versions(ver, version) == -1:
                return self.found
            self.environment['WXGLADE'] = find_program('wxglade')
            self.found = True
        except Exception:
            if self.debug:
                e = sys.exc_info()[1]
                print(e)
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '0.6.5'
            website = 'http://downloads.sourceforge.net/project/wxglade/wxglade/' + version + '/'
            src_dir = 'wxGlade-' + version
            archive = src_dir + '.tar.gz'
            install_pypkg(src_dir, website, archive, locally=locally)
            if not self.is_installed(environ, version):
                raise Exception('wxGlade installation failed.')
