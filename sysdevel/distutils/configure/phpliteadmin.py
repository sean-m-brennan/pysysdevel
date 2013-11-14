
import os
import shutil

from ..fetching import fetch, unarchive
from ..configuration import file_config
from .. import options

class configuration(file_config):
    """
    Fetch phpliteadmin
    """
    def __init__(self):
        file_config.__init__(self, debug=False)


    def install(self, environ, version, locally=True):
        if not version:
            version = '1-9-4-1'
        php_dir = os.path.join(options.target_build_dir, options.script_dir)
        if not os.path.exists(php_dir):
            os.makedirs(php_dir)
        website = 'http://phpliteadmin.googlecode.com/files/'
        archive = 'phpliteAdmin_v' + version + '.zip'
        script = 'phpliteadmin.php'
        if not os.path.exists(script):
            fetch(website, archive, archive)
            unarchive(archive, script)
            shutil.move(os.path.join(options.target_build_dir, script),
                        os.path.join(php_dir, script))
