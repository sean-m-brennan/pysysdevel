"""
Copyright 2013.  Los Alamos National Security, LLC.
This material was produced under U.S. Government contract
DE-AC52-06NA25396 for Los Alamos National Laboratory (LANL), which is
operated by Los Alamos National Security, LLC for the U.S. Department
of Energy. The U.S. Government has rights to use, reproduce, and
distribute this software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS
NATIONAL SECURITY, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR
ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is
modified to produce derivative works, such modified software should be
clearly marked, so as not to confuse it with the version available
from LANL.

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
# pylint: disable=W0105
"""
Package specification
"""

import os
import sys
import platform
import warnings
import glob
import zipfile

from .prerequisites import read_cache
from ..util import flatten
from . import options


#TODO unify argv, environ and options handling

def handle_arguments(argv, option_list=()):
    if '--quiet' in argv:
        options.set_verbose(False)
    if '--debug' in argv:
        options.set_debug(True)
        argv.remove('--debug')

    option_plus_list = list(option_list)
    option_plus_list.append('doc')

    opts = dict()
    opts['bundle'] = False
    opts['runscript'] = ''
    opts['ziplib'] = None
    opts['install'] = True
    opts['sublevel'] = 0
    opts['locally'] = False

    bundle = False
    if 'py2exe' in argv:
        bundle = True
    if 'py2app' in argv:
        bundle = True
    app = ''
    runscript = ''
    for arg in list(argv):
        if arg == '--show':
            opts['install'] = False
        if arg == '--local-install':
            opts['locally'] = True
        if arg.startswith('--sublevel='):
            opts['sublevel'] = int(arg[11:])

        if arg == '-b' or arg == '--build_base':
            idx = argv.index(arg)
            options.set_build_dir(argv[idx+1])

        ## args that won't work with setup
        if arg.startswith('--app='):
            app = runscript = arg[6:].lower()
            runscript = arg[6:].lower()
            if not runscript.endswith('.py'):
                runscript = runscript + '.py'
            for root, _, filenames in os.walk('.'): ## source directory
                for filename in filenames:
                    if filename == runscript:
                        runscript = os.path.join(root, filename)
                        break
            argv.remove(arg)

        if arg.startswith('--ziplib'):
            if '=' in arg:
                opts['ziplib'] = arg[9:]
                if opts['ziplib'][-4:] != '.zip':
                    opts['ziplib'] += '.zip'
            else:
                opts['ziplib'] = options.default_py2exe_library
            argv.remove(arg)

    if bundle and app != '' and runscript != '':
        opts['bundle'] = bundle
        opts['runscript'] = runscript
        opts['app'] = app

    opts['install_dir'] = sys.prefix
    data_directory = 'share'
    data_override = False
    for idx, arg in enumerate(argv[:]):
        if arg.startswith('--prefix='):
            opts['install_dir'] = arg[9:]
        elif arg.startswith('--home='):
            opts['install_dir'] = arg[7:]
        elif arg.startswith('--user='):
            opts['install_dir'] = arg[7:]
        elif arg.startswith('--install-data='):
            path = arg[15:]
            if os.path.isabs(path):
                opts['data_install_dir'] = path
                data_override = True  ## always overrides the above prefixes
            else:
                data_directory = path
        elif arg.startswith('build_') and arg[6:] in option_plus_list:
            opts[arg[6:]] = True
            if not 'build' in argv:
                argv.insert(idx, 'build')
            argv.remove(arg)
        elif arg.startswith('install_') and arg[8:] in option_plus_list:
            opts[arg[8:]] = True
            if not 'install' in argv:
                argv.insert(idx, 'install')
            argv.remove(arg)
        elif arg.startswith('clean_') and arg[8:] in option_plus_list:
            opts[arg[8:]] = True
            if not 'clean' in argv:
                argv.insert(idx, 'clean')
            argv.remove(arg)
    if not data_override:
        opts['data_install_dir'] = os.path.join(opts['install_dir'],
                                                data_directory)

    build_all = True
    for opt in option_list:  ## do not build docs by default
        if opt in opts:
            build_all = False
    if build_all:
        for opt in option_list:
            opts[opt] = True
           
    if 'doc' in opts:
        opts['documentation'] = True
    else:
        opts['documentation'] = False

    return opts, argv


def get_options(pkg_cfg, opts):
    '''
    pkg_config is a 'sysdevel.distutils.pkg_config' object.
    options from 'handle_arguments' above.
    '''
    target_os = platform.system().lower()  ## disallow cross-compile
    is_bundle = opts['bundle']
    runscript = opts['runscript']

    ##############################
    ## Windows plus py2exe
    if is_bundle and target_os == 'windows':
        warnings.simplefilter('ignore', DeprecationWarning)
        import py2exe  # pylint: disable=F0401,E0611,W0612
        warnings.resetwarnings()

        INCLUDE_GTK_WIN = False
        INCLUDE_TCLTK_WIN = False
        #os.environ['PATH'] += os.pathsep + 'gtk/lib' + os.pathsep + 'gtk/bin'

        package_name = pkg_cfg.PACKAGE
        icon_file = os.path.join(pkg_cfg.PACKAGE, pkg_cfg.image_dir,
                                 pkg_cfg.PACKAGE + '.ico')
    
        addtnl_files = []
        addtnl_files += pkg_cfg.get_data_files(opts['app'])
        addtnl_files += pkg_cfg.get_extra_data_files(opts['app'])
        addtnl_files += [('.', [icon_file])]
        addtnl_files += [('.', pkg_cfg.get_missing_libraries())]
        icon_res = [(0, icon_file)]

        if INCLUDE_GTK_WIN:
            gtk_includes = ['cairo', 'pango', 'pangocairo', 'atk',
                            'pygtk', 'gtk', 'gobject',]
        else:
            gtk_includes = []

        excludes = ['distutils', 'setuptools', 'sysdevel.distutils',
                    'bsddb', 'curses',
                    'pywin.debugger', 'pywin.debugger.dbgcon', 'pywin.dialogs',
                    ]
        dll_excludes = ['mswsock.dll', 'powrprof.dll',
                        'mpr.dll', 'msvcirt.dll', 'msvcrt.dll', 'netapi32.dll',
                        'netrap.dll', 'samlib.dll']

        if not INCLUDE_TCLTK_WIN:
            excludes += ['_gtkagg', '_tkagg', 'tcl', 'Tkconstants', 'Tkinter',]
            dll_excludes += ['tcl84.dll', 'tk84.dll',]
        if not INCLUDE_GTK_WIN:
            excludes += ['pygtk', 'gtk', 'gobject', 'gtkhtml2',]
            dll_excludes += ['libgdk-win32-2.0-0.dll', 'libgobject-2.0-0.dll',]


        file_bundling = 1
        if 'app_type' in opts and opts['app_type'] == 'console':
            file_bundling = 3

        exe_opts = {'py2exe': {
                    'unbuffered': False,
                    'optimize': 2,
                    'includes': flatten(list(pkg_cfg.dynamic_modules.values())) + \
                        gtk_includes,
                    'packages': flatten(list(pkg_cfg.required_pkgs.values())) + \
                        pkg_cfg.extra_pkgs,
                    'ignores': [],
                    'excludes': excludes,
                    'dll_excludes': dll_excludes,
                    'dist_dir': os.path.join('bin_dist', opts['app']),
                    'typelibs': [],
                    'compressed': False,
                    'xref': False,
                    'bundle_files': file_bundling,
                    'skip_archive': False,
                    'ascii': False,
                    'custom_boot_script': '',
                    }}

        exe_target = [{
                    'script': runscript,
                    'icon_resources': icon_res,
                    'bitmap_resources': [],
                    'other_resources': [],
                    'dest_base': opts['app'],
                    'company_name': pkg_cfg.COMPANY,
                    }]

        pkgs = pkg_cfg.extra_pkgs
        pkg_data = dict({})
        p = pkg_cfg.PACKAGE
        while True:
            pkgs += [pkg_cfg.names[p]]
            pkg_data[pkg_cfg.names[p]] = pkg_cfg.package_files[p]
            p = pkg_cfg.parents[p]
            if p is None:
                break

        for lib in pkg_cfg.extra_libraries:
            os.environ['PATH'] += os.pathsep + lib[0]
            os.environ['PATH'] += os.pathsep + os.path.join(lib[0], '..', 'bin')

        if 'app_type' in opts and opts['app_type'] == 'console':
            specific_options = dict(
                console = exe_target,
                package_dir = {pkg_cfg.PACKAGE: pkg_cfg.PACKAGE},
                packages = pkgs,
                package_data = pkg_data,
                data_files = addtnl_files,
                options = exe_opts,
                zipfile = opts['ziplib'],
                )
        else:
            specific_options = dict(
                windows = exe_target,
                package_dir = {pkg_cfg.PACKAGE: pkg_cfg.PACKAGE},
                packages = pkgs,
                package_data = pkg_data,
                data_files = addtnl_files,
                options = exe_opts,
                zipfile = opts['ziplib'],
                )

        return specific_options

    ##############################
    ## Mac OS X plus py2app
    elif is_bundle and target_os == 'darwin':
        import py2app  # pylint: disable=F0401,E0611,W0612

        package_name = pkg_cfg.PACKAGE
        target = [runscript]
        addtnl_files = pkg_cfg.source_files
        addtnl_files += [('.', [os.path.join(pkg_cfg.image_path,
                                             pkg_cfg.PACKAGE + '.icns')])]
    
        plist = {'CFBundleName': package_name,
                 'CFBundleDisplayName': package_name,
                 'CFBundleIdentifier': pkg_cfg.ID,
                 'CFBundleVersion': pkg_cfg.VERSION,
                 'CFBundlePackageType': 'APPL',
                 'CFBundleExecutable': package_name.upper(),
                 'CFBundleShortVersionString': pkg_cfg.RELEASE,
                 'NSHumanReadableCopyright': pkg_cfg.COPYRIGHT,
                 'CFBundleGetInfoString': package_name + ' ' + pkg_cfg.VERSION,
                 }
        
        opts = {'py2app': {
            'optimize': 2,
            'includes': pkg_cfg.dynamic_modules,
            'packages': list(pkg_cfg.required_pkgs.values()) + \
                pkg_cfg.extra_pkgs,
            'iconfile': os.path.join(pkg_cfg.PACKAGE, pkg_cfg.image_dir,
                                     pkg_cfg.PACKAGE + '.icns'),
            'excludes': ['tcl', 'Tkconstants', 'Tkinter', 'pytz',],
            'dylib_excludes': ['tcl84.dylib', 'tk84.dylib'],
            'datamodels': [],
            'resources': [],
            'frameworks': [],
            'plist': plist,
            'extension': '.app',
            'graph': False,
            'xref': False,
            #'no_strip': False,
            'no_strip': True,
            'no_chdir': True,
            'semi_standalone': False,
            'alias': False,
#            'argv_emulation': True,
            'argv_emulation': False,
            'argv_inject': [],
            'use_pythonpath': False,
            'bdist_base': pkg_cfg.build_dir,
            'dist_dir': 'bin_dist',
            'site_packages': True,
            #'strip': True,
            'strip': False,
            'prefer_ppc': False,
            'debug_modulegraph': False,
            'debug_skip_macholib': False,
            }}
    
        specific_options = dict(
            app = target,
            #packages = pkgs,
            #package_data = pkg_data,
            data_files = addtnl_files,
            options = opts,
            )
       
        return specific_options

    ##############################
    ## all others (assumes required packages are installed)
    else:
        directories = dict()
        data = dict()
        for p, _ in list(pkg_cfg.hierarchy.items()):
            pkg_name = pkg_cfg.names[p]
            directories[pkg_name] = os.path.join(pkg_cfg.PACKAGE,
                                                 pkg_cfg.directories[p])
            data[pkg_name] = pkg_cfg.package_files[p]
        specific_options = dict(
            package_dir = directories,
            packages = flatten(list(pkg_cfg.names.values())) + \
                pkg_cfg.extra_pkgs,
            package_data = data,
            create_scripts = pkg_cfg.generated_scripts,
            data_files = pkg_cfg.extra_data_files,
            tests = pkg_cfg.tests,
            )
        if target_os == 'windows':
            specific_options['bdist_wininst'] = {
                'bitmap': pkg_cfg.logo_bmp_path,
                'install_script': options.windows_postinstall,
                'keep_temp': True,
                'user_access_control': 'auto',
                }
            ## bdist_msi is incompatible with this build scheme

        return specific_options



def post_setup(pkg_cfg, opts):
    bundled = opts['bundle']
    if bundled:
        os_name = platform.system().lower()
        dist_dir = os.path.join('bin_dist', opts['app'])
        current = os.getcwd()
        os.chdir(dist_dir)
        archive = opts['app'] + '_' + os_name + '_' + pkg_cfg.RELEASE + '.zip'
        if pkg_cfg.PACKAGE != opts['app']:
            archive = pkg_cfg.PACKAGE + '_' + archive
        z = zipfile.ZipFile(os.path.join(current, 'bin_dist', archive),
                            'w', zipfile.ZIP_DEFLATED)
        for root, _, filenames in os.walk('.'):
            for filename in filenames:
                z.write(os.path.join(root, filename))
        z.close()
        os.chdir(current)




class pkg_config(object):
    '''
    Package configuration class for use with sysdevel.

    To create you custom configuration:
    create a config.py module wherein you subclass this object
    (eg. 'class subclass_config(pkg_config)'),
    then create an instance of your subclass named 'pkg'
    (eg. 'pkg = subclass_config(...)').
    '''
    def __init__(self, name, package_tree,
                 pkg_id, version, author, email, website, company,
                 copyrt, srcs, runscripts,
                 data_files=(), extra_data=(), req_pkgs=(), dyn_mods=(),
                 extra_pkgs=(), extra_libs=(), environ=None, prereq=(),
                 redistrib=(), img_dir='', build_dir='', description=''):
        if environ is None:
            environ = dict()
        if package_tree is not None:
            self.PACKAGE       = package_tree.root()
        else:
            self.PACKAGE       = name.lower()
        self.NAME              = name
        self.VERSION           = version[:version.rindex('.')]
        self.RELEASE           = version
        self.COPYRIGHT         = copyrt
        self.AUTHOR            = author
        self.AUTHOR_CONTACT    = email
        self.WEBSITE           = website
        self.COMPANY           = company
        self.ID                = pkg_id
        self.PACKAGE_TREE      = package_tree
        self.DESCRIPTION       = description
        self.REQUIRED          = req_pkgs

        self.source_files      = srcs
        self.runscripts        = runscripts
        self.generated_scripts = []
        self.tests             = []
        self.package_files     = dict({self.PACKAGE: list(data_files)})
        self.extra_data_files  = list(extra_data)
        self.required_pkgs     = dict({self.PACKAGE: list(req_pkgs)})
        self.dynamic_modules   = dict({self.PACKAGE: list(dyn_mods)})
        self.logo_bmp_path     = None
        self.environment       = environ
        self.prerequisites     = list(prereq)
        self.redistributed     = list(redistrib)
        self.image_dir         = img_dir
        self.build_dir         = build_dir
        self.build_config      = 'release'
        self.extra_pkgs        = list(extra_pkgs)
        self.extra_libraries   = list(extra_libs)
        self.missing_libraries = []
        self.has_extension     = False

        if package_tree is not None:
            self.package_names = dict((tree.root(),
                                       '_'.join(list(reversed(tree.flatten()))))
                                      for tree in self.PACKAGE_TREE.inverted())
            self.names         = dict((tree.root(),
                                       '.'.join(list(reversed(tree.flatten()))))
                                      for tree in self.PACKAGE_TREE.subtrees())
            self.parents       = dict((node, self.PACKAGE_TREE.parent(node))
                                      for node in self.PACKAGE_TREE.flatten())
            self.hierarchy     = dict((tree.root(),
                                       list(reversed(tree.flatten())))
                                      for tree in self.PACKAGE_TREE.subtrees())
            # pylint: disable=W0142
            self.directories   = dict((tree.root(),
                                       os.path.join(*(list(reversed(tree.flatten()))[1:]))) \
                                          for tree in self.PACKAGE_TREE.subtrees() if len(tree) > 1)
            self.directories[self.PACKAGE] = '.'
        else:
            self.package_names = dict()
            self.names         = dict()
            self.parents       = dict()
            self.hierarchy     = dict()
            self.directories   = dict()

        self.environment['PACKAGE'] = self.PACKAGE
        self.environment['NAME'] = self.NAME
        self.environment['VERSION'] = self.VERSION
        self.environment['RELEASE'] = self.RELEASE
        self.environment['COPYRIGHT'] = self.COPYRIGHT
        self.environment['AUTHOR'] = self.AUTHOR
        self.environment['COMPANY'] = self.COMPANY
        self.environment['COMPILER'] = 'gcc'

        self.environment['WEBSOCKET_SERVER']        = ''
        self.environment['WEBSOCKET_ORIGIN']        = ''
        self.environment['WEBSOCKET_RESOURCE']      = ''
        self.environment['WEBSOCKET_ADD_RESOURCES'] = ''
        self.environment['WEBSOCKET_TLS_PKEY']      = 'None'
        self.environment['WEBSOCKET_TLS_CERT']      = 'None'



    def get_prerequisites(self, argv):
        if 'windows' in platform.system().lower():
            environ = read_cache()
            if 'COMPILER' in environ:
                compiler = environ['COMPILER']
            else:
                compiler = 'msvc'  ## distutils default on Windows
            for a in range(len(argv)):
                if argv[a].startswith('--compiler='):
                    compiler = argv[a][11:]
                elif argv[a] == '-c':
                    compiler = argv[a+1]
            if compiler == 'mingw32':
                self.prerequisites = ['mingw'] + self.prerequisites
            elif compiler.startswith('msvc'):
                self.prerequisites = ['msvc'] + self.prerequisites
            else:
                raise Exception("Unknown compiler specified: " + compiler)
            self.environment['COMPILER'] = compiler
        if self.environment['COMPILER'] == 'gcc':
            self.prerequisites = ['gcc'] + self.prerequisites
        return self.prerequisites, argv

    def additional_env(self, envir):
        self.environment = dict(list(envir.items()) + list(self.environment.items()))
        return self.environment

    def get_source_files(self, *args):  # pylint: disable=W0613
        return self.source_files

    def get_data_files(self, *args):  # pylint: disable=W0613
        return [('', self.package_files[self.PACKAGE])]

    def get_extra_data_files(self, *args):  # pylint: disable=W0613
        return self.extra_data_files

    def get_missing_libraries(self, *args):  # pylint: disable=W0613
        '''
        List of libraries for explicit inclusion in py2exe build.
        See the list of DLLs at the end of py2exe processing.
        '''
        msvcrt_extra = []
        if self.has_extension:
            msvcrt_release_path = self.environment['MSVCRT_DIR']
            msvcrt_debug_path = self.environment['MSVCRT_DEBUG_DIR']
            if self.build_config.lower() == 'debug':
                msvc_glob = os.path.join(msvcrt_debug_path, '*.*')
                sys.path.append(msvcrt_debug_path)
            else:
                msvc_glob = os.path.join(msvcrt_release_path, '*.*')
                sys.path.append(msvcrt_release_path)
            msvcrt_extra += glob.glob(msvc_glob)

        missing = []
        for lib in self.missing_libraries + msvcrt_extra:
            missing.append(lib.encode('ascii', 'ignore'))
        return missing
