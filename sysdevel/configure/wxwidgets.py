
import os
import subprocess
import platform

from sysdevel.util import *
from sysdevel.configuration import lib_config

class configuration(lib_config):
    """
    Find/install wxWidgets library
    """
    def __init__(self):
        lib_config.__init__(self, "wx_baseu", "wx.h", debug=False)


    def null(self):
        self.environment['WX_CPP_FLAGS'] = []
        self.environment['WX_LD_FLAGS'] = []


    def is_installed(self, environ, version):
        set_debug(self.debug)
        try:
            wx_config = os.environ['WX_CONFIG']
        except:
            locations = []
            try:
                locations.append(environ['MINGW_DIR'])
                locations.append(environ['MSYS_DIR'])
            except:
                pass
            try:
                wx_config = find_program('wx-config', locations)
            except Exception as e:
                if self.debug:
                    print(e)
                return self.found
        try:
            cppflags_cmd = [wx_config, '--cppflags']
            process = subprocess.Popen(cppflags_cmd, stdout=subprocess.PIPE)
            cflags = process.communicate()[0].split()

            ldflags_cmd = [wx_config, '--libs', '--gl-libs', '--static=no']
            process = subprocess.Popen(ldflags_cmd, stdout=subprocess.PIPE)
            ldflags = process.communicate()[0].split()
            self.found = True
        except Exception as e:
            if self.debug:
                print(e)
            return self.found

        self.environment['WX_CPP_FLAGS'] = cflags
        self.environment['WX_LD_FLAGS'] = ldflags
        return self.found
    

    def install(self, environ, version, locally=True):
        if not self.found:
            if version is None:
                version = '2.8.12'
            website = ('http://prdownloads.sourceforge.net/wxwindows/',)
            if locally or 'windows' in platform.system().lower():
                src_dir = 'wxMSW-' + str(version)
                archive = src_dir + '.zip'
                autotools_install(environ, website, archive, src_dir, locally)
            else:
                global_install('wxWidgets', website,
                               brew='wxwidgets', port='wxgtk',
                               deb='libwxbase-dev libwxgtk-dev',
                               rpm='wxBase wxGTK-devel')
            if not self.is_installed(environ, version):
                raise Exception('WxGTK installation failed.')
