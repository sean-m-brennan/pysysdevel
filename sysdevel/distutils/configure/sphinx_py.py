
from ..configuration import py_config

class configuration(py_config):
    """
    Find/install Sphinx documentation tool
    """
    def __init__(self):
        py_config.__init__(self, 'Sphinx', '1.1.3',
                           dependencies=['docutils', 'jinja2', 'pygments',
                                         'roman',],# 'rst2pdf'], #FIXME
                           debug=False)
