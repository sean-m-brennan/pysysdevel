"""
Find SciPy
"""

from sysdevel.util import *

environment = dict()
scipy_found = False

DEPENDENCIES = ['gfortran']

def null():
    pass


def is_installed(environ, version):
    global environment, scipy_found
    try:
        import scipy
        ver = scipy.__version__
        if compare_versions(ver, version) == -1:
            return scipy_found
        scipy_found = True
    except:
        pass
    return scipy_found


def install(environ, version, locally=True):
    if not scipy_found:
        if version is None:
            version = '0.11.0'
        website = 'http://downloads.sourceforge.net/' + \
            'project/scipy/scipy/' + version + '/'
        src_dir = 'scipy-' + str(version)
        archive = src_dir + '.tar.gz' 
        install_pypkg(src_dir, website, archive, locally=locally)
        if not is_installed(environ, version):
            raise Exception('SciPy installation failed.')
