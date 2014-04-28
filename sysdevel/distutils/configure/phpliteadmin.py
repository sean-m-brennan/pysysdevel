
import os
import shutil
from sysdevel.distutils.fetching import fetch, unarchive
from sysdevel.distutils.configuration import file_config
from sysdevel.distutils import options

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


    def install(self, environ, version, strict=False, locally=True):
        self.download(environ, version, strict)
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)
        shutil.copy(os.path.join(options.target_build_dir, self.targets[0]),
                    self.target_dir)
