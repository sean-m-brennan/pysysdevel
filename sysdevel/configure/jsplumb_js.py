"""
Fetch jsPlumb (using jQuery)
"""

from sysdevel.util import *

DEPENDENCIES = ['jquery', 'jquery_ui',]

environment = dict()

def null():
    pass

def is_installed(environ, version):
    return False

def install(environ, version, target='build', locally=True):
    #FIXME
    if version is None:
        version = '1.3.16'
    website = 'http://jsplumb.googlecode.com/files/'
    js_file = 'jquery.jsPlumb-' + version + '-all-min.js'
    js_dir = os.path.join(target, javascript_dir)
    js_target = 'jquery.jsPlumb-all-min.js'
    if not os.path.exists(js_dir):
        os.makedirs(js_dir)
    if not os.path.exists(os.path.join(js_dir, js_target)):
        fetch(website, js_file, js_file)
        shutil.copy(os.path.join(download_dir, js_file),
                    os.path.join(js_dir, js_target))
