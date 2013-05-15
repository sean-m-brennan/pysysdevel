"""
Custom C/C++ compiler config
"""

import platform

from distutils import log
try:
    from numpy.distutils.command.config_compiler import config_cc as old_config_cc
except:
    from distutils.command.config_compiler import config_cc as old_config_cc


class config_cc(old_config_cc):
    def finalize_options(self):
        ## force cached compiler
        if 'windows' in platform.system().lower():
            env = self.distribution.environment
            if 'COMPILER' in env:
                self.compiler = env['COMPILER'].encode('ascii', 'ignore')

        ## *nearly* identical to that in the numpy original
        log.info('unifing config_cc, config, build_clib, build_shlib, ' +
                 'build_ext, build commands --compiler options')
        build_clib = self.get_finalized_command('build_clib')
        build_shlib = self.get_finalized_command('build_shlib')
        build_ext = self.get_finalized_command('build_ext')
        config = self.get_finalized_command('config')
        build = self.get_finalized_command('build')
        cmd_list = [self, config, build_clib, build_shlib, build_ext, build]
        for a in ['compiler']:
            l = []
            for c in cmd_list:
                v = getattr(c,a)
                if v is not None:
                    if not isinstance(v, str): v = v.compiler_type
                    if v not in l: l.append(v)
            if not l: v1 = None
            else: v1 = l[0]
            if len(l)>1:
                log.warn('  commands have different --%s options: %s'\
                         ', using first in list as default' % (a, l))
            if v1:
                for c in cmd_list:
                    if getattr(c,a) is None: setattr(c, a, v1)
        return
