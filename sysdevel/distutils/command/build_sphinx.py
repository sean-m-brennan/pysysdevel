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
'build_sphinx' command for Sphinx docs (plus Doxygen/Breathe for extension docs)
"""

import os
import sys
import fnmatch
import glob
import shutil
import platform
import subprocess
from distutils.core import Command

from sysdevel.distutils.filesystem import mkdir, copy_tree
from sysdevel.distutils.building import configure_file, configure_files
from sysdevel.distutils.prerequisites import find_program
from sysdevel.distutils import options


def create_breathe_stylesheet(dirname):
    dirs = os.path.split(dirname)
    if (dirs[1] == '' and not dirs[0].endswith('_static')) or \
            (dirs[1] != '' and dirs[1] != '_static'):
        dirname = os.path.join(dirname, '_static')
    mkdir(dirname)
    f = open(os.path.join(dirname, 'breathe.css'), 'w')
    f.write('''
/* -- breathe specific styles ----------------------------------------------- */

/* So enum value descriptions are displayed inline to the item */
.breatheenumvalues li tt + p {
	display: inline;
}

/* So parameter descriptions are displayed inline to the item */
.breatheparameterlist li tt + p {
	display: inline;
}

''')
    f.close()


class build_sphinx(Command):
    description = "build sphinx documentation"

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if not self.distribution.doc_modules:
            return

        ## Make sure that sources are complete in build_lib.
        self.run_command('build_src')
        ## Ditto extensions
        self.run_command('build_ext')

        build = self.get_finalized_command('build')
        buildpy = self.get_finalized_command('build_py')
        target = os.path.abspath(os.path.join(build.build_base, 'http'))
        mkdir(target)
        build_verbose = self.distribution.verbose
        environ = self.distribution.environment

        for dext in self.distribution.doc_modules:
            if self.distribution.verbose:
                print('building documentation "' + dext.name + '" sources')

            doc_dir = os.path.abspath(dext.source_directory)
            extra_dirs = dext.extra_directories
            working_dir = os.path.abspath(os.path.join(build.build_temp,
                                                       dext.source_directory))
            here = os.getcwd()

            reprocess = True
            ref = os.path.join(target, dext.name + '.html')
            root_dir = dext.name
            if os.path.exists(ref) and not self.force:
                reprocess = False
                for root, _, filenames in os.walk(doc_dir):
                    for fn in fnmatch.filter(filenames, '*.rst'):
                        doc = os.path.join(root, fn)
                        if os.path.getmtime(ref) < os.path.getmtime(doc):
                            reprocess = True
                            break
                        src = os.path.join(root_dir, root[len(doc_dir)+1:],
                                            fn[:-3] + 'py')
                        if os.path.exists(src):
                            if os.path.getmtime(ref) < os.path.getmtime(src):
                                reprocess = True
                                break
            if reprocess:
                src_dirs = []
                for package in buildpy.packages:
                    # Locate package source directory
                    src_dirs.append(os.path.abspath(buildpy.get_package_dir(package)))
                #FIXME rst files in package sources (mutiple packages)
                #src_dir = src_dirs[0]
                src_dir = os.path.abspath('.')
                bld_dir = os.path.abspath(build.build_lib)
                doc_bld_dir = os.path.join(bld_dir,
                                           os.path.relpath(doc_dir, src_dir))
                environ['BUILD_DIR'] = bld_dir
                environ['SOURCE_DIR'] = src_dir
                environ['RELATIVE_SOURCE_DIR'] = os.path.relpath(src_dir,
                                                                 doc_bld_dir)

                copy_tree(doc_dir, working_dir, True,
                          excludes=['.svn', 'CVS', '.git', '.hg*'])
                for d in extra_dirs:
                    subdir = os.path.basename(os.path.normpath(d))
                    copy_tree(d, os.path.join(target, subdir), True,
                              excludes=['.svn', 'CVS', '.git', '.hg*'])

                ## Configure rst files
                configure_files(environ, src_dir, '*.rst', working_dir)

                if os.path.exists(os.path.join(doc_dir, dext.doxygen_cfg)):
                    ## Doxygen + breathe
                    print('Config ' + os.path.join(doc_dir, dext.doxygen_cfg))
                    configure_file(environ,
                                   os.path.join(doc_dir, dext.doxygen_cfg),
                                   os.path.join(working_dir, dext.doxygen_cfg),
                                   style=dext.style)
                    for s in dext.doxygen_srcs:
                        configure_file(environ,
                                       os.path.join(doc_dir, s),
                                       os.path.join(working_dir, s),
                                       style=dext.style)
                    try:
                        doxygen_exe = find_program('doxygen')
                    except Exception:  # pylint: disable=W0703
                        sys.stderr.write('ERROR: Doxygen not installed ' +
                                         '(required for documentation).\n')
                        return

                    reprocess = True
                    ref = os.path.join(working_dir, 'html', 'index.html')
                    if os.path.exists(ref) and not self.force:
                        reprocess = False
                        for d in environ['C_SOURCE_DIRS'].split(' '):
                            for orig in glob.glob(os.path.join(d, '*.h*')):
                                if os.path.getmtime(ref) < \
                                   os.path.getmtime(orig):
                                    reprocess = True
                                    break
                    if reprocess:
                        if self.distribution.verbose:
                            out = sys.stdout
                            err = sys.stderr
                        else:
                            out = err = open('doxygen.log', 'w')
                        os.chdir(working_dir)
                        cmd_line = [doxygen_exe, dext.doxygen_cfg]
                        status = subprocess.call(cmd_line,
                                                 stdout=out, stderr=err)
                        if status != 0:
                            raise Exception("Command '" + str(cmd_line) +
                                            "' returned non-zero exit status "
                                            + str(status))

                        if not self.distribution.verbose:
                            out.close()
                        copy_tree('html', os.path.join(target, 'html'), True,
                                  excludes=['.svn', 'CVS', '.git', '.hg*'])
                        os.chdir(here)
                        create_breathe_stylesheet(target)

                for f in dext.extra_docs:
                    shutil.copy(os.path.join(doc_dir, f), target)

                ## Sphinx
                if dext.without_sphinx:
                    return
                if dext.sphinx_config is None:
                    level_up = os.path.dirname(os.path.dirname(__file__))
                    dext.sphinx_config = os.path.join(level_up,
                                                      'sphinx_conf.py.in')
                elif os.path.dirname(dext.sphinx_config) == '':
                    dext.sphinx_config =  os.path.join(doc_dir,
                                                       dext.sphinx_config)
                configure_file(environ, dext.sphinx_config,
                               os.path.join(working_dir, 'conf.py'))
                import warnings
                try:
                    import sphinx
                except ImportError:
                    configure_package('breathe')  ## requires sphinx
                    sys.path.insert(0, os.path.join(options.target_build_dir,
                                                    options.local_lib_dir))

                from sphinx.application import Sphinx
                if 'windows' in platform.system().lower() or \
                   not build_verbose:
                    from sphinx.util.console import nocolor
                warnings.filterwarnings("ignore",
                                        category=PendingDeprecationWarning)
                warnings.filterwarnings("ignore", category=UserWarning)

                status = sys.stdout
                if not build_verbose:
                    status = open('sphinx.log', 'w')
                if 'windows' in platform.system().lower() or not build_verbose:
                    nocolor()
                try:
                    sphinx_app = Sphinx(working_dir, working_dir, target,
                                        os.path.join(target, '.doctrees'),
                                        'html', None, status)
                    sphinx_app.build(True)
                except Exception:  # pylint: disable=W0703
                    if build_verbose:
                        print('ERROR: ' + str(sys.exc_info()[1]))
                    else:
                        pass
                if not build_verbose:
                    status.close()
                warnings.resetwarnings()
