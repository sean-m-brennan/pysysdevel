# -*- coding: utf-8 -*-
"""
Custom Fortran compiler config
"""
#**************************************************************************
# 
# This material was prepared by the Los Alamos National Security, LLC 
# (LANS), under Contract DE-AC52-06NA25396 with the U.S. Department of 
# Energy (DOE). All rights in the material are reserved by DOE on behalf 
# of the Government and LANS pursuant to the contract. You are authorized 
# to use the material for Government purposes but it is not to be released 
# or distributed to the public. NEITHER THE UNITED STATES NOR THE UNITED 
# STATES DEPARTMENT OF ENERGY, NOR LOS ALAMOS NATIONAL SECURITY, LLC, NOR 
# ANY OF THEIR EMPLOYEES, MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR 
# ASSUMES ANY LEGAL LIABILITY OR RESPONSIBILITY FOR THE ACCURACY, 
# COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, PRODUCT, OR 
# PROCESS DISCLOSED, OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE 
# PRIVATELY OWNED RIGHTS.
# 
#**************************************************************************

try:
    import os
    import platform
    from numpy.distutils import log
    from numpy.distutils.command.config_compiler import config_fc as old_cfg_fc

    class config_fc(old_cfg_fc):
        def initialize_options(self):
            old_cfg_fc.initialize_options(self)
            """ FIXME set this in build_shlib
            try:
                old_ldflags = os.environ['LDFLAGS']
            except:
                old_ldflags = ''
            if not 'darwin' in platform.system().lower():
                os.environ['LDFLAGS'] = old_ldflags + ' -shared'
            """

        def finalize_options(self):
            """ Perhaps not necessary? (potential OSX problem)
            if ((self.f77exec is None and self.f90exec is None) or \
                'gfortran' in self.f77exec or 'gfortran' in self.f90exec) and \
                'darwin' in platform.system().lower():
                ## Unify GCC and GFortran default outputs
                if util.gcc_is_64bit():
                    os.environ['FFLAGS'] = '-arch x86_64'
                    os.environ['FCFLAGS'] = '-arch x86_64'
                else:
                    os.environ['FFLAGS'] = '-arch i686'
                    os.environ['FCFLAGS'] = '-arch i686'
                """

            # the rest is *nearly* identical to that in the numpy original
            log.info('unifing config_fc, config, build_clib, build_shlib, ' +
                     'build_ext, build commands --fcompiler options')
            build_clib = self.get_finalized_command('build_clib')
            build_shlib = self.get_finalized_command('build_shlib')
            build_ext = self.get_finalized_command('build_ext')
            config = self.get_finalized_command('config')
            build = self.get_finalized_command('build')
            cmd_list = [self, config,
                        build_clib, build_shlib, build_ext, build]
            for a in ['fcompiler']:
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

except:
    from distutils.core import Command

    class config_fc(Command):
        """
        NumPy is not present, this is a dummy command.
        """
        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            pass
