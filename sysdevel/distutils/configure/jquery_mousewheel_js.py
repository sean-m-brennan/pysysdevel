
import os
from sysdevel.distutils.fetching import fetch
from sysdevel.distutils.configuration import file_config
from sysdevel.distutils import options

class configuration(file_config):
    """
    Fetch jQuery UI
    """
    def __init__(self):
        file_config.__init__(self, 'jquery.mousewheel.js',
                             os.path.join(options.target_build_dir,
                                          options.javascript_dir),
                             'https://github.com/brandonaaron/jquery-mousewheel',
                             dependencies=['jquery_ui'], debug=False)


    def download(self, environ, version, strict=False):
        website = 'https://raw.github.com/brandonaaron/jquery-mousewheel/master/'
        js_file = self.targets[0]
        fetch(website, js_file, js_file)
        return ''
