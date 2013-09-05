
import os
import sys

from sysdevel.util import *
from sysdevel.configuration import py_config

class configuration(py_config):
    """
    Find/install Breathe
    """
    def __init__(self):
        py_config.__init__(self, 'breathe', '1.0.0',
                           dependencies=[('sphinx', '1.0.7'), 'uuid',],
                           debug=False)
        ## NB: will not work (unpatched) with Python 2.4
        if sys.version_info < (2, 6):
            raise Exception('Breathe is not supported ' +
                            'for Python versions < 2.6')

    def install(self, environ, version, locally=True):
        if not self.found:
            website = 'https://pypi.python.org/packages/source/b/breathe/'
            if version is None:
                version = self.version
            if sys.version_info < (2, 6):
                version = '0.7.5'  ## Force version for patching
            src_dir = 'breathe-' + str(version)
            archive = src_dir + '.tar.gz' 
            install_pypkg(src_dir, website, archive, locally=locally,
                          patch=patch)
            if not self.is_installed(environ, version):
                raise Exception('Breathe installation failed.')



def patch(src_path):
    if sys.version_info < (2, 6):
        path = os.path.join(src_path, 'breathe', '__init__.py')
        patch_file(path, '(namespace, name) if namespace else name',
                   '            display_name = "%s::%s" % (namespace, name) if namespace else name',
                   '            if namespace:\n' +
                   '                display_name = "%s::%s" % (namespace, name)\n' +
                   '            else:\n' +
                   '                display_name = name')
        patch_file(path, '(namespace, name) if namespace else name',
                   '        xml_name = "%s::%s" % (namespace, name) if namespace else name',
                   '        if namespace:\n' +
                   '            xml_name = "%s::%s" % (namespace, name)\n' +
                   '        else:\n' +
                   '            xml_name = name')
        path = os.path.join(src_path, 'breathe', 'renderer', 'rst',
                            'doxygen', 'domain.py')
        patch_file(path, 'if data_object.explicit == ',
                   '        explicit = "explicit " if data_object.explicit == "yes" else ""',
                   '        explicit = ""\n' +
                   '        if data_object.explicit == "yes":\n' +
                   '            explicit = "explicit "')
        path = os.path.join(src_path, 'breathe', 'finder',
                            'doxygen', '__init__.py')
        patch_file(path, '(name) if name else AnyMatcher()',
                   '        return NameMatcher(name) if name else AnyMatcher()',
                   '        if name:\n' +
                   '          return NameMatcher(name)\n' +
                   '        return AnyMatcher()')
        patch_file(path, '    def create_ref_matcher_stack(self, class_, ref):',
                   '    def create_ref_matcher_stack(self, class_, ref):',
                   '    def create_ref_matcher_stack(self, class_, ref):\n' +
                   '        compound = AnyMatcher()\n' +
                   '        if class_:\n' +
                   '            compound = ItemMatcher(class_, "class")')
        patch_file(path, 'ItemMatcher(class_, "class") if class_ else AnyMatcher()',
                   '                "compound" : ItemMatcher(class_, "class") if class_ else AnyMatcher(),',
                   '                "compound" : compound,')
