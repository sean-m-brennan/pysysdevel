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
Utilities for accessing remote data and computation resources.
"""

import os
import subprocess
import platform
import getpass
import warnings


########################################
## Data resources

class Storage(object):
    def mount(*args, **kwargs):
        raise NotImplementedError('Mount type unknown')

    def unmount(*args, **kwargs):
        raise NotImplementedError('Mount type unknown')



class SshStorage(Storage):
    def __init__(self, host, remote_path, remote_user=None, local_path=None):
        Storage.__init__(self)
        if 'windows' in platform.system().lower():
            raise Exception('SSHfs not supported for Windows')
        self.host = host
        self.path = remote_path
        self.user = remote_user
        if remote_user is None:
            self.user = getpass.getuser()
        self.where = local_path
        if local_path is None:
            self.where = os.path.basename(remote_path)
        self.remove_local = False


    def mount():
        """
        Mount a remote filesystem using sshfs.
        Must have previously configured and loaded passwordless ssh keys.
        """
        if not os.path.is_dir(self.where):
            os.mkdir(self.where)
            self.remove_local = True

        resource = self.user + '@' + self.host + ':' + self.path
        cmd_line = ['sshfs', resource, self.where]
        status = subprocess.call(cmd_line)
        if status != 0:
            raise subprocess.CalledProcessError(status, cmd_line)


    def umount():
        if os.path.exists(self.where):
            cmd_line = ['fusermount', '-u', self.where]
            status = subprocess.call(cmd_line)
            if status != 0:
                raise subprocess.CalledProcessError(status, cmd_line)
            if self.remove_local:
                os.rmdir(self.where)



class NfsStorage(Storage):
     def __init__(self, host, remote_path, local_path=None):
        Storage.__init__(self)
        self.host = host
        self.path = remote_path
        self.where = local_path
        if local_path is None:
            self.where = os.path.basename(remote_path)
        self.remove_local = False


    def mount():
        """
        Mount a remote filesystem using nfs.
        Target must exist and host and local uids or guids must agree.
        For Windows, requires Client Services for NFS.
        """
        if not os.path.is_dir(self.where):
            os.mkdir(self.where)
            self.remove_local = True

        resource = self.host + ':' + self.path
        cmd_line = ['mount', '-t', 'nfs', resource, self.where]
        if 'windows' in platform.system().lower():
            resource = '//' + self.host + '/' + self.path
            cmd_line = ['mount', resource, self.where]

        status = subprocess.call(cmd_line)
        if status != 0:
            raise subprocess.CalledProcessError(status, cmd_line)


    def umount():
        if os.path.exists(self.where):
            cmd_line = ['umount', self.where]
            status = subprocess.call(cmd_line)
            if status != 0:
                raise subprocess.CalledProcessError(status, cmd_line)
            if self.remove_local:
                os.rmdir(self.where)



class SmbStorage(Storage):
     def __init__(self, host, share, remote_user=None, local_path=None):
        Storage.__init__(self)
        self.host = host
        self.path = share
        self.user = remote_user
        if remote_user is None:
            self.user = getpass.getuser()
        self.where = local_path
        if local_path is None:
            self.where = os.path.basename(remote_path)
        self.remove_local = False
        warnings.warn('SMB can be problematic and is almost certainly ' + \
                          '*not* what you want. Try CifsStorage for ' + \
                          'Windows shares instead.')


    def mount():
        """
        Mount a remote filesystem using samba.
        For 'passwordless' mounting:
        cat > '~/.smbcredentials' << EOF
        username=USER
        password=PASSWORD
        EOF
        """
        if not os.path.is_dir(self.where):
            os.mkdir(self.where)
            self.remove_local = True

        resource = '//' + self.user + '@' + self.host + '/' + self.path
        cmd_line = ['mount', '-t', 'smbfs', resource, self.where]
        if 'windows' in platform.system().lower():
            resource = '\\\\' + self.host + '\\' + self.path
            cmd_line = ['net', 'use', self.where,
                        resource, '/user:' + self.user]

        status = subprocess.call(cmd_line)
        if status != 0:
            raise subprocess.CalledProcessError(status, cmd_line)


    def umount():
        if os.path.exists(self.where):
            cmd_line = ['umount', self.where]
            if 'windows' in platform.system().lower():
                cmd_line = ['net', 'use', self.where, '/delete']
            status = subprocess.call(cmd_line)
            if status != 0:
                raise subprocess.CalledProcessError(status, cmd_line)
            if self.remove_local:
                os.rmdir(self.where)



class CifsStorage(Storage):
     def __init__(self, host, share, remote_user=None, domain=None,
                  local_path=None):
        Storage.__init__(self)
        self.host = host
        self.path = remote_path
        self.user = remote_user
        if remote_user is None:
            self.user = getpass.getuser()
        self.domain = domain
        self.where = local_path
        if local_path is None:
            self.where = os.path.basename(remote_path)
        self.remove_local = False


    def mount():
        """
        Mount a remote filesystem using cifs (Active Directory).
        For 'passwordless' mounting:
        cat > '~/.smbcredentials' << EOF
        username=DOMAIN\USER
        password=PASSWORD
        EOF
        """
        if not os.path.is_dir(self.where):
            os.mkdir(self.where)
            self.remove_local = True

        resource = '//' + self.host + '/' + self.path
        options = ['username=' + self.user]
        use_options = False
        if self.domain != None:
            options.append('domain=' + self.domain)
            use_options = True
        cmd_line = ['mount', '-t', 'cifs', resource, self.where]
        if use_options:
            cmd_line += ['-o', ','.join(options)]
        if 'windows' in platform.system().lower():
            resource = '\\\\' + self.host + '\\' + self.path
            user_id = self.user
            if self.domain != None:
                user_id = self.domain + '\\' + self.user
            cmd_line = ['net', 'use', self.where,
                        resource, '/user:' + user_id]

        status = subprocess.call(cmd_line)
        if status != 0:
            raise subprocess.CalledProcessError(status, cmd_line)


    def umount():
        if os.path.exists(self.where):
            cmd_line = ['umount', self.where]
            if 'windows' in platform.system().lower():
                cmd_line = ['net', 'use', self.where, '/delete']
            status = subprocess.call(cmd_line)
            if status != 0:
                raise subprocess.CalledProcessError(status, cmd_line)
            if self.remove_local:
                os.rmdir(self.where)




########################################
## Computation resources


