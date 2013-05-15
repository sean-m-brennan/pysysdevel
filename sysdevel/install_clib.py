"""
Flexible install_clib command
"""

try:
    from numpy.distutils.command.install_clib import install_clib

except:
    from distutils.core import Command

    class install_clib(Command):
        """
        NumPy is not present, this is a dummy command.
        """
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        pass
