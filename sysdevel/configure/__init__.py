"""
Entry point for finding/installing required libraries
"""

import os
import sys
import platform

from sysdevel import util


class FatalError(SystemExit):
    """
    Uncatchable error, exits uncleanly.
    """
    def __init__(self, what):
        sys.stderr.write('FatalError: ' + what + '\n')
        sys.stderr.flush()
        os._exit(-1)


def simplify_version(version):
    if isinstance(version, float):
        return str(version)
    elif isinstance(version, str):
        ver_tpl = version.split('.')
        return ver_tpl[0] + '.' + ver_tpl[1]


def configure_system(prerequisite_list, version, required_python_version='2.4',
                     install=True, quiet=False):
    '''
    Given a list of required software and optionally a Python version,
    verify that python is the proper version and that
    other required software is installed.
    Install missing prerequisites that have an installer defined.
    '''
    environment = util.read_cache()
    skip = False
    for idx, arg in enumerate(sys.argv[:]):
        if arg.startswith('clean'):
            skip = True
            quiet = True

    pyver = simplify_version(platform.python_version())
    reqver = simplify_version(required_python_version)
    if pyver < reqver:
        raise FatalError('Python version >= ' + reqver + ' is required.  ' +
                         'You are running version ' + pyver)

    if not quiet:
        sys.stdout.write('CONFIGURE  ')
        if len(environment):
            sys.stdout.write('(from cache)')
        sys.stdout.write('\n')
    environment['PACKAGE_VERSION'] = version

    prerequisite_list.insert(0, 'httpsproxy_urllib2_py')
    if 'windows' in platform.system().lower() and \
            util.in_prerequisites('mingw', prerequisite_list) and \
            util.in_prerequisites('boost', prerequisite_list) and not \
            util.in_prerequisites('msvcrt', prerequisite_list):
        print "WARNING: if you're using the boost-python DLL, " + \
            "also add 'msvcrt' as a prereuisite."
    if 'darwin' in platform.system().lower() and \
            not util.in_prerequisites('macports', prerequisite_list) and \
            not util.in_prerequisites('homebrew', prerequisite_list):
        if os.path.exists(os.path.join(os.path.sep,
                                       'opt', 'local', 'share', 'macports')):
            prerequisite_list.insert(0, 'macports')
        elif os.path.exists(os.path.join(os.path.sep,
                                         'usr', 'local', 'bin', 'brew')):
            prerequisite_list.insert(0, 'homebrew')
        else:
            print "WARNING: neither MacPorts nor Homebrew detected. " +\
                "All required libraries will be built locally."

    for help_name in prerequisite_list:
        environment = __configure_package(environment, help_name,
                                          skip, install, quiet)
    util.save_cache(environment)

    return environment


def __configure_package(environment, help_name, skip, install, quiet):
    req_version = None
    if not isinstance(help_name, basestring):
        req_version = help_name[1]
        help_name = help_name[0]
    base = help_name
    full_name = 'sysdevel.configure.' + help_name
    try:
        __import__(full_name)
    except ImportError, e:
        full_name = 'sysdevel.configure.' + help_name + '_py'
        try:
            __import__(full_name)
        except ImportError, e:
            full_name = 'sysdevel.configure.' + help_name + '_js'
            try:
                __import__(full_name)
            except ImportError, e:
                sys.stderr.write('No setup helper module ' + base + '\n')
                raise e
    return __run_helper__(environment, help_name, full_name,
                          req_version, skip, install, quiet)


configured = []

def __run_helper__(environment, short_name, long_name, version,
                   skip, install, quiet):
    helper = sys.modules[long_name]
    configured.append(short_name)
    cfg = helper.configuration()
    for dep in cfg.dependencies:
        dep_name = dep
        if not isinstance(dep, basestring):
            dep_name = dep[0]
        if dep_name in configured:
            continue
        environment = __configure_package(environment, dep,
                                          skip, install, quiet)
        util.save_cache(environment)
    if not quiet:
        sys.stdout.write('Checking for ' + short_name + ' ')
        if not version is None:
            sys.stdout.write('v.' + version)
        sys.stdout.write('\n')
        sys.stdout.flush()
    if skip:
        cfg.null()
    elif not cfg.is_installed(environment, version):
        if not install:
            raise Exception(help_name + ' cannot be found.')
        cfg.install(environment, version)
    env = dict(cfg.environment.items() + environment.items())
    util.save_cache(env)  ## intermediate cache
    return env
