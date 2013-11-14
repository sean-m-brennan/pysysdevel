
import os
import sys
import glob

from ..prerequisites import compare_versions, install_pypkg, patch_file
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install Matplotlib Basemap toolkit
    """

    basemap_data_pathlist = ['mpl-data', 'basemap-data']
    basemap_data_dir = os.path.join(*basemap_data_pathlist)

    def __init__(self):
        py_config.__init__(self, 'basemap', '1.0.5',
                           dependencies=['geos'], debug=False)
        ## NB: Basemap documentation lies! It requires Python version > 2.4
        if sys.version_info < (2, 6):
            raise Exception('Basemap is not supported ' +
                            'for Python versions < 2.6')


        def null(self):
            self.environment['BASEMAP_DATA_PATHLIST'] = []
            self.environment['BASEMAP_DIR'] = ''
            self.environment['BASEMAP_DATA_FILES'] = []
            self.environment['BASEMAP_DEPENDENCIES'] = []


        def is_installed(self, environ, version):
            try:
                from mpl_toolkits import basemap
                ver = basemap.__version__
                if compare_versions(ver, version) == -1:
                    return self.found
                self.found = True
            except Exception:
                if self.debug:
                    print(sys.exc_info()[1])
                return self.found

            self.environment['BASEMAP_DATA_PATHLIST'] = basemap_data_pathlist
            basemap_dir = os.path.dirname(basemap.__file__)
            self.environment['BASEMAP_DIR'] = basemap_dir
            self.environment['BASEMAP_DATA_FILES'] = \
                [(basemap_data_dir,
                  glob.glob(os.path.join(basemap_dir, 'data', '*.*')))]
            return self.found


        def install(self, environ, version, locally=True):
            if not self.found:
                if version is None:
                    version = self.version
                website = 'http://downloads.sourceforge.net/project/matplotlib/' + \
                    'matplotlib-toolkits/basemap-' + version + '/'
                src_dir = 'basemap-' + str(version)
                archive =  src_dir + '.tar.gz'
                pth = install_pypkg(src_dir, website, archive, locally=locally)
                self.environment['BASEMAP_DATA_PATHLIST'] = basemap_data_pathlist
                basemap_dir = os.path.join(pth, 'mpl_toolkits', 'basemap')
                self.environment['BASEMAP_DIR'] = basemap_dir
                self.environment['BASEMAP_DATA_FILES'] = \
                    [(basemap_data_dir,
                      glob.glob(os.path.join(basemap_dir, 'data', '*.*')))]
                self.__patch(basemap_dir)
                if not self.is_installed(environ, version):
                    raise Exception('basemap installation failed.')


        def __patch(self, basemap_dir):
            ## modify faulty pyproj data location
            problem_file = os.path.join(basemap_dir, 'pyproj.py')
            print('PATCH ' + problem_file)
            problem_exists = True
            pf = open(problem_file, 'r')
            for line in pf:
                if 'BASEMAPDATA' in line:
                    problem_exists = False
                    break
            pf.close()
            if problem_exists:
                replacement = \
                    "if 'BASEMAPDATA' in os.environ:\n" \
                    "    pyproj_datadir = os.environ['BASEMAPDATA']\n" \
                    "else:\n" \
                    "    pyproj_datadir = "
                try:
                    patch_file(problem_file, "pyproj_datadir = ",
                               "pyproj_datadir = ", replacement)
                except IOError:  ## Permission denied
                    sys.stderr.write('WARNING: installed basemap package at ' +
                                     basemap_dir + ' cannot be relocated. ' +
                                     'Most users can ignore this message.')
