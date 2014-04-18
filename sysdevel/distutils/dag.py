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

class dag(object):
    """
    Directed acyclic graph.
    """
    def __init__(self, arg):
        if isinstance(arg, dag):
            ## pre-screened for cycles
            self._root = arg._deepcopy()  # pylint: disable=W0212
        elif isinstance(arg, dict):
            ## no cycles possible (would be duplicate keys)
            self._root = arg
        elif isinstance(arg, list):
            adj = self._adj_lst(arg)  # pylint: disable=W0212
            cycles = self._detect_cycles(adj)  # pylint: disable=W0212
            if cycles:
                raise TypeError("Initializing an acyclic graph with cycle(s) " +
                                "due to node(s): " + str(cycles) + ".")
            self._root = dict(adj)
        else:
            raise TypeError("Initializing a dag requires either an adjacency " +
                            "dictionary, a list of lists or another dag.")

    def _detect_cycles(self, lstlst):
        nodes = [l[0] for l in lstlst]
        dupl = set([x for x in nodes if nodes.count(x) > 1])
        if len(dupl) < 1:
            return []
        def entuple(lst):
            if isinstance(lst, list):
                return tuple(entuple(x) for x in lst)
            return lst
        tpltpl = entuple(lstlst)
        cycles = []
        for n in dupl:
            s = set()
            for t in tpltpl:
                if t[0] == n:
                    s.add(tuple(t))
            if len(s) > 1:
                cycles.append(n)
        return cycles

    def _deepcopy(self, arg=None):
        if arg is None:
            arg = self._root
        if isinstance(arg, list):
            return [self._deepcopy(x) for x in arg]  # pylint: disable=W0212
        return dict(arg.items())

    def _adj_lst(self, arg):
        if len(arg) == 1:
            return [[arg[0], []]]
        result = [[arg[0], [l[0] for l in arg[1:]]]]
        for l in arg[1:]:
            result += self._adj_lst(l)
        return result

    def adjacency_list(self):
        return self._root

    def list(self):
        """
        Return hierarchical list of lists representation (undo _adj_lst())
        """
        def nest(key, adj):
            lsts = [key]
            if len(adj[key]) < 1:
                return lsts
            for n in adj[key]:
                lsts.append(nest(n, adj))
            return lsts
        first = list(self._root.items())[0][0]
        return nest(first, self._root)

    def __len__(self):
        """
        'len' operator: Return number of nodes and leaves
        """
        return len(set(self._root.keys()))

    def __str__(self):
        """
        'str' operator: Return string representation
        """
        return str(self.topological_sort()) #FIXME

    def __contains__(self, key):
        """
        'in' operator: Is key a node or leaf?
        """
        return key in self._root.keys()

    def __iter__(self):
        """
        Forward iterator
        """
        for key in self._root.keys():
            yield key

    def __reversed__(self):
        """
        'reversed' operator: Reverse iterator
        """
        for key in self._root.keys().reverse():
            yield key

    def __getitem__(self, key):
        """
        index operator: Get subtree at a node
        """
        return self._root[key]

    def __setitem__(self, key, value):
        """
        index assignment operator: Add/change children of a node
        """
        if not self.__contains__(key):
            raise IndexError
        root, parent = self.__descend(key, self._root)
        if type(value) is list:
            if len(value) == 1:
                value = [value]
        else:
            value = [value]
        parent[parent.index(root)] = [root[0]] + value

    def topological_sort(self):
        """
        Single list in order from leaves to root
        """
        ## DAG is guaranteed to be acyclic from constructor
        unsorted_g = dict(self._root)  ## copy
        sorted_g = []
        while unsorted_g:
            for node, edges in unsorted_g.items():
                ## enforce depth-first traversal
                if  next((False for edge in edges
                          if edge in unsorted_g.keys()), True):
                    del unsorted_g[node]
                    sorted_g.append(node)
        return sorted_g



def test():
    sample1 = ['a', ['b', ['c', ['d'], ['e']], ['f']], ['g', ['h']], ['i']]
    if dag(sample1).topological_sort() != \
       ['e', 'd', 'f', 'i', 'h', 'c', 'b', 'g', 'a']:
        raise RuntimeError('Failed test 1')
    if dag(sample1).list() != sample1:
        raise RuntimeError('Failed test 2')

    sample2 = ['a', ['b', ['c', ['d'], ['e']], ['f', ['a']]], ['g', ['h']], ['i']]
    try:
        dag(sample2)
        raise RuntimeError('Failed test 3')
    except TypeError:
        pass

    sample3 = ['a', ['b', ['c', ['i'], ['e']], ['f']], ['g', ['h']], ['i']]
    if dag(sample3).topological_sort() != \
       ['e', 'f', 'i', 'h', 'c', 'b', 'g', 'a']:
        raise RuntimeError('Failed test 4')

    print 'Success'
