"""
Fetch raphael
"""

from sysdevel.util import *

environment = dict()

def null():
    pass

def is_installed(environ, version):
    return False

def install(environ, version, target='build', locally=True):
    if version is None:
        version = '2.1.0'
    website = 'http://github.com/DmitryBaranovskiy/raphael/raw/master/'
    js_file = 'raphael-min.js'
    js_dir = os.path.join(target, javascript_dir)
    if not os.path.exists(js_dir):
        os.makedirs(js_dir)
    if not os.path.exists(os.path.join(js_dir, js_file)):
        fetch(website, js_file, js_file)
        shutil.copy(os.path.join(download_dir, js_file), js_dir)
