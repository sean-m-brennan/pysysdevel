
from sysdevel.configuration import prog_config

class configuration(prog_config):
    """
    Find/install ctypesgen package
    """
    def __init__(self):
        prog_config.__init__(self, 'ctypesgen.py', debug=False)


    def null(self):
        self.environment['CTYPESGEN'] = None
        self.environment['CTYPESGEN_PATH'] = None


    def is_installed(self, environ, version):
        set_debug(self.debug)
        limit = False
        locations = []
        if 'CTYPESGEN' in environ:
            locations.append(os.path.dirname(environ['CTYPESGEN']))
            limit = True

        try:
            exe = find_program('ctypesgen.py', locations, limit=limit)
            import ctypesgencore
            lib = os.path.dirname(ctypesgencore.__file__)
            self.found = True
        except Exception, e:
            if self.debug:
                print e
            return self.found

        self.environment['CTYPESGEN'] = exe
        self.environment['CTYPESGEN_PATH'] = lib
        return self.found


    def install(self, environ, version, locally=True):
        global local_search_paths
        if not self.found:
            website = 'http://pypi.python.org/packages/source/c/ctypesgen/'
            if version is None:
                version = '0.r125'
            archive = 'ctypesgen-' + version + '.tar.gz'
            install_pypkg('ctypesgen-' + version, website, archive,
                          locally=locally)
            if locally:
                prefix = os.path.abspath(target_build_dir)
                if not prefix in local_search_paths:
                    local_search_paths.append(prefix)
            if not self.is_installed(environ, version):
                raise Exception('ctypesgen installation failed.')
