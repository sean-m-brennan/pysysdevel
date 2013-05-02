# -*- coding: utf-8 -*-
"""
Custom setup
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

import sys

if True: #sys.version_info > (2, 5):
    try:
        # Must be first (get the monkeypatching out of the way)
        import setuptools
    except:
        pass  # setuptools plus earlier python do not mix well

import shutil
import os
import platform
import subprocess
import glob

from distutils.core import Command
from distutils.command.clean import clean as old_clean

have_numpy = False
try:
    from numpy.distutils.numpy_distribution import NumpyDistribution as oldDistribution
    from numpy.distutils.command.build import build as old_build
    from numpy.distutils.command.install import install as old_install
    from numpy.distutils.command.sdist import sdist as old_sdist
    from numpy.distutils.command import config, build_ext, install_headers
    from numpy.distutils.command import bdist_rpm, scons
    have_numpy = True

except ImportError, e:
    print 'NumPy not found. Failover to distutils alone.'
    from distutils.dist import Distribution as oldDistribution
    from distutils.command.build import build as old_build
    from distutils.command.install import install as old_install
    from distutils.command.sdist import sdist as old_sdist
    from distutils.command import config, build_ext, install_headers, bdist_rpm

import util



class CustomDistribution(oldDistribution):
    '''
    Subclass Distribution to support new commands
    '''
    def __init__(self, attrs=None):
        old_attrs = attrs
        ## setup the environment for custom commands
        self.environment = attrs.get('environment')
        if self.environment != None:
            del old_attrs['environment']
        else:
            self.environment = dict()
        ## PYJS web extensions
        self.web_ext_modules = attrs.get('web_ext_modules')
        if self.web_ext_modules != None:
            del old_attrs['web_ext_modules']
        ## Sphinx documentation
        self.doc_modules = attrs.get('doc_modules')
        if self.doc_modules != None:
            del old_attrs['doc_modules']
        ## Py++ extensions
        self.pypp_ext_modules = attrs.get('pypp_ext_modules')
        if self.pypp_ext_modules != None:
            del old_attrs['pypp_ext_modules']
        ## Shared libraries
        self.sh_libraries = attrs.get('sh_libraries')
        if self.sh_libraries != None:
            del old_attrs['sh_libraries']
        ## ANTLR parser/lexers
        self.antlr_modules = attrs.get('antlr_modules')
        if self.antlr_modules != None:
            del old_attrs['antlr_modules']
        ## Native executables
        self.native_executables = attrs.get('native_executables')
        if self.native_executables != None:
            del old_attrs['native_executables']
        ## Data to install to 'share'
        self.data_dirs = attrs.get('data_dirs')
        if self.data_dirs != None:
            del old_attrs['data_dirs']
        ## Non-stock libraries to install to 'lib' or 'lib64'
        self.extra_install_libraries = attrs.get('extra_install_libraries')
        if self.extra_install_libraries != None:
            del old_attrs['extra_install_libraries']
        ## Non-stock python packages to co-install
        self.extra_install_modules = attrs.get('extra_install_modules')
        if self.extra_install_modules != None:
            del old_attrs['extra_install_modules']
        ## Boilerplate scripts to create
        self.create_scripts = attrs.get('create_scripts')
        if self.create_scripts != None:
            del old_attrs['create_scripts']
        ## SysDevel support modules
        self.devel_support = attrs.get('devel_support')
        if self.devel_support != None:
            del old_attrs['devel_support']
        ## Files to delete upon 'clean'
        self.generated_files = attrs.get('generated_files')
        if self.generated_files != None:
            del old_attrs['generated_files']
        ## Separate packages with their own setup.py
        self.subpackages = attrs.get('subpackages')
        if self.subpackages != None:
            del old_attrs['subpackages']
        ## Whether to quit if a subpackage build fails
        self.quit_on_error = attrs.get('quit_on_error')
        if self.quit_on_error != None:
            del old_attrs['quit_on_error']
        ## Enable parallel building
        self.parallel_build = attrs.get('parallel_build')
        if self.parallel_build != None:
            del old_attrs['parallel_build']
        ## Unit testing
        self.tests = attrs.get('tests')
        if self.tests != None:
            del old_attrs['tests']

        ## py2exe options
        self.ctypes_com_server = attrs.pop("ctypes_com_server", [])
        self.com_server = attrs.pop("com_server", [])
        self.service = attrs.pop("service", [])
        self.windows = attrs.pop("windows", [])
        self.console = attrs.pop("console", [])
        self.isapi = attrs.pop("isapi", [])
        self.zipfile = attrs.pop("zipfile", util.default_py2exe_library)

        oldDistribution.__init__(self, old_attrs)

    def has_scripts(self):
        return oldDistribution.has_scripts(self) or \
            (self.create_scripts != None and len(self.create_scripts) > 0)

    def has_c_libraries(self):
        return oldDistribution.has_c_libraries(self) or self.has_shared_libs()

    def has_shared_libs(self):
        return (self.sh_libraries != None and len(self.sh_libraries) > 0) or \
            (self.extra_install_libraries != None and
             len(self.extra_install_libraries) > 0)

    def has_antlr_extensions(self):
        return self.antlr_modules != None and len(self.antlr_modules) > 0

    def has_sysdevel_support(self):
        return self.devel_support != None and len(self.devel_support) > 0

    def has_pypp_extensions(self):
        return self.pypp_ext_modules != None and \
            len(self.pypp_ext_modules) > 0

    def has_web_extensions(self):
        return self.web_ext_modules != None and len(self.web_ext_modules) > 0

    def has_documents(self):
        return self.doc_modules != None and len(self.doc_modules) > 0

    def has_executables(self):
        return self.native_executables != None and \
            len(self.native_executables) > 0

    def has_data_directories(self):
        return self.data_dirs != None and len(self.data_dirs) > 0




def process_package(fnctn, build_base, progress, pyexe, argv,
                    pkg_name, pkg_dir, addtnl_args=[]):
    sys.stdout.write(fnctn.upper() + 'ING ' + pkg_name + ' in ' + pkg_dir + ' ')
    logging = True
    if 'clean' in fnctn:
        logging = False
    log_file = os.path.join(build_base, pkg_name + '_' + fnctn + '.log')
    if logging:
        log = open(log_file, 'w')
    else:
        log = open(os.devnull, 'w')
    try:
        p = subprocess.Popen([pyexe, os.path.join(pkg_dir, 'setup.py'),
                              ] + argv + addtnl_args,
                             stdout=log, stderr=log)
        status = progress(p)
        log.close()
    except KeyboardInterrupt:
        p.terminate()
        log.close()
        status = 1
    if status != 0:
        sys.stdout.write(' failed')
        if logging:
            sys.stdout.write('; See ' + log_file)
    else:
        sys.stdout.write(' done')
    sys.stdout.write('\n')           
    return pkg_name, status


def process_subpackages(parallel, fnctn, build_base, subpackages,
                        argv, quit_on_error):
    try:
        if not parallel:
            raise ImportError
        ## parallel
        import pp
        job_server = pp.Server()
        results = [job_server.submit(process_package,
                                     (fnctn, build_base, util.process_progress,
                                      sys.executable, argv,) + sub,
                                     (), ('os', 'subprocess',))
                   for sub in subpackages]
        has_failed = False
        for result in results:
            res_tpl = result()
            if res_tpl is None:
                raise Exception("Parallel build failed.")
            pkg_name, status = res_tpl
            if status != 0 and quit_on_error:
                has_failed = True
            if has_failed:
                sys.exit(status)
    except ImportError: ## serial
        for sub in subpackages:
            args = (fnctn, build_base, util.process_progress,
                    sys.executable, argv,) + sub
            pkg_name, status = process_package(*args)
            if status != 0 and quit_on_error:
                sys.exit(status)



class build(old_build):
    '''
    Subclass build command to support new commands.
    '''
    def has_pure_modules(self):
        return self.distribution.has_pure_modules() or \
            self.distribution.has_antlr_extensions() or \
            self.distribution.has_sysdevel_support()

    def has_scripts(self):
        return self.distribution.has_scripts()

    def has_c_libraries(self):
        return self.distribution.has_c_libraries()

    def has_shared_libraries(self):
        return self.distribution.has_shared_libs()

    def has_pypp_extensions(self):
        return self.distribution.has_pypp_extensions()

    def has_web_extensions(self):
        return self.distribution.has_web_extensions()

    def has_documents(self):
        return self.distribution.has_documents()

    def has_executables(self):
        return self.distribution.has_executables()

    def has_data(self):
        return self.distribution.has_data_files() or \
            self.distribution.has_data_directories()


    ## Order is important
    sub_commands = [('config_cc',      lambda *args: True),
                    ('config_fc',      lambda *args: True),
                    ('build_src',      old_build.has_ext_modules),
                    ('build_py',       has_pure_modules),
                    ('build_js',       has_web_extensions),
                    ('build_clib',     has_c_libraries),
                    ('build_shlib',    has_shared_libraries),
                    ('build_ext',      old_build.has_ext_modules),
                    ('build_pypp_ext', has_pypp_extensions),
                    ('build_scripts',  has_scripts),
                    ('build_doc',      has_documents),
                    ('build_exe',      has_executables),
                    ]


    def run(self):
        if self.distribution.subpackages != None:
            if self.get_finalized_command('install').ran:
                return  ## avoid build after install
            try:
                os.makedirs(self.build_base)
            except:
                pass
            for idx in range(len(sys.argv)):
                if 'setup.py' in sys.argv[idx]:
                    break
            argv = list(sys.argv[idx+1:])
            if 'install' in argv:
                argv.remove('install')
            if 'clean' in argv:
                argv.remove('clean')

            process_subpackages(self.distribution.parallel_build, 'build',
                                self.build_base, self.distribution.subpackages,
                                argv, self.distribution.quit_on_error)

            if self.has_pure_modules() or self.has_c_libraries() or \
                    self.has_ext_modules() or self.has_shared_libraries() or \
                    self.has_pypp_extensions() or self.has_web_extensions() or \
                    self.has_documents() or self.has_executables() or \
                    self.has_scripts() or self.has_data():
                old_build.run(self)
        else:
            old_build.run(self)


class install(old_install):
    '''
    Subclass install command to support new commands.
    '''
    def initialize_options (self):
        old_install.initialize_options(self)
        self.ran = False

    def has_lib(self):
        return old_install.has_lib(self) or self.distribution.has_shared_libs()

    def has_exe(self):
        return self.distribution.has_executables()

    def has_data(self):
        return self.distribution.has_data_files() or \
            self.distribution.has_data_directories()

    sub_commands = [('install_exe', has_exe),
                    ('install_data', has_data),
                    ('install_lib', has_lib),
                    ('install_headers', old_install.has_headers),
                    ('install_scripts', old_install.has_scripts),
                    #('install_egg_info', lambda self:True),
                    ]

    def run(self):
        if self.distribution.subpackages != None:
            self.ran = True
            build = self.get_finalized_command('build')
            try:
                os.makedirs(build.build_base)
            except:
                pass
            for idx in range(len(sys.argv)):
                if 'setup.py' in sys.argv[idx]:
                    break
            argv = list(sys.argv[idx+1:])
            if 'build' in argv:
                argv.remove('build')
            if 'clean' in argv:
                argv.remove('clean')

            process_subpackages(build.distribution.parallel_build, 'install',
                                build.build_base, self.distribution.subpackages,
                                argv, build.distribution.quit_on_error)

            if build.has_pure_modules() or build.has_c_libraries() or \
                    build.has_ext_modules() or build.has_shared_libraries() or \
                    build.has_pypp_extensions() or \
                    build.has_web_extensions() or \
                    build.has_documents() or build.has_executables() or \
                    build.has_scripts() or build.has_data():
                old_install.run(self)
        else:
            old_install.run(self)


class sdist(old_sdist):
    def get_file_list (self):
        old_sdist.get_file_list(self)
        self.filelist.extend(glob.glob('third_party/*'))

    def run (self):
        ## Bizarrely, the following simply does not work
        ## old_sdist.run(self)
        ## Therefore:
        from distutils.filelist import FileList
        self.filelist = FileList()
        self.check_metadata()
        self.get_file_list()
        if self.manifest_only:
            return
        self.make_distribution()
        


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


class test(Command):
    description = "unit testing"

    user_options = []

    def initialize_options(self):
        self.tests = []

    def finalize_options(self):
        if not self.tests: 
            self.tests = self.distribution.tests

    def run(self):
        if self.tests:
            self.run_command('build')
            build = self.get_finalized_command('build')
            build_dir = build.build_base
            buildpy = self.get_finalized_command('build_py')
            src_dirs = buildpy.package_dir
            environ = self.distribution.environment

            pkg_dirs = [build_dir, build.build_lib,
                        os.path.join(build_dir, 'python')]
            lib_dirs = [build.build_temp]
            try:
                lib_dirs += environ['PATH']
                # FIXME need boost, etc dlls for windows
            except:
                pass
            try:
                lib_dirs.append(os.path.join(environ['MINGW_DIR'], 'bin'))
                lib_dirs.append(os.path.join(environ['MSYS_DIR'], 'bin'))
                lib_dirs.append(os.path.join(environ['MSYS_DIR'], 'lib'))
            except:
                pass
            postfix = '.'.join(build.build_temp.split('.')[1:])
            for pkg, units in self.tests:
                test_dir = os.path.join(build_dir, 'test_' + pkg)
                if not os.path.exists(test_dir):
                    util.copy_tree(os.path.join(src_dirs[pkg], 'test'),
                                   test_dir, excludes=['.svn*', 'CVS*'])
                f = open(os.path.join(test_dir, '__init__.py'), 'w')
                f.write("__all__ = ['" +
                        "', '".join(units) + "']\n")
                f.close()
                outfile = os.path.join(build_dir, 'test_' + pkg + '.py')
                util.create_testscript('test_' + pkg, units, outfile, pkg_dirs)
                wrap = util.create_test_wrapper(outfile, build_dir, lib_dirs)
                log.info('running unit tests for ' + pkg)
                util.check_call([wrap])




##################################################
## Almost verbatim from numpy.disutils.core
##################################################

if 'setuptools' in sys.modules:
    have_setuptools = True
    from setuptools import setup as old_setup
    # easy_install imports math, it may be picked up from cwd
    from setuptools.command import easy_install
    try:
        # very old versions of setuptools don't have this
        from setuptools.command import bdist_egg
    except ImportError:
        have_setuptools = False
else:
    from distutils.core import setup as old_setup
    have_setuptools = False

allows_py2app = False
try:
    from py2app.build_app import py2app
    allows_py2app = True
except:
    pass

import warnings
import distutils.core
import distutils.dist

import config_cc
import config_fc
import build_doc
import build_js
import build_py
import build_scripts
import build_pypp_ext
import build_src
import build_clib
import build_shlib
import build_exe
import install_data
import install_lib
import install_clib
import install_exe

my_cmdclass = {'build':            build,
               'build_src':        build_src.build_src,
               'build_scripts':    build_scripts.build_scripts,
               'config_cc':        config_cc.config_cc,
               'config_fc':        config_fc.config_fc,
               'config':           config.config,
               'build_ext':        build_ext.build_ext,
               'build_py':         build_py.build_py,
               'build_clib':       build_clib.build_clib,
               'build_shlib':      build_shlib.build_shlib,
               'build_js':         build_js.build_js,
               'build_doc':        build_doc.build_doc,
               'build_pypp_ext':   build_pypp_ext.build_pypp_ext,
               'build_exe':        build_exe.build_exe,
               'sdist':            sdist,
               'install_exe':      install_exe.install_exe,
               'install_lib':      install_lib.install_lib,
               'install_clib':     install_clib.install_clib,
               'install_data':     install_data.install_data,
               'install_headers':  install_headers.install_headers,
               'install':          install,
               'bdist_rpm':        bdist_rpm.bdist_rpm,
               'clean':            clean,
               'test':             test,
               }

if have_numpy:
    my_cmdclass['scons']         = scons.scons

if have_setuptools:
    if have_numpy:
        # Use our own versions of develop and egg_info to ensure that build_src
        # is handled appropriately.
        from numpy.distutils.command import develop, egg_info
        
    my_cmdclass['bdist_egg']     = bdist_egg.bdist_egg
    if have_numpy:
        my_cmdclass['develop']   = develop.develop
    my_cmdclass['easy_install']  = easy_install.easy_install
    if have_numpy:
        my_cmdclass['egg_info']  = egg_info.egg_info
    
if allows_py2app:
    my_cmdclass['py2app']        = py2app


def _dict_append(d, **kws):
    for k,v in kws.items():
        if k not in d:
            d[k] = v
            continue
        dv = d[k]
        if isinstance(dv, tuple):
            d[k] = dv + tuple(v)
        elif isinstance(dv, list):
            d[k] = dv + list(v)
        elif isinstance(dv, dict):
            _dict_append(dv, **v)
        elif util.is_string(dv):
            d[k] = dv + v
        else:
            raise TypeError, repr(type(dv))

def _command_line_ok(_cache=[]):
    """ Return True if command line does not contain any
    help or display requests.
    """
    if _cache:
        return _cache[0]
    ok = True
    display_opts = ['--'+n for n in distutils.dist.Distribution.display_option_names]
    for o in distutils.dist.Distribution.display_options:
        if o[1]:
            display_opts.append('-'+o[1])
    for arg in sys.argv:
        if arg.startswith('--help') or arg=='-h' or arg in display_opts:
            ok = False
            break
    _cache.append(ok)
    return ok


def get_distribution(always=False):
    dist = distutils.core._setup_distribution
    # XXX Hack to get numpy installable with easy_install.
    # The problem is easy_install runs it's own setup(), which
    # sets up distutils.core._setup_distribution. However,
    # when our setup() runs, that gets overwritten and lost.
    # We can't use isinstance, as the DistributionWithoutHelpCommands
    # class is local to a function in setuptools.command.easy_install
    if dist is not None and \
            'DistributionWithoutHelpCommands' in repr(dist):
        dist = None
    if always and dist is None:
        dist = CustomDistribution()
    return dist


def setup(**attr):
    if len(sys.argv)<=1 and not attr.get('script_args',[]):
        try:
            from numpy.distutils.interactive import interactive_sys_argv
            from numpy.distutils.core import _exit_interactive_session
            import atexit
            atexit.register(_exit_interactive_session)
            sys.argv[:] = interactive_sys_argv(sys.argv)
            if len(sys.argv)>1:
                return setup(**attr)
        except:
            pass

    cmdclass = my_cmdclass.copy()

    new_attr = attr.copy()
    if 'cmdclass' in new_attr:
        cmdclass.update(new_attr['cmdclass'])
    new_attr['cmdclass'] = cmdclass

    if 'configuration' in new_attr:
        # To avoid calling configuration if there are any errors
        # or help request in command in the line.
        configuration = new_attr.pop('configuration')

        old_dist = distutils.core._setup_distribution
        old_stop = distutils.core._setup_stop_after
        distutils.core._setup_distribution = None
        distutils.core._setup_stop_after = "commandline"
        try:
            dist = setup(**new_attr)
        finally:
            distutils.core._setup_distribution = old_dist
            distutils.core._setup_stop_after = old_stop
        if dist.help or not _command_line_ok():
            # probably displayed help, skip running any commands
            return dist

        # create setup dictionary and append to new_attr
        config = configuration()
        if hasattr(config,'todict'):
            config = config.todict()
        _dict_append(new_attr, **config)

    # Move extension source libraries to libraries
    libraries = []
    for ext in new_attr.get('ext_modules',[]):
        new_libraries = []
        for item in ext.libraries:
            #[item] = util.convert_ulist([item])
            if util.is_sequence(item):
                lib_name, build_info = item
                _check_append_ext_library(libraries, item)
                new_libraries.append(lib_name)
            elif util.is_string(item):
                new_libraries.append(item)
            else:
                raise TypeError("invalid description of extension module "
                                "library %r" % (item,))
        ext.libraries = new_libraries
    if libraries:
        if 'libraries' not in new_attr:
            new_attr['libraries'] = []
        for item in libraries:
            _check_append_library(new_attr['libraries'], item)

    # sources in ext_modules or libraries may contain header files
    if ('ext_modules' in new_attr or 'libraries' in new_attr) \
       and 'headers' not in new_attr:
        new_attr['headers'] = []

    # Use our custom Distribution class instead of distutils' one
    new_attr['distclass'] = CustomDistribution

    return old_setup(**new_attr)


def _check_append_library(libraries, item):
    for libitem in libraries:
        if util.is_sequence(libitem):
            if util.is_sequence(item):
                if item[0]==libitem[0]:
                    if item[1] is libitem[1]:
                        return
                    warnings.warn("[0] libraries list contains %r with"
                                  " different build_info" % (item[0],))
                    break
            else:
                if item==libitem[0]:
                    warnings.warn("[1] libraries list contains %r with"
                                  " no build_info" % (item[0],))
                    break
        else:
            if util.is_sequence(item):
                if item[0]==libitem:
                    warnings.warn("[2] libraries list contains %r with"
                                  " no build_info" % (item[0],))
                    break
            else:
                if item==libitem:
                    return
    libraries.append(item)

def _check_append_ext_library(libraries, (lib_name,build_info)):
    for item in libraries:
        if util.is_sequence(item):
            if item[0]==lib_name:
                if item[1] is build_info:
                    return
                warnings.warn("[3] libraries list contains %r with"
                              " different build_info" % (lib_name,))
                break
        elif item==lib_name:
            warnings.warn("[4] libraries list contains %r with"
                          " no build_info" % (lib_name,))
            break
    libraries.append((lib_name,build_info))
