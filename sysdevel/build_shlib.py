"""
'build_shlib' command for *shared* (non-python) libraries
"""

have_numpy = False
try:
    from numpy.distutils.command.build_clib import *
    from numpy.distutils.misc_util import get_numpy_include_dirs
    have_numpy = True
except:
    from distutils.command.build_clib import *

from util import convert_ulist

class build_shlib(build_clib):
    '''
    Build *shared* libraries for use in Python extensions
    '''
    def finalize_options (self):
        build_clib.finalize_options(self)
        self.libraries = self.distribution.sh_libraries
        self.install_shared_libraries = []
        ## prevent collision
        self.build_temp = os.path.join(self.build_temp, 'shared')
        if self.libraries and len(self.libraries) > 0:
            self.check_library_list(self.libraries)
            from distutils.ccompiler import new_compiler
            compiler = new_compiler(compiler=self.compiler)
            compiler.customize(self.distribution,
                               need_cxx=self.have_cxx_sources())
            static_libraries = self.distribution.libraries
            for lib in self.libraries:
                target_lib = compiler.library_filename(lib[0],
                                                       lib_type='shared',
                                                       output_dir='')
                self.install_shared_libraries.append((lib[1]['package'],
                                                      target_lib))

    def build_libraries(self, libraries):
        if self.libraries and len(self.libraries) > 0:
            for (lib_name, build_info) in libraries:
                ## Special defines
                env = self.distribution.environment
                key = lib_name + '_DEFINES'
                if env and key in env:
                    extra_preargs = build_info.get('extra_compiler_args') or []
                    install_data = self.get_finalized_command('install_data')
                    for define in env[key]:
                        template = define[0]
                        insert = util.safe_eval(define[1])
                        arg = template.replace('@@def@@', insert)
                        extra_preargs.append(arg)
                    build_info['extra_compiler_args'] = extra_preargs
                self.build_a_library(build_info, lib_name, libraries)


    def build_a_library(self, build_info, lib_name, libraries):
        libraries = convert_ulist(build_info.get('libraries') or [])
        library_dirs = convert_ulist(build_info.get('library_dirs') or [])
        runtime_library_dirs = convert_ulist(build_info.get('runtime_library_dirs'))
        extra_preargs = build_info.get('extra_compiler_args') or []
        extra_postargs = build_info.get('extra_link_args') or []

        ## Conditional recompile
        target_library = self.compiler.library_filename(lib_name,
                                                        lib_type='shared',
                                                        output_dir='')
        target_path = os.path.join(self.build_clib, target_library)
        recompile = False
        if not os.path.exists(target_path) or self.force:
            recompile = True
        else:
            for src in build_info.get('sources'):
                if os.path.getmtime(target_path) < os.path.getmtime(src):
                    recompile = True
                    break
        if not recompile:
            return

        library_dirs += [self.build_clib]


        ########################################
        ## Copied verbatim from numpy.distutils.command.build_clib

        # default compilers
        compiler = self.compiler
        fcompiler = self.fcompiler

        sources = build_info.get('sources')
        if sources is None or not is_sequence(sources):
            raise DistutilsSetupError, \
                  ("in 'libraries' option (library '%s'), " +
                   "'sources' must be present and must be " +
                   "a list of source filenames") % lib_name
        sources = list(sources)

        c_sources, cxx_sources, f_sources, fmodule_sources \
                   = filter_sources(sources)
        requiref90 = not not fmodule_sources or \
                     build_info.get('language','c')=='f90'

        # save source type information so that build_ext can use it.
        source_languages = []
        if c_sources: source_languages.append('c')
        if cxx_sources: source_languages.append('c++')
        if requiref90: source_languages.append('f90')
        elif f_sources: source_languages.append('f77')

        specified = build_info.get('language', None)
        if specified:
            source_languages.append(specified)
            if specified == 'c++':  ## force c++ compiler
                cxx_sources += c_sources
                c_sources = []
        build_info['source_languages'] = source_languages

        lib_file = compiler.library_filename(lib_name, lib_type='shared',
                                             output_dir=self.build_clib)
        depends = sources + build_info.get('depends',[])
        if not (self.force or newer_group(depends, lib_file, 'newer')):
            log.debug("skipping '%s' library (up-to-date)", lib_name)
            return
        else:
            log.info("building '%s' library", lib_name)

        if have_numpy:
            config_fc = build_info.get('config_fc',{})
            if fcompiler is not None and config_fc:
                log.info('using additional config_fc from setup script '\
                             'for fortran compiler: %s' \
                             % (config_fc,))
                from numpy.distutils.fcompiler import new_fcompiler
                fcompiler = new_fcompiler(compiler=fcompiler.compiler_type,
                                          verbose=self.verbose,
                                          dry_run=self.dry_run,
                                          force=self.force,
                                          requiref90=requiref90,
                                          c_compiler=self.compiler)
                if fcompiler is not None:
                    dist = self.distribution
                    base_config_fc = dist.get_option_dict('config_fc').copy()
                    base_config_fc.update(config_fc)
                    fcompiler.customize(base_config_fc)

            # check availability of Fortran compilers
            if (f_sources or fmodule_sources) and fcompiler is None:
                ver = '77'
                if requiref90:
                    ver = '90'
                raise DistutilsError, "library %s has Fortran%s sources"\
                    " but no Fortran compiler found" % (lib_name, ver)

        if fcompiler is not None:
            fcompiler.extra_f77_compile_args = build_info.get('extra_f77_compile_args') or []
            fcompiler.extra_f90_compile_args = build_info.get('extra_f90_compile_args') or []

        macros = build_info.get('macros')
        include_dirs = build_info.get('include_dirs')
        if include_dirs is None:
            include_dirs = []
        extra_postargs = build_info.get('extra_compiler_args') or []

        if have_numpy:
            include_dirs.extend(get_numpy_include_dirs())
        # where compiled F90 module files are:
        module_dirs = build_info.get('module_dirs') or []
        module_build_dir = os.path.dirname(lib_file)
        if requiref90: self.mkpath(module_build_dir)

        if compiler.compiler_type=='msvc':
            # this hack works around the msvc compiler attributes
            # problem, msvc uses its own convention :(
            c_sources += cxx_sources
            cxx_sources = []

        objects = []
        if c_sources:
            log.info("compiling C sources")
            objects = compiler.compile(c_sources,
                                       output_dir=self.build_temp,
                                       macros=macros,
                                       include_dirs=include_dirs,
                                       debug=self.debug,
                                       extra_postargs=extra_postargs)

        if cxx_sources:
            log.info("compiling C++ sources")
            cxx_compiler = compiler.cxx_compiler()
            cxx_objects = cxx_compiler.compile(cxx_sources,
                                               output_dir=self.build_temp,
                                               macros=macros,
                                               include_dirs=include_dirs,
                                               debug=self.debug,
                                               extra_postargs=extra_postargs)
            objects.extend(cxx_objects)

        if f_sources or fmodule_sources:
            extra_postargs = []
            f_objects = []

            if requiref90:
                # FIXME breaks under numpy 1.7
                if fcompiler.module_dir_switch is None:
                    existing_modules = glob('*.mod')
                extra_postargs += fcompiler.module_options(\
                    module_dirs,module_build_dir)

            if fmodule_sources:
                log.info("compiling Fortran 90 module sources")
                f_objects += fcompiler.compile(fmodule_sources,
                                               output_dir=self.build_temp,
                                               macros=macros,
                                               include_dirs=include_dirs,
                                               debug=self.debug,
                                               extra_postargs=extra_postargs)

            if requiref90 and self.fcompiler.module_dir_switch is None:
                # move new compiled F90 module files to module_build_dir
                for f in glob('*.mod'):
                    if f in existing_modules:
                        continue
                    t = os.path.join(module_build_dir, f)
                    if os.path.abspath(f)==os.path.abspath(t):
                        continue
                    if os.path.isfile(t):
                        os.remove(t)
                    try:
                        self.move_file(f, module_build_dir)
                    except DistutilsFileError:
                        log.warn('failed to move %r to %r' \
                                 % (f, module_build_dir))

            if f_sources:
                log.info("compiling Fortran sources")
                f_objects += fcompiler.compile(f_sources,
                                               output_dir=self.build_temp,
                                               macros=macros,
                                               include_dirs=include_dirs,
                                               debug=self.debug,
                                               extra_postargs=extra_postargs)
        else:
            f_objects = []

        objects.extend(f_objects)

        # assume that default linker is suitable for
        # linking Fortran object files
        ########################################

        link_compiler = compiler
        if cxx_sources:
            link_compiler = cxx_compiler
        extra_postargs = build_info.get('extra_link_args') or []

        ## May be dependent on other libs we're builing
        shlib_libraries = []
        for libinfo in build_info.get('libraries',[]):
            if isinstance(libinfo, basestring):
                shlib_libraries.append(libinfo)
            else:
                shlib_libraries.append(libinfo[0])

        ## Alternate ending
        link_compiler.link(
            target_desc          = link_compiler.SHARED_LIBRARY,
            objects              = objects,
            output_filename      = target_library,
            output_dir           = self.build_clib,
            libraries            = shlib_libraries,
            library_dirs         = library_dirs,
            runtime_library_dirs = runtime_library_dirs,
            debug                = self.debug,
            extra_preargs        = extra_preargs,
            extra_postargs       = extra_postargs,
            )
