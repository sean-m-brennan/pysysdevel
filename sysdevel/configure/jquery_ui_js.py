"""
Fetch jQuery UI
"""

from sysdevel.util import *

DEPENDENCIES = ['jquery',]

environment = dict()

def null():
    pass

def is_installed(environ, version):
    return False

def install(environ, version, locally=True):
    if version is None:
        version = '1.8.23'
    website = 'http://code.jquery.com/ui/' + version + '/'
    js_file = 'jquery-ui.min.js'
    js_dir = os.path.join(target_build_dir, javascript_dir)
    if not os.path.exists(js_dir):
        os.makedirs(js_dir)
    if not os.path.exists(os.path.join(js_dir, js_file)):
        fetch(website, js_file, js_file)
        shutil.copy(os.path.join(download_dir, js_file), js_dir)
