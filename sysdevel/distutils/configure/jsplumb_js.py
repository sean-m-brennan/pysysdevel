
import os
from sysdevel.distutils.fetching import fetch
from sysdevel.distutils.configuration import file_config, latest_version
from sysdevel.distutils import options

class configuration(file_config):
    """
    Fetch jsPlumb (using jQuery)
    """
    def __init__(self):
        file_config.__init__(self, 'jquery.jsPlumb.min.js',
                             os.path.join(options.target_build_dir,
                                          options.javascript_dir),
                             'https://raw.github.com/sporritt/jsPlumb',
                             dependencies=[('jquery', '1.8.1'),
                                           ('jquery_ui', '1.8.23')],
                             debug=False)


    def download(self, environ, version, strict=False):
        file_pattern = 'jquery.jsPlumb-*-min.js'
        if version is None:
            website = 'https://raw.github.com/sporritt/jsPlumb/master/dist/js/'
            version = '1.6.2' #latest_version('jsPlumb', website, file_pattern)
        else:
            website = 'https://raw.github.com/sporritt/jsPlumb/dev/' + \
                      version + '/dist/js/'
        file_parts = file_pattern.split('*')
        js_file = file_parts[0] + version + file_parts[1]
        fetch(website, js_file, self.targets[0])
        return ''
