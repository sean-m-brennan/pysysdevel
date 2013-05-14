
import os
import glob
import sys
import subprocess

from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install Pyjamas
    """
    def __init__(self):
        py_config.__init__(self, 'pyjs', '0.8.1a', debug=False)


    def null(self):
        self.environment['PYJSBUILD'] = None


    def is_installed(self, environ, version):
        set_debug(self.debug)
        try:
            pyjamas_root = os.environ['PYJAMAS_ROOT']
            pyjs_bin = os.path.join(pyjamas_root, 'bin')
            pyjs_lib = os.path.join(pyjamas_root, 'build', 'lib')
            self.environment['PYJSBUILD'] = find_program('pyjsbuild',
                                                         [pyjs_bin])
            sys.path.insert(0, pyjs_lib)
            self.found = True
        except Exception, e:
            if self.debug:
                print e
            try:
                import pyjs
                self.environment['PYJSBUILD'] = find_program('pyjsbuild')
                self.found = True
            except Exception, e:
                if self.debug:
                    print e
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = self.version
            website = 'https://github.com/pyjs/pyjs/zipball/'
            archive = 'pyjs-' + version + '.zip'
            src_dir = 'pyjamas-' + version
            fetch(website, version, archive)
            unarchive(archive, src_dir)
            if VERBOSE:
                sys.stdout.write('PREREQUISITE pyjamas ')

            working_dir = os.path.join(target_build_dir, src_dir)
            if not os.path.exists(working_dir):
                os.rename(glob.glob(os.path.join(target_build_dir,
                                                 '*pyjs*'))[0], working_dir)

            ## Unique two-step installation
            log_file = os.path.join(target_build_dir, 'pyjamas.log')
            log = open(log_file, 'w')
            here = os.path.abspath(os.getcwd())
            os.chdir(working_dir)

            cmd_line = [sys.executable, 'bootstrap.py',]
            try:
                p = subprocess.Popen(cmd_line, stdout=log, stderr=log)
                status = process_progress(p)
            except KeyboardInterrupt,e:
                p.terminate()
                log.close()
                raise e
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
            except KeyboardInterrupt,e:
                p.terminate()
                log.close()
                raise e
            self.check_install(status, log, log_file)

            if VERBOSE:
                sys.stdout.write(' done\n')
            os.chdir(here)
            search_path = []
            if locally:
                search_path.append(working_dir)
                sys.path.insert(0, os.path.join(working_dir, 'build', 'lib'))
            self.environment['PYJSBUILD'] = find_program('pyjsbuild',
                                                         search_path)


    def check_install(self, status, log, log_file):
        if status != 0:
            log.close()
            sys.stdout.write(' failed; See ' + log_file)
            raise Exception('Pyjamas is required, but could not be ' +
                            'installed; See ' + log_file)
