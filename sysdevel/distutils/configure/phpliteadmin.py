
import os
from ..fetching import fetch, unarchive
from ..configuration import file_config
from .. import options

class configuration(file_config):
    """
    Fetch phpliteadmin
    """
    def __init__(self):
        file_config.__init__(self, 'phpliteadmin.php',
                             os.path.join(options.target_build_dir,
                                          options.script_dir),
                             'http://phpliteadmin.googlecode.com/files/',
                             debug=False)


    def download(self, environ, version, strict=False):
        if not version:
            version = '1-9-4-1'
        archive = 'phpliteAdmin_v' + version + '.zip'
        fetch(self.website, archive, archive)
        unarchive(archive, self.targets[0])
        return ''
