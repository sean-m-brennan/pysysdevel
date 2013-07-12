"""
'build_js' command for python-to-javascript conversion using Pyjamas
"""

import os
import sys
import logging
import subprocess
import shutil
import glob

from distutils.errors import DistutilsExecError

try:
    from numpy.distutils.command.build_ext import build_ext
except:
    from distutils.command.build_ext import build_ext

import util


class build_js(build_ext):
    '''
    Build Pyjamas web interfaces using WebExtension
    '''
    user_options = build_ext.user_options + [
        ('pyjscompiler=', None,
         "specify the Pyjamas python-to-javascript compiler path"),
        ('pyjspath=', None,
         "specify the path to the Pyjamas distribution"),
        ]

    def initialize_options(self):
        build_ext.initialize_options(self)
        self.web_ext_modules = []
        self.pyjscompiler = None
        self.pyjspath = None

    def finalize_options(self):
        build_ext.finalize_options(self)
        self.web_ext_modules = self.distribution.web_ext_modules
        if self.pyjspath is None:
            try:
                import pyjs
                self.pyjspath = os.path.dirname(pyjs.__file__)
            except:
                pass
        else:
            sys.path.insert(0, os.path.join(self.pyjspath, 'build', 'lib'))
        if self.pyjscompiler is None:
            try:
                self.pyjscompiler = util.find_program('pyjsbuild',
                                                      [self.pyjspath])
            except:
                pass


    def run(self):
        if not self.web_ext_modules:
            return

        ## Make sure that extension sources are complete.
        self.run_command('build_src')
        build = self.get_finalized_command('build')
        environ = self.distribution.environment

        import pyjs
        ## TODO: use pyjs module directly (instead of 'pyjsbuild')
        for wext in self.web_ext_modules:
            if self.distribution.verbose:
                print 'building web extension "' + \
                    os.path.join(wext.public_subdir, wext.name) + '" sources'

            target = os.path.abspath(os.path.join(build.build_base, 'http',
                                                  wext.public_subdir))
            util.mkdir(target)
            here = os.getcwd()
            src_dir = os.path.abspath(wext.source_directory)
            working_dir = os.path.abspath(os.path.join(build.build_temp,
                                                       'web', wext.name))
            util.mkdir(working_dir)

            for support in wext.extra_support_files:
                src_file = util.sysdevel_support_path(support + '.in')
                if not os.path.exists(src_file):
                    src_file = src_file[:-3]
                dst_file = os.path.join(working_dir, support)
                util.configure_file(environ, src_file, dst_file)

            reprocess = True
            ref = os.path.join(target, wext.name + '.html')
            if os.path.exists(ref) and not self.force:
                reprocess = False
                for src in wext.sources:
                    if os.path.getmtime(ref) < os.path.getmtime(src):
                        reprocess = True
            if reprocess:
                for s in wext.sources:
                    util.configure_file(environ, s,
                                        os.path.join(working_dir,
                                                     os.path.basename(s)))
                ## Special handling for 'public' directory
                util.configure_files(environ, os.path.join(src_dir, 'public'),
                                     '*', os.path.join(working_dir, 'public'),
                                     excludes=['.svn', 'CVS'])

                compiler = wext.compiler or \
                    environ['PYJSBUILD'] or self.pyjscompiler
                if compiler is None:
                    raise DistutilsExecError, \
                        "no value pyjsbuild executable found or given"
                cmd_line = [os.path.abspath(compiler)]
                for arg in wext.extra_compile_args:
                    if 'debug' in arg.lower():
                        cmd_line.append('--debug')
                        cmd_line.append('--print-statements')
                    else:
                        cmd_line.append(arg)
                if self.distribution.verbose:
                    cmd_line.append('--log-level=' + str(logging.INFO))
                else:
                    cmd_line.append('--log-level=' + str(logging.ERROR))
                cmd_line.append('--output=' + target)
                cmd_line.append(wext.name)

                os.chdir(working_dir)
                status = subprocess.call(cmd_line)
                if status != 0:
                    raise Exception("Command '" + str(cmd_line) +
                                    "' returned non-zero exit status "
                                    + str(status))
                os.chdir(here)

            for filename in wext.extra_public_files:
                filepath = util.sysdevel_support_path(filename + '.in')
                if not os.path.exists(filepath):
                    filepath = filepath[:-3]
                targetfile = os.path.join(target, filename)
                if not os.path.exists(targetfile):
                    util.configure_file(environ, filepath, targetfile)

            js_dir = os.path.join(build.build_base, util.javascript_dir)
            if os.path.exists(js_dir):
                util.copy_tree(js_dir, os.path.join(target,
                                                    util.javascript_dir))

            if not os.path.lexists(os.path.join(target, 'index.html')):
                shutil.copyfile(os.path.join(target, wext.name + '.html'),
                                os.path.join(target, 'index.html'))
