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
recursive build support
"""

import os
import sys
import subprocess

from .building import process_progress


def process_package(fnctn, build_base, progress, pyexe, argv,
                    pkg_name, pkg_dir, addtnl_args=[]):
    sys.stdout.write(fnctn.upper() + 'ING ' + pkg_name + ' in ' + pkg_dir + ' ')
    logging = True
    if 'clean' in fnctn:
        logging = False
    log_file = os.path.join(build_base, pkg_name + '_' + fnctn + '.log')
    if logging:
        log = open(log_file, 'w')
    else:
        log = open(os.devnull, 'w')
    try:
        p = subprocess.Popen([pyexe, os.path.join(pkg_dir, 'setup.py'),
                              ] + argv + addtnl_args,
                             stdout=log, stderr=log)
        status = progress(p)
        log.close()
    except KeyboardInterrupt:
        p.terminate()
        log.close()
        status = 1
    if status != 0:
        sys.stdout.write(' failed')
        if logging:
            sys.stdout.write('; See ' + log_file)
    else:
        sys.stdout.write(' done')
    sys.stdout.write('\n')           
    return pkg_name, status


def process_subpackages(parallel, fnctn, build_base, subpackages,
                        argv, quit_on_error):
    failed_somewhere = False
    try:
        if not parallel:
            raise ImportError
        ## parallel building
        import pp
        job_server = pp.Server()
        results = [job_server.submit(process_package,
                                     (fnctn, build_base, process_progress,
                                      sys.executable, argv,) + sub,
                                     (), ('os', 'subprocess',))
                   for sub in subpackages]
        has_failed = False
        for result in results:
            res_tpl = result()
            if res_tpl is None:
                raise Exception("Parallel build failed.")
            pkg_name, status = res_tpl
            if status != 0:
                has_failed = True
        if has_failed:
            failed_somewhere = True
            if quit_on_error:
                sys.exit(status)

    except ImportError: ## serial building
        for sub in subpackages:
            args = (fnctn, build_base, process_progress,
                    sys.executable, argv,) + sub
            pkg_name, status = process_package(*args)
            if status != 0:
                failed_somewhere = True
                if quit_on_error:
                    sys.exit(status)

    return failed_somewhere
