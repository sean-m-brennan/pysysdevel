
import os
from sysdevel.distutils.fetching import fetch
from sysdevel.distutils.configuration import file_config
from sysdevel.distutils import options

class configuration(file_config):
    """
    Fetch jQuery UI
    """
    def __init__(self):
        file_config.__init__(self, 'jquery-ui.min.js',
                             os.path.join(options.target_build_dir,
                                          options.javascript_dir),
                             'http://code.jquery.com/ui/',
                             dependencies=['jquery'], debug=False)
        ## add mousewheel plugin by default
        self.targets = ['jquery-ui.min.js', 'jquery.mousewheel.js']


    def download(self, environ, version, strict=False):
        if version is None:
            version = '1.8.23'
        website = 'http://code.jquery.com/ui/' + version + '/'
        js_file = self.targets[0]
        fetch(website, js_file, js_file)
        website = 'https://raw.github.com/brandonaaron/jquery-mousewheel/master/'
        js_file = self.targets[1]
        fetch(website, js_file, js_file)
        return ''
