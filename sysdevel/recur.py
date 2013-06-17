"""
recursive build support
"""

import os
import sys
import subprocess

import util


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
                                     (fnctn, build_base, util.process_progress,
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
            args = (fnctn, build_base, util.process_progress,
                    sys.executable, argv,) + sub
            pkg_name, status = process_package(*args)
            if status != 0:
                failed_somewhere = True
                if quit_on_error:
                    sys.exit(status)

    return failed_somewhere
