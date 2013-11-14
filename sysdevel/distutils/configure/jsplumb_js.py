
import os
import shutil

from ..fetching import fetch
from ..configuration import file_config
from .. import options

class configuration(file_config):
    """
    Fetch jsPlumb (using jQuery)
    """
    def __init__(self):
        file_config.__init__(self, dependencies=[('jquery', '1.8.1'),
                                               ('jquery_ui', '1.8.23')],
                           debug=False)


    def install(self, environ, version, locally=True):
        if version is None:
            version = '1.5.3'
        website = 'https://raw.github.com/sporritt/jsPlumb/master/dist/js/'
        js_file = 'jquery.jsPlumb-' + version + '-min.js'
        js_dir = os.path.join(options.target_build_dir, options.javascript_dir)
        js_target = 'jquery.jsPlumb.min.js'
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        if not os.path.exists(os.path.join(js_dir, js_target)):
            fetch(website, js_file, js_file)
            shutil.copy(os.path.join(options.download_dir, js_file),
                        os.path.join(js_dir, js_target))
