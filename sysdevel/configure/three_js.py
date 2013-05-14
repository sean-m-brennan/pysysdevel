
import os
import shutil

from sysdevel.util import *
from sysdevel.configuration import js_config

class configuration(js_config):
    """
    Fetch THREE
    """
    def __init__(self):
        js_config.__init__(self, debug=False)


    def install(self, environ, version, locally=True):
        website = 'https://raw.github.com/mrdoob/three.js/master/'
        js_file = 'three.min.js'
        js_dir = os.path.join(target_build_dir, javascript_dir)
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        if not os.path.exists(os.path.join(js_dir, js_file)):
            fetch(website + 'build/', js_file, js_file)
            shutil.copy(os.path.join(download_dir, js_file), js_dir)

        for js_tpl in [('', 'Detector.js'),
                       ('shaders/', 'FXAAShader.js'),
                       ('shaders/', 'CopyShader.js'),
                       ('shaders/', 'ConvolutionShader.js'),
                       ('postprocessing/', 'EffectComposer.js'),
                       ('postprocessing/', 'MaskPass.js'),
                       ('postprocessing/', 'RenderPass.js'),
                       ('postprocessing/', 'ShaderPass.js'),
                       ('postprocessing/', 'BloomPass.js'),
                       ## plenty more that could be added here
                       ]:
            js_subdir = os.path.join(js_dir, js_tpl[0])
            js_file = js_tpl[1]
            if not os.path.exists(js_subdir):
                os.makedirs(js_subdir)
            if not os.path.exists(os.path.join(js_subdir, js_file)):
                fetch(website + 'examples/js/' + js_tpl[0], js_file, js_file)
                shutil.copy(os.path.join(download_dir, js_file), js_subdir)
