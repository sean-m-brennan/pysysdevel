
import os

from ..prerequisites import *
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install Matplotlib
    """
    def __init__(self):
        py_config.__init__(self, 'matplotlib', '1.2.0', debug=False)


    def null(self):
        self.environment['MATPLOTLIB_DATA_FILES'] = []


    def is_installed(self, environ, version):
        try:
            import matplotlib
            ver = matplotlib.__version__
            if compare_versions(ver, version) == -1:
                return self.found
            self.found = True
        except Exception as e:
            if self.debug:
                print(e)
            return self.found

        self.environment['MATPLOTLIB_DATA_FILES'] = \
            matplotlib.get_py2exe_datafiles()
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'https://github.com/downloads/matplotlib/matplotlib/'
            if version is None:
                version = self.version
            src_dir = 'matplotlib-' + str(version)
            archive = src_dir + '.tar.gz'
            pth = install_pypkg(src_dir, website, archive, locally=locally)

            if not self.is_installed(environ, version):
                raise Exception('matplotlib installation failed.')

            ##FIXME: is this needed at all?
            mpl = sys.modules.get('matplotlib', None)
            if mpl:
                self.environment['MATPLOTLIB_DATA_FILES'] = \
                    mpl.get_py2exe_datafiles()
            else:
                ## Can't re-import properly?
                datapath = os.path.abspath(os.path.join(pth, 'matplotlib',
                                                        'mpl-data'))
                head, tail = os.path.split(datapath)
                d = {}
                for root, dirs, files in os.walk(datapath):
                    # Need to explicitly remove cocoa_agg files or py2exe complains
                    # NOTE I dont know why, but do as previous version
                    if 'Matplotlib.nib' in files:
                        files.remove('Matplotlib.nib')
                    files = [os.path.join(root, filename) for filename in files]
                    root = root.replace(tail, 'mpl-data')
                    root = root[root.index('mpl-data'):]
                    d[root] = files
                self.environment['MATPLOTLIB_DATA_FILES'] = list(d.items())

