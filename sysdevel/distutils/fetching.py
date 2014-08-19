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
Utilities for downloading and unpacking archives
"""

import os
import sys
import tarfile
import zipfile
import tempfile
import shutil

try:
    # pylint: disable=F0401,E0611
    from urllib.request import ProxyHandler, build_opener, install_opener
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError, ContentTooShortError
except ImportError:
    from urllib2 import ProxyHandler, build_opener, install_opener
    from urllib2 import Request, urlopen
    from urllib2 import URLError, HTTPError
    from urllib import ContentTooShortError


from sysdevel.distutils.filesystem import mkdir
from sysdevel.distutils import options


class DownloadError(Exception):
    def __init__(self, which, url=None, code=None):
        # pylint: disable=W0231
        self.header = 'DownloadError -- '
        self.explanation = ''
        if not url is None:
            self.explanation += str(url) + ' : '
        self.explanation += which
        if not code is None:
            self.explanation += ' ' + str(code)

    def __str__(self):
        return str(self.explanation)

    def __repr__(self):
        return str(self.header) + str(self.explanation)



__DOWNLOAD_FILE = ''

def set_downloading_file(dlf):
    '''
    Set the global for the download_progress callback below.
    '''
    global __DOWNLOAD_FILE  # pylint: disable=W0603
    __DOWNLOAD_FILE = dlf

def download_progress(count, block_size, total_size):
    '''
    Callback for displaying progress for use with urlretrieve()
    '''
    percent = int(count * block_size * 100 / total_size)
    if options.VERBOSE:
        sys.stdout.write("\rFETCHING " + __DOWNLOAD_FILE + "  %2d%%" % percent)
        sys.stdout.flush()


def fetch(website, remote, local, dwnld_dir=options.download_dir):
    mkdir(dwnld_dir)
    set_downloading_file(remote)
    if not os.path.exists(os.path.join(dwnld_dir, local)):
        url = website + '/' + remote
        if website.endswith('/'):
            url = website + remote
        urlretrieve(url, os.path.join(dwnld_dir, local), download_progress)
        if options.VERBOSE:
            sys.stdout.write('\n')


def zipextractall(zip_file):
    ## zip_file.extractall not in 2.4
    for name in zip_file.namelist():
        (dirname, filename) = os.path.split(name)
        if not os.path.exists(dirname):
            mkdir(dirname)
        if not filename == '':
            f = open(name, 'w')
            f.write(zip_file.read(name))
            f.close()

    
def tarextractall(tar_file):
    ## tar_file.extractall not in 2.4
    for tarinfo in tar_file:
        tar_file.extract(tarinfo)


def open_archive(archive, archive_dir=None):
    if archive_dir is None:
        archive_dir = options.download_dir
    if archive.endswith('.tar.Z'):
        if not os.path.exists(os.path.join(archive_dir, archive[:-2])):
            ## Ugly, but necessary (neither gzip nor zlib packages work)
            here = os.path.abspath(os.getcwd())
            os.chdir(archive_dir)
            os.system('gunzip ' + archive)
            os.chdir(here)
        archive = archive[:-2]

    if archive.endswith('.tgz') or archive.endswith('.tar.gz'):
        z = tarfile.open(os.path.join(archive_dir, archive), 'r:gz')
        names = z.getnames()
    elif archive.endswith('.tar.bz2'):
        z = tarfile.open(os.path.join(archive_dir, archive), 'r:bz2')
        names = z.getnames()
    elif archive.endswith('.tar'):
        z = tarfile.open(os.path.join(archive_dir, archive), 'r:')
        names = z.getnames()
    elif archive.endswith('.zip'):
        z = zipfile.ZipFile(os.path.join(archive_dir, archive), 'r')
        names = z.namelist()
    else:
        raise DownloadError('Unsupported archive compression: ' + archive)

    return z, names

    
def unarchive(archive, target, archive_dir=None):
    if archive_dir is None:
        archive_dir = options.download_dir
    here = os.path.abspath(os.getcwd())
    if not os.path.isabs(archive_dir):
        archive_dir = os.path.join(here, archive_dir)
    if not os.path.exists(os.path.join(options.target_build_dir, target)):
        mkdir(options.target_build_dir)
        os.chdir(options.target_build_dir)
        z, members = open_archive(archive, archive_dir)
        root = os.path.commonprefix(members)
        if root.endswith(os.sep):
            root = root[:-1]
        if root == '':
            root = target
            mkdir(target)
            os.chdir(target)
        if archive.endswith('.zip'):
            zipextractall(z)
        else:
            tarextractall(z)
        z.close()
        if root != target:
            shutil.move(root, target)
        os.chdir(here)


def urlretrieve(url, filename=None, progress=None, data=None, proxy=None):
    '''
    Identical to urllib.urlretrieve, except that it handles
    SSL, proxies, and redirects properly.
    '''
    proxy_url = proxy
    if proxy_url is None:
        try:
            proxy_url = os.environ['HTTP_PROXY']
        except KeyError:
            try:
                proxy_url = os.environ['http_proxy']
            except KeyError:
                pass

    if not proxy_url is None:
        proxies = ProxyHandler({'http': proxy_url, 'https': proxy_url})
        opener = build_opener(proxies)
    else:
        opener = build_opener()
    install_opener(opener)

    try:
        req = Request(url=url, data=data)
        fp = urlopen(req)
        try:
            headers = fp.info()
            if filename:
                tfp = open(filename, 'wb')
            else:
                tfp = tempfile.NamedTemporaryFile(delete=False)
                filename = tfp.name

            try:
                result = filename, headers
                size = -1
                bs = 1024*8
                read = 0
                blocknum = 0
                if "content-length" in headers:
                    size = int(headers["Content-Length"])
                if progress:
                    progress(blocknum, bs, size)

                while True:
                    block = fp.read(bs)
                    if not block or block == "":
                        break
                    read += len(block)
                    tfp.write(block)
                    blocknum += 1
                    if progress:
                        progress(blocknum, bs, size)
            finally:
                tfp.close()
        finally:
            fp.close()
        del fp
        del tfp
    except (URLError, HTTPError):
        exc_class, exc, tb = sys.exc_info()
        which = str(getattr(exc, 'reason', str(exc_class.__name__)))
        new_exc = DownloadError(which, url, str(getattr(exc, 'code', None)))
        raise new_exc.__class__, new_exc, tb

    if size >= 0 and read < size:
        raise ContentTooShortError("%s: retrieval incomplete: "
                                   "got only %i out of %i bytes" %
                                   (url, read, size), result)

    return result
