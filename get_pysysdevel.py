import os
import sys
import platform
import subprocess

base_dir = os.path.abspath(os.path.dirname(__file__))

try:
    import sysdevel
except:
    if not os.path.exists(os.path.join(base_dir, 'pysysdevel')):
        shell = False
        if 'windows' in platform.system().lower():
            shell = True
        #FIXME change to base_dir and back
        here = os.path.abspath(os.getcwd())
        os.chdir(base_dir)
        subprocess.check_call(['git', 'clone',
                               'http://github.com/sean-m-brennan/pysysdevel.git'
                               ], shell=shell)
        os.chdir(here)

    sys.path.insert(0, os.path.join(base_dir, 'pysysdevel'))
