
import os
import sys
import shutil
import traceback

from ..prerequisites import *
from ..configuration import config

class configuration(config):
    """
    Find/install GMAT sources
    """

    ## latest release or current svn checkout
    (R2012a, SVN) = list(range(2))
    version_strs  = {R2012a: 'R2012a', SVN: 'svn'}
    version_zfill = 6

    VERSION = R2012a

    def __init__(self):
        config.__init__(self, debug=False)


    def null(self):
        self.environment['GMAT_ROOT'] = ''
        self.environment['GMAT_VERSION'] = ''
        self.environment['GMAT_DATA'] = None
        self.environment['GMAT_INCLUDE_DIRS'] = []
        self.environment['GMAT_SRC_DIR'] = ''
        self.environment['GMAT_BASE_DIR'] = ''
        self.environment['GMAT_BASE_INCLUDE_DIRS'] = []
        self.environment['GMAT_BASE_SRCS'] = []
        self.environment['GMAT_GUI_DIR'] = ''
        self.environment['GMAT_GUI_INCLUDE_DIRS'] = []
        self.environment['GMAT_GUI_SRCS'] = []
        self.environment['GMAT_CONSOLE_DIR'] = ''
        self.environment['GMAT_CONSOLE_SOURCES'] = []
        self.environment['GMAT_CONSOLE_EXTRA_SOURCES'] = []
        self.environment['GMAT_C_DIR'] = ''
        self.environment['GMAT_C_INCLUDE_DIRS'] = []
        self.environment['GMAT_C_EXT_HEADERS'] = []
        self.environment['GMAT_C_EXT_SOURCES'] = []
        self.environment['GMAT_FORTRAN_SRCS'] = []


    def is_installed(self, environ, version):
        set_debug(self.debug)

        locations = []
        limit = False
        if 'GMAT_ROOT' in environ and environ['GMAT_ROOT']:
            gmat_root = environ['GMAT_ROOT']
        else:
            try:
                gmat_root = os.environ['GMAT_ROOT']
            except Exception:
                if self.debug:
                    e = sys.exc_info()[1]
                    print(e)
                return self.found

        if os.path.exists(gmat_root):
            try:
                gmat_version = os.environ['GMAT_VERSION']
            except:
                try:
                    import pysvn
                    rev_num = pysvn.Client().info(gmat_root).revision.number
                    gmat_version = 'svn-' + str(rev_num).zfill(self.version_zfill)
                except:
                    gmat_version = 'R2012a'
            if compare_versions(gmat_version, version) == -1:
                return self.found
            self.environment['GMAT_ROOT'] = gmat_root
            self.environment['GMAT_VERSION'] = gmat_version
            try:
                self.environment['GMAT_DATA'] = os.environ['GMAT_DATA']
            except:
                # WARNING: enforcing the svn convention on release data location
                self.environment['GMAT_DATA'] = os.path.join(gmat_root,
                                                             'application')
            self._set_environment(gmat_root, gmat_version)
            self.found = True

        return self.found


    def install(self, environ, version, locally=True):
        if version is None:
            version = self.version_strs[self.VERSION]
        if version.lower().startswith('svn'):
            import pysvn
            svn_repo = 'https://gmat.svn.sourceforge.net/svnroot/gmat/trunk'
            client = pysvn.Client()
            src_dir = os.path.join(target_build_dir, 'gmat-svn-src')
            data_dir = os.path.join(src_dir, 'application')
            if not os.path.exists(src_dir):
                client.checkout(svn_repo, src_dir)
            rev_num = client.info(src_dir).revision.number
            version = self.version_strs[version] + '-' + \
                str(rev_num).zfill(self.version_zfill)
        else:
            website = ('http://prdownloads.sourceforge.net/gmat/',)
            here = os.path.abspath(os.getcwd())
            src_dir = 'gmat-src-' + str(version) + '-Beta'
            archive = src_dir + '.zip'
            fetch(''.join(website), archive, archive)
            unarchive(archive, src_dir)

            data_dir = 'gmat-datafiles-' + str(version) + '-Beta'
            data_archive = data_dir + '.zip'
            fetch(''.join(website), data_archive, data_archive)
            unarchive(data_archive, data_dir)
            src_dir = os.path.join(target_build_dir, src_dir)
            data_dir = os.path.join(target_build_dir, data_dir)

        self.environment['GMAT_VERSION'] = version
        self.environment['GMAT_ROOT'] = os.path.abspath(src_dir)
        self.environment['GMAT_DATA'] = os.path.abspath(data_dir)
        self._set_environment(src_dir, version)


    def _do_patching(self, gmat_root, gmat_version):
        # modify faulty MessageReceiver.hpp
        msg_rcvr = os.path.join(gmat_root, 'src', 'base', 'util',
                                'MessageReceiver.hpp')
        print('Patch ' + msg_rcvr)
        if not os.path.exists(msg_rcvr + '.orig'):
            old_file = msg_rcvr + '.orig'
            os.rename(msg_rcvr, old_file)
            old = open(old_file, 'r')
            new = open(msg_rcvr, 'w')
            for line in old:
                if not 'GmatGlobal' in line:
                    new.write(line)
            old.close()
            new.close()


    def _is_lib_dir(self, parent, name):
        return name != 'include' and not 'svn' in name and not 'CVS' in name \
            and not 'cvs' in name and os.path.isdir(os.path.join(parent, name))


    def _set_environment(self, gmat_root, gmat_version):
        self._do_patching(gmat_root, gmat_version)

        excludes = ['Spice*.?pp', 'SPKPropagator.?pp',
                    'RunSimulator.?pp', 'OpenGlPlot.?pp',
                    'SocketServer.?pp', 'Cowell.?pp', 'TableTemplate.?pp',
                    'ArrayTemplate.?pp',
                    ]

        self.environment['GMAT_PLUGIN_DIR'] = os.path.join(gmat_root, 'plugins')
        self.environment['GMAT_SRC_DIR'] = os.path.join(gmat_root, 'src')
        self.environment['GMAT_DATA_DIRS'] = []

        ## C Interface
        self.environment['GMAT_C_DIR'] = os.path.join(
            self.environment['GMAT_PLUGIN_DIR'], 'CInterfacePlugin', 'src')
        self.environment['GMAT_C_INCLUDE_DIRS'] = [
            os.path.join(self.environment['GMAT_C_DIR'], 'include'),
            os.path.join(self.environment['GMAT_C_DIR'], 'command'),
            os.path.join(self.environment['GMAT_C_DIR'], 'factory'),
            os.path.join(self.environment['GMAT_C_DIR'], 'plugin'),
            ]
        self.environment['GMAT_C_EXT_HEADERS'] = [
            os.path.join(self.environment['GMAT_C_DIR'],
                         'command', 'PrepareMissionSequence.hpp'),
            os.path.join(self.environment['GMAT_C_DIR'],
                         'factory', 'CCommandFactory.hpp'),
            os.path.join(self.environment['GMAT_C_DIR'],
                         'plugin', 'CInterfacePluginFunctions.hpp'),
            os.path.join(self.environment['GMAT_C_DIR'],
                         'include', 'GmatCFunc_defs.hpp'),
            os.path.join(self.environment['GMAT_SRC_DIR'],
                         'base', 'include', 'gmatdefs.hpp'),
            ]
        self.environment['GMAT_C_EXT_SOURCES'] = [
            os.path.join(self.environment['GMAT_C_DIR'],
                         'command', 'PrepareMissionSequence.cpp'),
            os.path.join(self.environment['GMAT_C_DIR'],
                         'factory', 'CCommandFactory.cpp'),
            os.path.join(self.environment['GMAT_C_DIR'],
                         'plugin', 'CInterfacePluginFunctions.cpp'),
            ]

        ## Console
        self.environment['GMAT_CONSOLE_DIR'] = os.path.join(
            self.environment['GMAT_SRC_DIR'], 'console')
        self.environment['GMAT_CONSOLE_HEADERS'] = [
            os.path.join(self.environment['GMAT_SRC_DIR'],
                         'console', 'ConsoleAppException.hpp'),
            os.path.join(self.environment['GMAT_SRC_DIR'],
                         'console', 'ConsoleMessageReceiver.hpp'),
            os.path.join(self.environment['GMAT_SRC_DIR'],
                         'console', 'driver.hpp'),
            os.path.join(self.environment['GMAT_SRC_DIR'],
                         'console', 'PrintUtility.hpp'),
            os.path.join(self.environment['GMAT_SRC_DIR'],
                         'base', 'include', 'gmatdefs.hpp'),
            ]
        self.environment['GMAT_CONSOLE_EXTRA_SOURCES'] = [
            os.path.join(self.environment['GMAT_SRC_DIR'],
                         'console', 'PrintUtility.cpp'),
            os.path.join(self.environment['GMAT_SRC_DIR'],
                         'console', 'ConsoleMessageReceiver.cpp'),
            ]
        self.environment['GMAT_CONSOLE_SOURCES'] = [
            os.path.join(self.environment['GMAT_SRC_DIR'],
                         'console', 'driver.cpp'),
            os.path.join(self.environment['GMAT_SRC_DIR'],
                         'console', 'ConsoleAppException.cpp'),
            ] + self.environment['GMAT_CONSOLE_EXTRA_SOURCES']
        
        ## Base
        base_dir = os.path.join(self.environment['GMAT_SRC_DIR'], 'base')
        self.environment['GMAT_BASE_DIR'] = base_dir
        dirs = []
        self.environment['GMAT_BASE_LIBS'] = [name for name in os.listdir(base_dir)
                                              if self._is_lib_dir(base_dir, name)]
        self.environment['GMAT_BASE_INCLUDE_DIRS'] = [os.path.join(base_dir,
                                                                   'include'),]

        base_srcs = []
        base_hdrs = []
        for lib in self.environment['GMAT_BASE_LIBS']:
            include_dirs = [os.path.join(base_dir, lib)]
            self.environment['GMAT_BASE_' + lib + '_HDRS'] = []
            for root, dirnames, filenames in os.walk(os.path.join(base_dir, lib)):
                for filename in fnmatch.filter(filenames, '*.cpp'):
                    exclude = False
                    for pattern in excludes:
                        if fnmatch.fnmatch(filename, pattern):
                            exclude = True
                    if not exclude:
                        base_srcs.append(os.path.join(root, filename))
                for filename in fnmatch.filter(filenames, '*.hpp'):
                    exclude = False
                    for pattern in excludes:
                        if fnmatch.fnmatch(filename, pattern):
                            exclude = True
                    if not exclude:
                        path = os.path.join(root, filename)
                        if not root in include_dirs:
                            include_dirs += [root]
                        self.environment['GMAT_BASE_' + lib + '_HDRS'].append(path)
                        base_hdrs.append(path)
            self.environment['GMAT_BASE_INCLUDE_DIRS'] += include_dirs
        self.environment['GMAT_FORTRAN_SRCS'] = [
            os.path.join(base_dir, 'solarsys', 'msise90_sub.for')]
        self.environment['GMAT_BASE_HDRS'] = base_hdrs
        self.environment['GMAT_BASE_SRCS'] = base_srcs

        ## Plugins
        self.environment['GMAT_PLUGINS'] = ['EphemPropagator', 'Estimation',
                                            'FminconOptimizer',]  ## ignore Matlab
        plugin_dir = self.environment['GMAT_PLUGIN_DIR']
        for plugin in self.environment['GMAT_PLUGINS']:
            plugin_srcs = []
            plugin_hdrs = []
            include_dirs = [os.path.join(plugin_dir, plugin + 'Plugin', 'src')]
            for root, dirnames, filenames in os.walk(include_dirs[0]):
                for filename in fnmatch.filter(filenames, '*.cpp'):
                    exclude = False
                    for pattern in excludes:
                        if fnmatch.fnmatch(filename, pattern):
                            exclude = True
                    if not exclude:
                        plugin_srcs.append(os.path.join(root, filename))
                for filename in fnmatch.filter(filenames, '*.hpp'):
                    exclude = False
                    for pattern in excludes:
                        if fnmatch.fnmatch(filename, pattern):
                            exclude = True
                    if not exclude:
                        path = os.path.join(root, filename)
                        if not root in include_dirs:
                            include_dirs += [root]
                        plugin_hdrs.append(path)
            self.environment['GMAT_' + plugin + '_INCLUDE_DIRS'] = include_dirs
            self.environment['GMAT_' + plugin + '_HDRS'] = plugin_hdrs
            self.environment['GMAT_' + plugin + '_SRCS'] = plugin_srcs


        ## GUI
        gui_dir = os.path.join(self.environment['GMAT_SRC_DIR'], 'gui')
        self.environment['GMAT_GUI_DIR'] = gui_dir
        self.environment['GMAT_GUI_LIBS'] = [name for name in os.listdir(gui_dir)
                                             if self._is_lib_dir(gui_dir, name)]
        gui_include = os.path.join(gui_dir, 'include')
        self.environment['GMAT_GUI_INCLUDE_DIRS'] = [gui_include]
        for sub in os.listdir(gui_include):
            if self._is_lib_dir(gui_include, sub):
                self.environment['GMAT_GUI_INCLUDE_DIRS'] += [
                    os.path.join(gui_include, sub)]
        gui_srcs = []
        gui_hdrs = []
        for lib in self.environment['GMAT_GUI_LIBS']:
            self.environment['GMAT_GUI_INCLUDE_DIRS'] += [os.path.join(gui_dir,
                                                                       lib)]
            for root, dirnames, filenames in os.walk(os.path.join(gui_dir, lib)):
                for filename in fnmatch.filter(filenames, '*.cpp'):
                    exclude = False
                    for pattern in excludes:
                        if fnmatch.fnmatch(filename, pattern):
                            exclude = True
                    if not exclude:
                        gui_srcs.append(os.path.join(root, filename))
                for filename in fnmatch.filter(filenames, '*.hpp'):
                    exclude = False
                    for pattern in excludes:
                        if fnmatch.fnmatch(filename, pattern):
                            exclude = True
                    if not exclude:
                        gui_hdrs.append(os.path.join(root, filename))
        self.environment['GMAT_GUI_HDRS'] = gui_hdrs
        self.environment['GMAT_GUI_SRCS'] = gui_srcs


        self.environment['GMAT_INCLUDE_DIRS'] = \
            self.environment['GMAT_BASE_INCLUDE_DIRS'] + \
            self.environment['GMAT_GUI_INCLUDE_DIRS'] 
