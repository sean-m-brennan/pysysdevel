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
'build_org' command using emacs on org-mode files
"""

import os
import glob
import shutil
import subprocess

try:
    from numpy.distutils.command.build_ext import build_ext
except ImportError:
    from distutils.command.build_ext import build_ext

from sysdevel.distutils.prerequisites import find_program
from sysdevel.distutils.filesystem import mkdir, copy_tree
from sysdevel.distutils import options


def make_doc(src_file, target_dir=None, mode='docbook'):
    if target_dir is None:
        pth = os.path.relpath(os.path.dirname(src_file)).split(os.sep)[1:]
        # pylint: disable=W0142
        target_dir = os.path.join(options.target_build_dir, *pth)

    emacs_exe = find_program('emacs')
    src_dir = os.path.abspath(os.path.dirname(src_file))
    mkdir(target_dir)
    copy_tree(src_dir, target_dir)
    cfg_filename = os.path.join(target_dir, '.emacs')
    cfg = open(cfg_filename, 'w')
    cfg.write("(require 'org-latex)\n" +
              "(unless (boundp 'org-export-latex-classes)\n" +
              "  (setq org-export-latex-classes nil))\n" +
              "(add-to-list 'org-export-latex-classes\n" +
              "             '(\"short-book\"\n" +
              "               \"\\\\documentclass{book}\"\n" +
              "               (\"\\\\chapter{%s}\" . \"\\\\chapter*{%s}\")\n" +
              "               (\"\\\\section{%s}\" . \"\\\\section*{%s}\")\n" +
              "               (\"\\\\subsection{%s}\" . \"\\\\subsection*{%s}\")\n" +
              "               (\"\\\\subsubsection{%s}\" . \"\\\\subsubsection*{%s}\"))\n" +
              "             )\n"
          )
    cfg.close()

    ## Check version of org-mode
    cmd_line = [emacs_exe, '--batch', "--execute='(message (org-version))'"]
    p = subprocess.Popen(" ".join(cmd_line), shell=True,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    _, err = p.communicate()
    version_eight = False
    try:
        last = err.split('\n')[-2]
        if int(last[:last.index('.')]) > 7:
            version_eight = True
    except:
        raise Exception("Emacs does not have Org mode support.")

    ## Emacs Org mode export
    cmd_line = [emacs_exe, '--batch',
                "--execute='(load-file \"" + cfg_filename + "\"))'",
                '--visit=' + src_file]
    base_filename = os.path.splitext(os.path.basename(src_file))[0]
    if 'pdflatex' in mode:
        cmd_line.append("--execute='(org-export-as-pdf nil)'")
        result_files = [base_filename + '.tex', base_filename + '.pdf',]
    elif 'latex' in mode:
        cmd_line.append("--execute='(org-export-as-latex nil)'")
        result_files = [base_filename + '.tex']
    elif 'html' in mode:
        cmd_line.append("--execute='(org-export-as-html nil)'")
        result_files = [base_filename + '.html']
    else:
        if version_eight:
            ## TODO  texinfo for org v8.0+
            raise Exception("Emacs Org mode v8.0+ is not (yet) supported")
        else:
            cmd_line.append("--execute='(org-export-as-docbook nil)'")
            result_files = [base_filename + '.xml']

    subprocess.check_call(" ".join(cmd_line), shell=True)
    os.remove(cfg_filename)

    for r in result_files:
        shutil.move(os.path.join(src_dir, r),
                    os.path.join(target_dir, r))
    return os.path.join(target_dir, result_files[-1])


# pylint: disable=W0201
class build_org(build_ext):
    description = "Transform Emacs Org-mode documentation"
    user_options = [('latex', None, 'transform org to latex'),
                    ('html', None, 'transform org to html'),
                    ('docbook', None,
                     'transform org to docbook xml (default)'),]

    def initialize_options(self):
        self.latex = False
        self.html = False
        self.docbook = False
        self.mode = 'docbook'

    def finalize_options(self):
        if not self.latex and not self.html:
            self.docbook = True
        if self.latex:
            self.mode = 'latex'
        if self.html:
            self.mode = 'html'
        if self.docbook:
            self.mode = 'docbook'


    def run(self):
        build = self.get_finalized_command('build')
        target = os.path.abspath(os.path.join(build.build_base, 'docs'))

        for dext in self.distribution.doc_modules:
            if dext.org_mode:  ## must be provided to trigger this
                for src in glob.glob(os.path.join(dext.source_directory,
                                                  '*.org')):
                    make_doc(src, target, dext.org_modemode)

        if not self.distribution.doc_dir:
            return

        for src in glob.glob(os.path.join(self.distribution.doc_dir, '*.org')):
            make_doc(src, target, self.mode)
