"""
Custom extensions
"""

try:
    from numpy.distutils import extension as old_extension
except:
    from distutils import extension as old_extension

import util


## Shared libraries, like static libraries, consist of
##  a name and a build_info dictionary.


class Extension(old_extension.Extension):
    def __init__(self, name, sources,
                 include_dirs=None,
                 define_macros=None,
                 undef_macros=None,
                 library_dirs=None,
                 libraries=None,
                 runtime_library_dirs=None,
                 extra_objects=None,
                 extra_compile_args=None,
                 extra_link_args=None,
                 export_symbols=None,
                 swig_opts=None,
                 depends=None,
                 language=None,
                 f2py_options=None,
                 module_dirs=None,):
        old_extension.Extension.__init__(self, name, sources,
                                     include_dirs, define_macros, undef_macros,
                                     util.convert_ulist(library_dirs),
                                     util.convert_ulist(libraries),
                                     util.convert_ulist(runtime_library_dirs),
                                     extra_objects,
                                     extra_compile_args, extra_link_args,
                                     export_symbols, swig_opts, depends,
                                     language, f2py_options, module_dirs,)


class WebExtension(old_extension.Extension):
    def __init__(self, name, sources, source_dir,
                 public_subdir='', extra_support_files=[],
                 extra_public_files=[], extra_compile_args=[],
                 compiler=None):
        old_extension.Extension.__init__(self, name, sources)
        self.source_directory = source_dir
        self.public_subdir = public_subdir
        self.extra_support_files = extra_support_files
        self.extra_public_files = extra_public_files
        self.compiler = compiler
        self.extra_compile_args = extra_compile_args


class DocExtension(old_extension.Extension):
    def __init__(self, name, source_dir, sphinx_cfg=None,
                 doxy_cfg=None, doxy_srcs=[], extra_docs = [],
                 extra_directories=[], no_sphinx=False,
                 style=util.DEFAULT_STYLE):
        old_extension.Extension.__init__(self, name, [])
        self.source_directory = source_dir
        self.sphinx_config = sphinx_cfg
        self.doxygen_cfg = doxy_cfg
        self.doxygen_srcs = doxy_srcs
        self.extra_docs = extra_docs
        self.extra_directories = extra_directories
        self.without_sphinx = no_sphinx
        self.style = style


class AntlrGrammar(old_extension.Extension):
    def __init__(self, name, directory, sources):
        old_extension.Extension.__init__(self, name, sources)
        self.directory = directory


class PyPlusPlusExtension(old_extension.Extension):
    def __init__(self, name, sources,
                 pypp_file, binding_file,
                 include_dirs=None,
                 define_macros=None,
                 undef_macros=None,
                 library_dirs=None,
                 libraries=None,
                 runtime_library_dirs=None,
                 extra_objects=None,
                 extra_compile_args=None,
                 extra_link_args=None,
                 export_symbols=None,
                 swig_opts=None,
                 depends=None,
                 language=None,
                 f2py_options=None,
                 module_dirs=None,):
        old_extension.Extension.__init__(self, name, sources,
                                     include_dirs, define_macros, undef_macros,
                                     util.convert_ulist(library_dirs),
                                     util.convert_ulist(libraries),
                                     util.convert_ulist(runtime_library_dirs),
                                     extra_objects,
                                     extra_compile_args, extra_link_args,
                                     export_symbols, swig_opts, depends,
                                     language, f2py_options, module_dirs,)
        self.pyppdef = pypp_file
        self.binding_file = binding_file
        self.builder = ''


class Executable(old_extension.Extension):
    ## make sure it matches extension signature
    def __init__(self, name, sources,
                 include_dirs=None,
                 define_macros=None,
                 undef_macros=None,
                 library_dirs=None,
                 libraries=None,
                 runtime_library_dirs=None,
                 extra_objects=None,
                 extra_compile_args=None,
                 extra_link_args=None,
                 export_symbols=None,
                 swig_opts=None,
                 depends=None,
                 language=None,
                 f2py_options=None,
                 module_dirs=None,
                 link_with_fcompiler=False,):
        self.config_fc = dict()
        self.source_languages = []
        self.link_with_fcompiler = link_with_fcompiler
        old_extension.Extension.__init__(self, name, sources,
                                     include_dirs, define_macros, undef_macros,
                                     util.convert_ulist(library_dirs),
                                     util.convert_ulist(libraries),
                                     util.convert_ulist(runtime_library_dirs),
                                     extra_objects,
                                     extra_compile_args, extra_link_args,
                                     export_symbols, swig_opts, depends,
                                     language, f2py_options, module_dirs,)


## Unit test suites are tuples, consisting of a name and a list of unit tests:
##  either python, fortran or c/c++.

## Python unit tests are a list of unit test modules.


class FortranUnitTest(Executable):
    def __init__(self, testfile, extra_sources=[],
                 include_dirs=None,
                 define_macros=None,
                 undef_macros=None,
                 library_dirs=None,
                 libraries=None,
                 runtime_library_dirs=None,
                 extra_objects=None,
                 extra_compile_args=None,
                 extra_link_args=None,
                 export_symbols=None,
                 swig_opts=None,
                 depends=None,
                 language=None,
                 f2py_options=None,
                 module_dirs=None,):
        name = os.path.splitext(testfile)[0]
        sources = [testfile] + extra_sources
        Executable.__init__(self, name, sources,
                            include_dirs, define_macros, undef_macros,
                            util.convert_ulist(library_dirs),
                            util.convert_ulist(libraries),
                            util.convert_ulist(runtime_library_dirs),
                            extra_objects,
                            extra_compile_args, extra_link_args,
                            export_symbols, swig_opts, depends,
                            language, f2py_options, module_dirs, True)


class CUnitTest(Executable):
    def __init__(self, testfile, extra_sources=[],
                 include_dirs=None,
                 define_macros=None,
                 undef_macros=None,
                 library_dirs=None,
                 libraries=None,
                 runtime_library_dirs=None,
                 extra_objects=None,
                 extra_compile_args=None,
                 extra_link_args=None,
                 export_symbols=None,
                 swig_opts=None,
                 depends=None,
                 language=None,
                 f2py_options=None,
                 module_dirs=None,):
        name = os.path.splitext(testfile)[0]
        sources = [testfile] + extra_sources
        Executable.__init__(self, name, sources,
                            include_dirs, define_macros, undef_macros,
                            util.convert_ulist(library_dirs),
                            util.convert_ulist(libraries),
                            util.convert_ulist(runtime_library_dirs),
                            extra_objects,
                            extra_compile_args, extra_link_args,
                            export_symbols, swig_opts, depends,
                            language, f2py_options, module_dirs,)


class CppUnitTest(Executable):
    def __init__(self, testfile, extra_sources=[],
                 include_dirs=None,
                 define_macros=None,
                 undef_macros=None,
                 library_dirs=None,
                 libraries=None,
                 runtime_library_dirs=None,
                 extra_objects=None,
                 extra_compile_args=None,
                 extra_link_args=None,
                 export_symbols=None,
                 swig_opts=None,
                 depends=None,
                 language=None,
                 f2py_options=None,
                 module_dirs=None,):
        name = os.path.splitext(testfile)[0]
        sources = [testfile] + extra_sources
        Executable.__init__(self, name, sources,
                            include_dirs, define_macros, undef_macros,
                            util.convert_ulist(library_dirs),
                            util.convert_ulist(libraries),
                            util.convert_ulist(runtime_library_dirs),
                            extra_objects,
                            extra_compile_args, extra_link_args,
                            export_symbols, swig_opts, depends,
                            language, f2py_options, module_dirs,)
