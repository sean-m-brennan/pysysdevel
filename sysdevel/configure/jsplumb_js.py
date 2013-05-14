
import os
import shutil

from sysdevel.util import *
from sysdevel.configuration import js_config

class configuration(js_config):
    """
    Fetch jsPlumb (using jQuery)
    """
    def __init__(self):
        js_config.__init__(self, dependencies=['jquery', 'jquery_ui'],
                           debug=False)


    def install(self, environ, version, locally=True):
        if version is None:
            version = '1.3.16'
        website = 'http://jsplumb.googlecode.com/files/'
        js_file = 'jquery.jsPlumb-' + version + '-all-min.js'
        js_dir = os.path.join(target_build_dir, javascript_dir)
        js_target = 'jquery.jsPlumb.min.js'
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        if not os.path.exists(os.path.join(js_dir, js_target)):
            fetch(website, js_file, js_file)
            shutil.copy(os.path.join(download_dir, js_file),
                        os.path.join(js_dir, js_target))
