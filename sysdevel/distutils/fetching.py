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


from .filesystem import mkdir
from . import options


class DownloadError(Exception):
    pass


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


def fetch(website, remote, local, quiet=False):
    mkdir(options.download_dir)
    set_downloading_file(remote)
    if not os.path.exists(os.path.join(options.download_dir, local)):
        url = website + '/' + remote
        if website.endswith('/'):
            url = website + remote
        urlretrieve(url, os.path.join(options.download_dir, local),
                    download_progress, quiet=quiet)
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
            ## Ugly, but neccessary (neither gzip nor zlib packages work)
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
        z, _ = open_archive(archive, archive_dir)
        if archive.endswith('.zip'):
            zipextractall(z)
        else:
            tarextractall(z)
        z.close()
        os.chdir(here)


def urlretrieve(url, filename=None, progress=None, data=None, proxy=None,
                quiet=False):
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
        if not quiet:
            sys.stderr.write("HTTP Error connecting to " + url + ":\n")
        raise

    if size >= 0 and read < size:
        raise ContentTooShortError("%s: retrieval incomplete: "
                                   "got only %i out of %i bytes" %
                                   (url, read, size), result)

    return result
