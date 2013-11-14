
import os
import shutil

from ..fetching import fetch
from ..configuration import file_config
from .. import options

class configuration(file_config):
    """
    Fetch raphael
    """
    def __init__(self):
        file_config.__init__(self, debug=False)


    def install(self, environ, version, locally=True):
        if version is None:
            version = '2.1.0'
        website = 'http://github.com/DmitryBaranovskiy/raphael/raw/master/'
        js_file = 'raphael-min.js'
        js_dir = os.path.join(options.target_build_dir, options.javascript_dir)
        js_target = 'raphael.min.js'
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        if not os.path.exists(os.path.join(js_dir, js_file)):
            fetch(website, js_file, js_file)
            shutil.copy(os.path.join(options.download_dir, js_file),
                        os.path.join(js_dir, js_target))
