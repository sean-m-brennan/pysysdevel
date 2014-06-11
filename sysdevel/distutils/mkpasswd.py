#!/usr/bin/env python

import os
import sys
import base64
import platform

password = sys.argv[1]

if platform.system().lower() == 'linux':
    import crypt
    salt = base64.b64encode(os.urandom(16))
    print crypt.crypt(password, "$6$" + salt + "$")
else:
    ## requires Python passlib package (https://pythonhosted.org/passlib)
    from passlib.hash import sha512_crypt
    print sha512_crypt.encrypt(password, rounds=5000)
