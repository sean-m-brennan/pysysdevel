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
Utilities for portable filesystem manipulation
"""

import os
import fnmatch
import glob


def mkdir(newdir):
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("A *file* with the same name as the desired " +
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            mkdir(head)
        if tail:
            os.mkdir(newdir)


def copy_tree(src, dst, preserve_mode=1, preserve_times=1, preserve_symlinks=0,
              update=0, verbose=0, dry_run=0, excludes=[]):
    '''
    Extends distutils.dir_util.copy_tree to exclude given patterns
    '''
    from distutils import dir_util, file_util
    from distutils.errors import DistutilsFileError
    from distutils import log

    if not dry_run and not os.path.isdir(src):
        raise DistutilsFileError("cannot copy tree '%s': not a directory" % src)
    try:
        names = os.listdir(src)
    except OSError:
        e = sys.exc_info()[1]
        if dry_run:
            names = []
        else:
            raise DistutilsFileError("error listing files in '%s': %s" %
                                     (src, e.strerror))

    if not dry_run:
        dir_util.mkpath(dst)

    outputs = []

    for n in names:
        exclude = False
        for excl in excludes:
            if fnmatch.fnmatch(n, excl):
                exclude = True
        if exclude:
            if verbose:
                log.info("excluding %s from copy", n)
            continue

        src_name = os.path.join(src, n)
        dst_name = os.path.join(dst, n)

        if preserve_symlinks and os.path.islink(src_name):
            link_dest = os.readlink(src_name)
            log.info("linking %s -> %s", dst_name, link_dest)
            if not dry_run:
                os.symlink(link_dest, dst_name)
            outputs.append(dst_name)

        elif os.path.isdir(src_name):
            outputs.extend(
                copy_tree(src_name, dst_name, preserve_mode,
                          preserve_times, preserve_symlinks, update,
                          verbose, dry_run, excludes))
        else:
            file_util.copy_file(src_name, dst_name, preserve_mode,
                                preserve_times, update, None,
                                verbose=verbose, dry_run=dry_run)
            outputs.append(dst_name)

    return outputs



def recursive_chown(directory, uid, gid):
    for root, dirnames, filenames in os.walk(directory):
        for dirname in dirnames:
            os.chown(os.path.join(root, dirname), uid, gid)
        for filename in filenames:
            os.chown(os.path.join(root, filename), uid, gid)


def symlink(original, target):
    if not os.path.lexists(target):
        if not os.path.isabs(original):
            levels = len(target.split(os.sep))-1
            for l in range(levels):
                original = os.path.join('..', original)
        try:
            os.symlink(original, target)
        except:
            shutil.copyfile(original, target)


def is_out_of_date(target, source, additional=[]):
    extra = False
    for addtnl in additional:
        if os.path.exists(target) and os.path.exists(addtnl):
            extra = extra or os.path.getmtime(addtnl) > os.path.getmtime(target)

    if (not os.path.exists(target)) or extra or \
            (os.path.getmtime(source) > os.path.getmtime(target)):
        return True
    return False
 

def glob_insensitive(directory, file_pattern):
    def either(c):
        return '[%s%s]' % (c.lower(), c.upper()) if c.isalpha() else c
    return glob.glob(os.path.join(directory, ''.join(map(either, file_pattern))))


