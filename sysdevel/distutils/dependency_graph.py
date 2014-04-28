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
import os

from .dag import dag
from .configuration import find_package_config
from .prerequisites import RequirementsFinder


# pylint: disable=W0613
def _fetch_deps(short_name, helper, version, strict, setup_dir=None):
    try:
        cfg = helper.configuration()
    except Exception:
        ver_info = ''
        if not version is None:
            ver_info = ' v.' + str(version)
        print('Error loading ' + short_name + ver_info + ' configuration.\n')
        raise
    if not version is None:
        results = [(short_name, version, strict)]
    else:
        results = [short_name]
    for dep in cfg.dependencies:
        results.append(find_package_config(dep, _fetch_deps))
    return results


def _recurse_prereqs(path):
    rf = RequirementsFinder(os.path.join(path, 'setup.py'))
    required = [rf.package]
    for _, pkg_dir in rf.subpackages_list:
        required.append(_recurse_prereqs(os.path.join(path, pkg_dir)))
    for pkg in rf.requires_list:
        required.append(find_package_config(pkg, _fetch_deps, setup_dir=path))
    for pkg in rf.prerequisite_list:
        required.append(find_package_config(pkg, _fetch_deps, setup_dir=path))
    return required



def get_dep_dag(pkg_path):
    '''
    Construct a directed acyclic graph of dependencies.
    Takes the path of the root package.
    '''
    # pylint: disable=W0212
    graph = dag(_recurse_prereqs(pkg_path))

    ## remove duplicates where name,version,strict tuple equals name string
    adjacency_list = dict(graph.adjacency_list())
    changed = []
    for dep in adjacency_list.keys():
        if isinstance(dep, tuple):
            if dep[0] in adjacency_list.keys():
                changed.append(dep)
                graph._graph[dep] = graph._graph.pop(dep[0])
    adjacency_list = dict(graph.adjacency_list())
    for dep in changed:
        for k,v in adjacency_list.items():
            if dep[0] in v:
                graph._graph[k] = [x if x != dep[0] else dep for x in v]

    return graph
