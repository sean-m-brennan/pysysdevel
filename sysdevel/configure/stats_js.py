
import os
import shutil

from sysdevel.util import *
from sysdevel.configuration import js_config

class configuration(js_config):
    """
    Fetch three.js stats tool
    """
    def __init__(self):
        js_config.__init__(self, debug=False)


    def install(environ, version, locally=True):
        website = 'https://github.com/mrdoob/stats.js/blob/master/build/'
        js_file = 'stats.min.js'
        js_dir = os.path.join(target_build_dir, javascript_dir)
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        if not os.path.exists(os.path.join(js_dir, js_file)):
            fetch(website, js_file, js_file)
            shutil.copy(os.path.join(download_dir, js_file), js_dir)
