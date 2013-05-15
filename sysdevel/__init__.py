"""
sysdevel package

The sysdevel package facilitates multi-model simulation development in three
areas: model coupling, data visualization, and collaboration & distribution.
"""


__all__ = ['pkg_config', 'core', 'extensions',
           'config_cc', 'config_fc', 'build_clib', 'build_doc', 'build_exe',
           'build_js', 'build_pypp_ext', 'build_py', 'build_scripts',
           'build_shlib', 'build_src', 'install_clib', 'install_data',
           'install_exe', 'install_lib', 'util', 'tree',
           'configuration', 'configure',]

import os

config_dir = os.path.join(os.path.dirname(__file__), 'configure')
support_dir = os.path.join(os.path.dirname(__file__), 'support')
using_setuptools = False

def use_setuptools():
    global using_setuptools
    using_setuptools = True

from configure import configure_system, FatalError

