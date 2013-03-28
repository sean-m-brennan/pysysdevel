"""
Fetch three
"""

from sysdevel.util import *

environment = dict()

def null():
    pass

def is_installed(environ, version):
    return False

def install(environ, version, locally=True):
    website = 'http://mrdoob.github.com/three.js/build/'
    js_file = 'three.min.js'
    js_dir = os.path.join(target_build_dir, javascript_dir)
    if not os.path.exists(js_dir):
        os.makedirs(js_dir)
    if not os.path.exists(os.path.join(js_dir, js_file)):
        fetch(website, js_file, js_file)
        shutil.copy(os.path.join(download_dir, js_file), js_dir)
