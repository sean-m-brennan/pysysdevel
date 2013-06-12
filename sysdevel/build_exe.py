"""
'build_exe' command for (non-python) executables
"""

import os
from glob import glob
from distutils.errors import DistutilsSetupError, DistutilsError, \
     DistutilsFileError
from distutils.dep_util import newer_group

have_numpy = False
try:
    from numpy.distutils.command.build_clib import build_clib
    from numpy.distutils.misc_util import get_numpy_include_dirs
    from numpy.distutils import log
    have_numpy = True
except:
    from distutils.command.build_clib import build_clib
    from distutils import log

from util import convert_ulist, has_f_sources, has_cxx_sources, \
    filter_sources, is_sequence, all_strings


class build_exe(build_clib):
    '''
    Build executables
    '''
    def finalize_options (self):
        build_clib.finalize_options(self)
        self.executables = self.distribution.native_executables
        self.install_executables = []
        self.libraries = []  ## required!
        if self.executables and len(self.executables) > 0:
            from distutils.ccompiler import new_compiler
            compiler = new_compiler(compiler=self.compiler)
            compiler.customize(self.distribution,
                               need_cxx=self.have_cxx_sources())
            exe_extension = compiler.exe_extension or ''
            for exe in self.executables:
                self.install_executables.append(exe.name + exe_extension)


    def have_f_sources(self):
        for exe in self.executables:
            if has_f_sources(exe.sources):
                return True
        return False

    def have_cxx_sources(self):
        for exe in self.executables:
            if has_cxx_sources(exe.sources):
                return True
        return False


    def run(self):
        if not self.executables:
            return

        # Make sure that library sources are complete.
        languages = []
        for exe in self.executables:
            if not all_strings(exe.sources):
                self.run_command('build_src')
            l = exe.language
            if l and l not in languages: languages.append(l)

        from distutils.ccompiler import new_compiler
        self.compiler = new_compiler(compiler=self.compiler,
                                     dry_run=self.dry_run,
                                     force=self.force)
        self.compiler.customize(self.distribution,
                                need_cxx=self.have_cxx_sources())

        self.compiler.customize_cmd(self)
        self.compiler.show_customization()

        if have_numpy and self.have_f_sources():
            from numpy.distutils.fcompiler import new_fcompiler
            self.fcompiler = new_fcompiler(compiler=self.fcompiler,
                                           verbose=self.verbose,
                                           dry_run=self.dry_run,
                                           force=self.force,
                                           requiref90='f90' in languages,
                                           c_compiler=self.compiler)
            if self.fcompiler is not None:
                self.fcompiler.customize(self.distribution)

                self.fcompiler.customize_cmd(self)
                self.fcompiler.show_customization()



        exes = []
        for exe in self.executables:
            libraries = exe.libraries or []
            library_dirs = exe.library_dirs or []
            runtime_library_dirs = exe.runtime_library_dirs or []
            extra_preargs = exe.extra_compile_args or []
            extra_postargs = exe.extra_link_args or []

            ## include libraries built by build_shlib and/or build_clib
            library_dirs.append(self.build_temp)

            ## Conditional recompile
            build_directory = self.build_clib
            target_path = os.path.join(build_directory, exe.name)
            recompile = False
            if not os.path.exists(target_path) or self.force:
                recompile = True
            else:
                for src in exe.sources:
                    if os.path.getmtime(target_path) < os.path.getmtime(src):
                        recompile = True
                        break
            if not recompile:
                return

            ########################################
            ## Copied from numpy.distutils.command.build_clib

            # default compilers
            compiler = self.compiler
            fcompiler = self.fcompiler

            sources = exe.sources
            if sources is None or not is_sequence(sources):
                raise DistutilsSetupError, \
                    ("in 'libraries' option (library '%s'), " +
                     "'sources' must be present and must be " +
                     "a list of source filenames") % exe.name
            sources = list(sources)

            c_sources, cxx_sources, f_sources, fmodule_sources \
                = filter_sources(sources)
            if not exe.language:
                exe.language = 'c'
            requiref90 = not not fmodule_sources or exe.language =='f90'

            # save source type information so that build_ext can use it.
            source_languages = []
            if c_sources: source_languages.append('c')
            if cxx_sources: source_languages.append('c++')
            if requiref90: source_languages.append('f90')
            elif f_sources: source_languages.append('f77')
            exe.source_languages = source_languages

            lib_file = compiler.library_filename(exe.name,
                                                 output_dir=build_directory)
            depends = sources + (exe.depends or [])
            if not (self.force or newer_group(depends, lib_file, 'newer')):
                log.debug("skipping '%s' library (up-to-date)", exe.name)
                return
            else:
                log.info("building '%s' library", exe.name)

            if have_numpy:
                config_fc = exe.config_fc or {}
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
                    raise DistutilsError, "library %s has Fortran sources"\
                        " but no Fortran compiler found" % (exe.name)

            macros = exe.define_macros
            include_dirs = exe.include_dirs
            if include_dirs is None:
                include_dirs = []

            if have_numpy:
                include_dirs.extend(get_numpy_include_dirs())
            # where compiled F90 module files are:
            module_dirs = exe.module_dirs or []
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

            ## May be dependent on other libs we're builing
            shlib_libraries = []
            for libinfo in exe.libraries:
                if isinstance(libinfo, basestring):
                    shlib_libraries.append(convert_ulist([libinfo])[0])
                else:
                    shlib_libraries.append(libinfo[0])

            ## Alternate ending
            link_compiler.link(
                target_desc          = link_compiler.EXECUTABLE,
                objects              = objects,
                output_filename      = exe.name,
                output_dir           = build_directory,
                libraries            = shlib_libraries,
                library_dirs         = library_dirs,
                runtime_library_dirs = runtime_library_dirs,
                debug                = self.debug,
                extra_preargs        = extra_preargs,
                extra_postargs       = extra_postargs,
                )
