
from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install PyYAML
    """
    def __init__(self):
        py_config.__init__(self, 'PyYAML', '3.10', debug=False,
                           dependencies=['libyaml'])


    def is_installed(self, environ, version):
        try:
            import yaml
            ver = yaml.__version__
            check_version = False
            if hasattr(yaml, '__version__'):
                ver = yaml.__version__
                check_version = True
            elif hasattr(yaml, 'version'):
                ver = yaml.version
                check_version = True
            if check_version:
                if compare_versions(ver, version) == -1:
                    return self.found
            self.found = True
        except Exception, e:
            if self.debug:
                print e
        return self.found
