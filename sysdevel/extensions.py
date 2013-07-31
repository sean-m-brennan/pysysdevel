"""
Copyright 2013.  Los Alamos National Security, LLC. This material was
produced under U.S. Government contract DE-AC52-06NA25396 for Los
Alamos National Laboratory (LANL), which is operated by Los Alamos
National Security, LLC for the U.S. Department of Energy. The
U.S. Government has rights to use, reproduce, and distribute this
software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS NATIONAL SECURITY,
LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY
FOR THE USE OF THIS SOFTWARE.  If software is modified to produce
derivative works, such modified software should be clearly marked, so
as not to confuse it with the version available from LANL.

Licensed under the Mozilla Public License, Version 2.0 (the
"License"); you may not use this file except in compliance with the
License. You may obtain a copy of the License at
http://www.mozilla.org/MPL/2.0/

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
implied. See the License for the specific language governing
permissions and limitations under the License.
"""

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
## Javascript unit tests are a list of QUnit HTML files.

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
