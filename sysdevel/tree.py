"""
Copyright 2013.  Los Alamos National Security, LLC. This material was
produced under U.S. Government contract DE-AC52-06NA25396 for Los
Alamos National Laboratory (LANL), which is operated by Los Alamos
National Security, LLC for the U.S. Department of Energy. The
U.S. Government has rights to use, reproduce, and distribute this
software.  NEITHER THE GOVERNMENT NOR LOS ALAMOS NATIONAL SECURITY,
LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR ASSUMES ANY LIABILITY
FOR THE USE OF THIS SOFTWARE.  If software is modified to produce
derivative works, such modified software should be clearly marked, so
as not to confuse it with the version available from LANL.

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
Unordered tree with unique nodes
"""

class tree(object):
    """
    Unordered tree with unique nodes.
    """
    def __init__(self, arg):
        if isinstance(arg, tree):
            self._root = arg.__deepcopy()
        elif isinstance(arg, list):
            self._root = arg
            try:
                arg = self.__flat(self._root)  ## verify recursive nature
            except TypeError:
                raise TypeError("Initializing a tree requires " + \
                                    "that leaves are also lists.")
            if len(arg) != len(set(arg)):  ## verify uniqueness constraint
                raise TypeError("Initializing a tree requires " + \
                                    "unique nodes and leaves.")
        else:
            raise TypeError("Initializing a tree requires either a " +
                            "list of lists or another tree.")

    def __deepcopy(self, arg=None):
        if arg is None:
            arg = self._root
        if isinstance(arg, list):
            return list(map(self.__deepcopy, arg))
        return arg

    def __flat(self, subtree):
        result = [subtree[0]]
        for node in subtree[1:]:
            result += self.__flat(node)
        return result

    def flatten(self):
        """
        Return nodes and leaves as a flat list
        """
        return self.__flat(self._root)

    def list(self):
        """
        Return hierarchical list of lists representation
        """
        return self._root

    def __len__(self):
        """
        'len' operator: Return number of nodes and leaves
        """
        return len(self.flatten())

    def __str__(self):
        """
        'str' operator: Return string representation
        """
        return str(self._root)

    def __contains__(self, key):
        """
        'in' operator: Is key a node or leaf?
        """
        return key in self.flatten()

    def __iter__(self):
        """
        Forward iterator
        """
        for key in self.__flat(self._root):
            yield key

    def __reversed__(self):
        """
        'reversed' operator: Reverse iterator
        """
        for key in self.__flat(self._root).reverse():
            yield key

    def __descend(self, key, subtree, prev=None):
        if subtree[0] == key:
            return subtree, prev
        for node in subtree[1:]:
            result, prev = self.__descend(key, node, subtree)
            if result != None:
                return result, prev
        return None, None

    def __getitem__(self, key):
        """
        index operator: Get subtree at a node
        """
        if not self.__contains__(key):
            raise IndexError
        return self.__descend(key, self._root)[0]

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

    def subtree(self, key):
        """
        Return a subtree
        """
        if not self.__contains__(key):
            raise IndexError
        root, parent = self.__descend(key, self._root)
        return root

    def __delitem__(self, key):
        """
        'del' operator: Remove subtree
        """
        if not self.__contains__(key):
            raise IndexError
        root, parent = self.__descend(key, self._root)
        parent.remove(root)

    def remove(self, key):
        """
        Remove a subtree
        """
        self.__delitem__(key)

    def parent(self, key):
        """
        Returns parent of a node, if any
        """
        if not self.__contains__(key):
            raise IndexError
        lst = self.__descend(key, self._root)[1]
        if lst != None:
            return lst[0]
        return lst

    def root(self):
        """
        Returns the root node of the tree
        """
        return self._root[0]

    def __invert(self, subtree, leaves_only=False, parentage=None):
        if parentage is None:
            family_list = [subtree[0]]
        else:
            family_list = [subtree[0], parentage]
        if len(subtree) == 1:
            return [tree(family_list)]
        result = []
        for node in subtree[1:]:
            result += self.__invert(node, leaves_only, family_list)
        if leaves_only:
            return result
        return result + [tree(family_list)]

    def leaves(self):
        """
        Returns a list of tree leaves
        """
        lvs = []
        for l in self.__invert(self._root, True):
            lvs += [l.root()]
        return lvs

    def subtrees(self):
        """
        Produces a forest of all complete subtrees
        """
        return self.__invert(self._root)

    def inverted(self):
        """
        Produces a forest rooted at the leaves
        """
        return self.__invert(self._root, True)

    def __dive(self, subtree):
        if len(subtree) == 1:
            return 1;
        maximum = 0
        for node in subtree[1:]:
            value = self.__dive(node)
            if value > maximum:
                maximum = value
        return maximum + 1

    def depth(self):
        """
        Returns the maximum height of the tree
        """
        return self.__dive(self._root)
