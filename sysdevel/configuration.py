"""
Configuration classes
"""

import os
import platform

from sysdevel import util


class config(object):
    def __init__(self, dependencies=[], debug=False):
        self.dependencies = dependencies
        self.debug = debug
        self.environment = dict()
        self.found = False

    def null(self):
        pass

    def is_installed(self, environ, version):
        raise NotImplementedError('is_installed')

    def install(self, environ, version, locally=True):
        raise NotImplementedError('install')



class lib_config(config):
    def __init__(self, lib, header, dependencies=[], debug=False):
        config.__init__(self, dependencies, debug)
        self.lib = lib
        self.hdr = header


    def null(self):
        self.environment[self.lib.upper() + '_INCLUDE_DIR'] = None
        self.environment[self.lib.upper() + '_LIB_DIR'] = None
        self.environment[self.lib.upper() + '_SHLIB_DIR'] = None
        self.environment[self.lib.upper() + '_LIB_FILES'] = None
        self.environment[self.lib.upper() + '_LIBRARIES'] = None


    def is_installed(self, environ, version=None):
        util.set_debug(self.debug)

        locations = []
        limit = False
        if self.lib.upper() + '_LIB_DIR' in environ and \
                environ[self.lib.upper() + '_LIB_DIR']:
            locations.append(environ[self.lib.upper() + '_LIB_DIR'])
            limit = True
            if self.lib.upper() + '_INCLUDE_DIR' in environ and \
                    environ[self.lib.upper() + '_INCLUDE_DIR']:
                locations.append(environ[self.lib.upper() + '_INCLUDE_DIR'])

        if not limit:
            try:
                locations += os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
                locations += os.environ['CPATH'].split(os.pathsep)
            except:
                pass
            try:
                locations.append(os.environ[self.lib.upper() + '_ROOT'])
            except:
                pass
            for d in util.programfiles_directories():
                locations.append(os.path.join(d, 'GnuWin32'))
                locations += util.glob_insensitive(d, self.lib + '*')
            try:
                locations.append(environ['MINGW_DIR'])
                locations.append(environ['MSYS_DIR'])
            except:
                pass
        try:
            incl_dir = util.find_header(self.hdr, locations, limit=limit)
            lib_dir, lib = util.find_library(self.lib, locations, limit=limit)
            self.found = True
        except Exception, e:
            if self.debug:
                print e
            return self.found

        self.environment[self.lib.upper() + '_INCLUDE_DIR'] = incl_dir
        self.environment[self.lib.upper() + '_LIB_DIR'] = lib_dir
        #self.environment[self.lib.upper() + '_SHLIB_DIR'] = lib_dir #FIXME
        self.environment[self.lib.upper() + '_LIB_FILES'] = [lib]
        self.environment[self.lib.upper() + '_LIBRARIES'] = [self.lib]
        return self.found


    def install(self, environ, version, locally=True):
        raise NotImplementedError('lib' + self.lib + ' installation')



class py_config(config):
    def __init__(self, pkg, version, dependencies=[], debug=False):
        config.__init__(self, dependencies, debug)
        self.pkg = pkg
        self.version = version


    def is_installed(self, environ, version=None):
        try:
            impl = __import__(self.pkg.lower())
            check_version = False
            if hasattr(impl, '__version__'):
                ver = impl.__version__
                check_version = True
            elif hasattr(impl, 'version'):
                ver = impl.version
                check_version = True
            if check_version:
                if util.compare_versions(ver, version) == -1:
                    return self.found
            self.found = True
        except:
            if self.debug:
                print e
        return self.found


    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'https://pypi.python.org/packages/source/' + \
                self.pkg[0] + '/' + self.pkg + '/'
            if version is None:
                version = self.version
            src_dir = self.pkg + '-' + str(version)
            archive = src_dir + '.tar.gz' 
            util.install_pypkg(src_dir, website, archive, locally=locally)
            if not self.is_installed(environ, version):
                raise Exception(self.pkg + ' installation failed.')



class js_config(config):
    def __init__(self, dependencies=[], debug=False):
        config.__init__(self, dependencies, debug)


    def is_installed(self, environ, version=None):
        return False  ## always fetch



class prog_config(config):
    def __init__(self, exe, dependencies=[], debug=False):
        config.__init__(self, dependencies, debug)
        self.exe = exe


    def null(self):
        self.environment[self.exe.upper()] = None


    def is_installed(self, environ, version=None):
        util.set_debug(self.debug)
        limit = False
        locations = []
        if self.exe.upper() in environ and environ[self.exe.upper()]:
            locations.append(os.path.dirname(environ[self.exe.upper()]))
            limit = True

        if not limit:
            try:
                locations.append(os.environ[self.exe.upper() + '_ROOT'])
            except:
                pass
            try:
                locations.append(environ['MINGW_DIR'])
                locations.append(environ['MSYS_DIR'])
            except:
                pass

        try:
            program = util.find_program(self.exe, locations, limit=limit)
            self.found = True
        except Exception, e:
            if self.debug:
                print e
            return self.found

        self.environment[self.exe.upper()] = program
        return self.found


    def install(self, environ, version, locally=True):
        raise NotImplementedError(self.exe + ' installation')
