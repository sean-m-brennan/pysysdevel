
import os
import glob
import sys
import subprocess

from ..prerequisites import find_program, as_admin, ConfigError
from ..building import process_progress
from ..configuration import py_config
from ..fetching import fetch, unarchive
from .. import options

class configuration(py_config):
    """
    Find/install Pyjamas
    """
    ##TODO should be PyPI, but ugly due to fork
    def __init__(self):
        py_config.__init__(self, 'pyjs', '0.8.1a', debug=False)


    def null(self):
        self.environment['PYJSBUILD'] = None


    def is_installed(self, environ, version=None, strict=False):
        options.set_debug(self.debug)
        try:
            pyjamas_root = os.environ['PYJAMAS_ROOT']
            pyjs_bin = os.path.join(pyjamas_root, 'bin')
            #pyjs_lib = os.path.join(pyjamas_root, 'build', 'lib')
            self.environment['PYJSBUILD'] = find_program('pyjsbuild',
                                                         [pyjs_bin])
            self.found = True
        except (KeyError, ConfigError, ImportError):
            if self.debug:
                print(sys.exc_info()[1])
            try:
                local = glob.glob(os.path.join(options.target_build_dir,
                                               'pyjamas-*'))
                local_bins = []
                if len(local):
                    local_bins.append(os.path.join(local[0], 'bin'))
                self.environment['PYJSBUILD'] = find_program('pyjsbuild',
                                                             local_bins)
                self.found = True
            except (ImportError, ConfigError):
                if self.debug:
                    print(sys.exc_info()[1])
        return self.found


    def download(self, environ, version, strict=False):
        if version is None:
            version = self.version
        website = 'https://github.com/pyjs/pyjs/zipball/'
        archive = 'pyjs-' + version + '.zip'
        src_dir = 'pyjamas-' + str(version)
        fetch(website, version, archive)
        unarchive(archive, src_dir)
        return src_dir


    def install(self, environ, version, strict=False, locally=True):
        ## always locally, o.w. won't work
        locally = True
        if not self.found:
            src_dir = self.download(environ, version, strict)
            if options.VERBOSE:
                sys.stdout.write('PREREQUISITE pyjamas ')

            working_dir = os.path.join(options.target_build_dir, src_dir)
            if not os.path.exists(working_dir):
                os.rename(glob.glob(os.path.join(options.target_build_dir,
                                                 '*pyjs*'))[0], working_dir)

            ## Unique two-step installation
            log_file = os.path.join(options.target_build_dir, 'pyjamas.log')
            log = open(log_file, 'w')
            here = os.path.abspath(os.getcwd())
            os.chdir(working_dir)

            cmd_line = [sys.executable, 'bootstrap.py',]
            try:
                p = subprocess.Popen(cmd_line, stdout=log, stderr=log)
                status = process_progress(p)
            except KeyboardInterrupt:
                p.terminate()
                log.close()
                raise
            self.check_install(status, log, log_file)

            cmd_line = [sys.executable, 'run_bootstrap_first_then_setup.py',
                        'build']
            if not locally:
                sudo_prefix = []
                if not as_admin():
                    sudo_prefix = ['sudo']
                cmd_line = sudo_prefix + cmd_line + ['install']
            try:
                p = subprocess.Popen(cmd_line, stdout=log, stderr=log)
                status = process_progress(p)
                log.close()
            except KeyboardInterrupt:
                p.terminate()
                log.close()
                raise
            self.check_install(status, log, log_file)

            if options.VERBOSE:
                sys.stdout.write(' done\n')
            os.chdir(here)
            search_path = []
            if locally:
                search_path.append(working_dir)
            self.environment['PYJSBUILD'] = find_program('pyjsbuild',
                                                         search_path)


    def check_install(self, status, log, log_file):
        if status != 0:
            log.close()
            sys.stdout.write(' failed; See ' + log_file)
            raise Exception('Pyjamas is required, but could not be ' +
                            'installed; See ' + log_file)
