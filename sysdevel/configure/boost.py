
import os
import platform
import subprocess

from sysdevel.util import *
from sysdevel.configuration import lib_config

class configuration(lib_config):
    """
    Find/install Boost
    """
    def __init__(self):
        lib_config.__init__(self, "archive", "archive.h",
                            debug=False)
        if 'windows' in platform.system().lower():
            self.dependencies = ['mingw'] # FIXME msvc build also


    def is_installed(self, environ, version):
        if version is None:
            required_version = '1_44_0'
        else:
            required_version = version.replace('.', '_')

        set_debug(self.debug)
        base_dirs = []
        limit = False
        if 'BOOST_LIB_DIR' in environ and environ['BOOST_LIB_DIR']:
            base_dirs.append(environ['BOOST_LIB_DIR'])
            limit = True
            if 'BOOST_INCLUDE_DIR' in environ and environ['BOOST_INCLUDE_DIR']:
                base_dirs.append(environ['BOOST_INCLUDE_DIR'])

        if not limit:
            try:
                base_dirs += os.environ['LD_LIBRARY_PATH'].split(os.pathsep)
            except:
                pass
            try:
                boost_root = os.environ['BOOST_ROOT']
                boost_root = boost_root.strip('"')
                if os.path.exists(os.path.join(boost_root, 'stage', 'lib')):
                    base_dirs.append(os.path.join(boost_root, 'stage'))
                base_dirs.append(boost_root)
            except:
                pass
            try:
                base_dirs.append(os.environ['BOOST_LIBRARY_DIR'])
            except:
                pass
            try:
                base_dirs.append(environ['MINGW_DIR'])
                base_dirs.append(environ['MSYS_DIR'])
            except:
                pass
        try:
            incl_dir = find_header(os.path.join('boost', 'version.hpp'),
                                   base_dirs, ['boost-*'], limit=limit)
            lib_dir, libs = find_libraries('boost', base_dirs, limit=limit)
            ## FIXME lib_dir is wrong in windows (maybe)
            boost_version = get_header_version(os.path.join(incl_dir, 'boost',
                                                            'version.hpp'),
                                               'BOOST_LIB_VERSION')
            boost_version = boost_version.strip('"')
            if compare_versions(boost_version, required_version) == -1:
                return self.found
            self.found = True
        except Exception, e:
            if self.debug:
                print e
            return self.found

        self.environment['BOOST_INCLUDE_DIR'] = incl_dir
        self.environment['BOOST_LIB_DIR'] = lib_dir
        self.environment['BOOST_LIB_FILES'] = libs
        self.environment['BOOST_LIBRARIES'] = ['boost_python',
                                               'boost_date_time',
                                               'boost_filesystem',
                                               'boost_graph',
                                               'boost_iostreams',
                                               'boost_prg_exec_monitor',
                                               'boost_program_options',
                                               'boost_regex',
                                               'boost_serialization',
                                               'boost_signals',
                                               'boost_system', 'boost_thread',
                                               'boost_unit_test_framework',
                                               'boost_wave',
                                               'boost_wserialization',]
        return self.found


    def install(self, environ, version, locally=True):
        global local_search_paths
        if not self.found:
            if version is None:
                version = '1_44_0'
            if '.' in version:
                version = version.replace('.', '_')
            if len(version.split('_')) < 3:
                version += '_0'
            website = ('http://downloads.sourceforge.net/project/boost/',
                       'boost/' + version.replace('_', '.') + '/')
            if locally or 'windows' in platform.system().lower():
                src_dir = 'boost_' + str(version)
                archive = src_dir + '.tar.gz'

                here = os.path.abspath(os.getcwd())
                fetch(''.join(website), archive, archive)
                unarchive(archive, src_dir)

                if locally:
                    prefix = os.path.abspath(target_build_dir)
                    if not prefix in local_search_paths:
                        local_search_paths.append(prefix)
                else:
                    prefix = global_prefix

                os.chdir(os.path.join(target_build_dir, src_dir))
                log = open('build.log', 'w')
                err = open('build.errors', 'w')
                ## unique build process
                if 'windows' in platform.system().lower():
                    os_environ = os.environ.copy()
                    new_path = os_environ['PATH'] + \
                        os.path.join(environ['MINGW_DIR'], 'bin') + ';' + \
                        os.path.join(environ['MSYS_DIR'], 'bin') + ';'
                    os_environ['PATH'] = new_path.encode('ascii', 'ignore')
                    cmd_line = 'bootstrap.bat mingw'
                    #cmd_line = 'bootstrap.bat msvc'
                    p = subprocess.Popen(cmd_line, env=os_environ,
                                         stdout=log, stderr=err)
                    status = p.wait()
                    if status != 0:
                        raise subprocess.CalledProcessError(status, cmd_line)
                    toolset = 'toolset=gcc'
                    #toolset = 'toolset=msvc'
                    cmd_line = 'bjam.exe install link=shared link=static ' + \
                        toolset + ' variant=release threading=single ' + \
                        '--prefix=' + prefix
                    p = subprocess.Popen(cmd_line, env=os_environ,
                                         stdout=log, stderr=err)
                    status = p.wait()
                    if status != 0:
                        raise subprocess.CalledProcessError(status, cmd_line)
                else:
                    check_call(['./bootstrap.sh'], stdout=log, stderr=err)
                    subprocess.call(['./bjam', 'install', '--prefix=' + prefix],
                                    stdout=log, stderr=err)
                    ## may return an error even if everything built
                log.close()
                err.close()
                os.chdir(here)
            else:
                global_install('Boost', website,
                               brew='boost',
                               port='boost +python' + ''.join(get_python_version()),
                               deb='libboost-dev',
                               rpm='boost-devel')
            if not self.is_installed(environ, version):
                raise Exception('Boost installation failed.')
