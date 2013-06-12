"""
modified 'clean' command
"""

import os
import sys
import shutil

from distutils.command.clean import clean as old_clean

from recur import process_subpackages
import util


class clean(old_clean):
    def run(self):
        # Remove .pyc, .lreg and .sibling files
        if hasattr(os, 'walk'):
            for root, dirs, files in os.walk('.'):
                for f in files:
                    if f.endswith('.pyc') or \
                            f.endswith('.lreg') or f.endswith('.sibling'):
                        try:
                            os.unlink(f)
                        except:
                            pass

        # Remove generated directories
        build = self.get_finalized_command('build')
        build_dir = build.build_base
        if os.path.exists(build_dir):
            try:
                shutil.rmtree(build_dir, ignore_errors=True)
            except:
                pass
        if self.distribution.subpackages != None:
            for idx in range(len(sys.argv)):
                if 'setup.py' in sys.argv[idx]:
                    break
            argv = list(sys.argv[idx+1:])
            process_subpackages(build.distribution.parallel_build, 'clean',
                                build.build_base, self.distribution.subpackages,
                                argv, False)

        # Remove user-specified generated files
        if self.distribution.generated_files != None:
            for path in self.distribution.generated_files:
                if os.path.isfile(path) or os.path.islink(path):
                    try:
                        os.unlink(path)
                    except:
                        pass
                elif os.path.isdir(path):
                    try:
                        shutil.rmtree(path, ignore_errors=True)
                    except:
                        pass

        old_clean.run(self)
        util.delete_cache()
