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

"""
'build_docbook' command using emacs on org-mode files
"""


import os
import sys
import glob
import shutil
import subprocess

try:
    from numpy.distutils.command.build_ext import build_ext
except:
    from distutils.command.build_ext import build_ext

import util


def make_doc(src_file, target_dir=None, stylesheet=None):
    src_dir = os.path.abspath(os.path.dirname(src_file))
    if target_dir is None:
        pth = os.path.relpath(os.path.dirname(src_file)).split(os.sep)[1:]
        target_dir = os.path.join(util.target_build_dir, *pth)
    if stylesheet is None:
        stylesheet = 'http://docbook.sourceforge.net/release/fo/docbook.xsl'

    fop_exe = util.find_program('fop')
    java_exe = util.find_program('java')
    try:  ## prefer the jar
        classpaths = []
        try:
            for path in os.environ['CLASSPATH'].split(os.pathsep):
                classpaths.append(os.path.dirname(path))
        except:
            pass
        try:
            classpaths.append(os.path.join(os.environ['JAVA_HOME'], 'lib'))
        except:
            pass
        saxon_jar = util.find_file('saxon*.jar',
                                   ['/usr/share/java', '/usr/local/share/java',
                                    '/opt/local/share/java',] + classpaths)
        resolver_jar = util.find_file('resolver*.jar',
                                      ['/usr/share/java',
                                       '/usr/local/share/java',
                                       '/opt/local/share/java',] + classpaths)
        saxon_exe = [java_exe,  '-classpath',
                     os.pathsep.join([saxon_jar, resolver_jar]),
                     'net.sf.saxon.Transform']
    except:
        saxon_exe = [util.find_program('saxon')]
    if not os.path.exists(target_dir):
        util.mkdir(target_dir)
    support = glob.glob(os.path.join(os.path.dirname(__file__),
                                     'support', '*.xsl'))
    for s in support:
        shutil.copy(s, target_dir)
    util.copy_tree(src_dir, target_dir)

    ## Need to respect relative paths
    here = os.getcwd()
    os.chdir(target_dir)
    src_base = os.path.basename(src_file)
    fo_src = os.path.splitext(src_base)[0] + '.fo'
    pdf_dst = os.path.splitext(src_base)[0] + '.pdf'

    cmd_line = saxon_exe + [src_base, '-o:' + fo_src, '-xsl:' + stylesheet]
    if 'XML_CATALOG_FILES' in os.environ:
        cmd_line += ['-catalog:' + os.environ['XML_CATALOG_FILES']]
    subprocess.check_call(" ".join(cmd_line), shell=True)

    cmd_line = [fop_exe, '-fo', fo_src, '-pdf', pdf_dst]
    subprocess.check_call(" ".join(cmd_line), shell=True)
    os.chdir(here)


class build_docbook(build_ext):
    '''
    Build pdfs from docbook xml
    '''
    def run(self):
        if not self.distribution.doc_dir:
            return

        build = self.get_finalized_command('build')
        target = os.path.abspath(os.path.join(build.build_base, 'docs'))

        # FIXME filename or (filename, stylesheet) from self.distribution
        xml_files = glob.glob(os.path.join(self.distribution.doc_dir, '*.xml'))
        for xfile in xml_files:
            make_docs(xfile, target)
