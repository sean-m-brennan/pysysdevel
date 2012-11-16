# -*- coding: utf-8 -*-
"""
Package specification
"""
#**************************************************************************
# 
# This material was prepared by the Los Alamos National Security, LLC 
# (LANS), under Contract DE-AC52-06NA25396 with the U.S. Department of 
# Energy (DOE). All rights in the material are reserved by DOE on behalf 
# of the Government and LANS pursuant to the contract. You are authorized 
# to use the material for Government purposes but it is not to be released 
# or distributed to the public. NEITHER THE UNITED STATES NOR THE UNITED 
# STATES DEPARTMENT OF ENERGY, NOR LOS ALAMOS NATIONAL SECURITY, LLC, NOR 
# ANY OF THEIR EMPLOYEES, MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR 
# ASSUMES ANY LEGAL LIABILITY OR RESPONSIBILITY FOR THE ACCURACY, 
# COMPLETENESS, OR USEFULNESS OF ANY INFORMATION, APPARATUS, PRODUCT, OR 
# PROCESS DISCLOSED, OR REPRESENTS THAT ITS USE WOULD NOT INFRINGE 
# PRIVATELY OWNED RIGHTS.
# 
#**************************************************************************

class pkg_config(object):
    '''
    Package configuration class for use with pydevel.

    To create you custom configuration:
    create a config.py module wherein you subclass this object
    (eg. 'class subclass_config(pkg_config)'),
    then create an instance of your subclass named 'pkg'
    (eg. 'pkg = subclass_config(...)').
    '''
    def __init__(self, name, package_tree,
                 pkg_id, version, author, company, copyright, srcs, runscripts,
                 data_files=dict(), extra_data=[], req_pkgs=[], dyn_mods=[],
                 environ=dict(), prereq=[], redistrib=[],
                 img_dir='', build_dir=''):
        self.PACKAGE          = package_tree.root()
        self.NAME             = name
        self.VERSION          = version[:version.rindex('.')]
        self.RELEASE          = version
        self.COPYRIGHT        = copyright
        self.AUTHOR           = author
        self.COMPANY          = company
        self.ID               = pkg_id
        self.PACKAGE_TREE     = package_tree

        self.source_files     = srcs
        self.runscripts       = runscripts
        self.package_files    = data_files
        self.extra_data_files = extra_data
        self.required_pkgs    = req_pkgs
        self.dynamic_modules  = dyn_mods
        self.environment      = environ
        self.prerequisites    = prereq
        self.redistributed    = redistrib
        self.image_dir        = img_dir
        self.build_dir        = build_dir
        self.build_config     = 'release'

        self.package_names = dict((tree.root(),
                                   '_'.join(list(reversed(tree.flatten()))))
                                  for tree in self.PACKAGE_TREE.inverted())
        self.names         = dict((tree.root(),
                                   '.'.join(list(reversed(tree.flatten()))))
                                  for tree in self.PACKAGE_TREE.subtrees())
        self.parents       = dict((node, self.PACKAGE_TREE.parent(node))
                                  for node in self.PACKAGE_TREE.flatten())
        self.hierarchy     = dict((tree.root(), list(reversed(tree.flatten())))
                                  for tree in self.PACKAGE_TREE.subtrees())

        self.environment['PACKAGE'] = self.PACKAGE
        self.environment['NAME'] = self.NAME
        self.environment['VERSION'] = self.VERSION
        self.environment['RELEASE'] = self.RELEASE
        self.environment['COPYRIGHT'] = self.COPYRIGHT
        self.environment['AUTHOR'] = self.AUTHOR
        self.environment['COMPANY'] = self.COMPANY


    def get_prerequisites(self, argv):
        return self.prerequisites, argv

    def additional_env(self, envir):
        return dict(envir.items() + self.environment.items())

    def get_source_files(self, *args):
        return self.source_files

    def get_extra_data_files(self, *args):
        return self.extra_data_files



############################################################

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
