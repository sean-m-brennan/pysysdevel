
import os
from sysdevel.distutils.fetching import fetch
from sysdevel.distutils.configuration import file_config
from sysdevel.distutils import options

class configuration(file_config):
    """
    Fetch jQuery UI
    """
    def __init__(self):
        file_config.__init__(self, 'jquery-ui-timepicker-addon.js',
                             os.path.join(options.target_build_dir,
                                          options.javascript_dir),
                             'http://trentrichardson.com/examples/timepicker/',
                             dependencies=['jquery_ui'], debug=False)
        self.targets = ['jquery-ui-timepicker-addon.js',
                        'jquery-ui-timepicker-addon.css']

    def download(self, environ, version, strict=False):
        website = 'http://trentrichardson.com/examples/timepicker/'
        for t in self.targets:
            fetch(website, t, t)
        ## FIXME move stylesheet to proper place
        return ''
