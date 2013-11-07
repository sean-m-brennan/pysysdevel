
import os
import shutil

from ..prerequisites import *
from ..configuration import file_config

class configuration(file_config):
    """
    Fetch THREE
    """
    def __init__(self):
        file_config.__init__(self, debug=False)


    def install(self, environ, version, locally=True):
        website = 'https://raw.github.com/mrdoob/three.js/master/'
        js_dir = os.path.join(target_build_dir, javascript_dir)
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        js_file = 'three.min.js'
        if not os.path.exists(os.path.join(js_dir, js_file)):
            fetch(website + 'build/', js_file, js_file)
            shutil.copy(os.path.join(download_dir, js_file), js_dir)
        js_file = 'three.js'
        if not os.path.exists(os.path.join(js_dir, js_file)):
            fetch(website + 'build/', js_file, js_file)
            shutil.copy(os.path.join(download_dir, js_file), js_dir)

        for js_tpl in [('', 'Detector.js'),

                       ('shaders/', 'FXAAShader.js'),
                       ('shaders/', 'CopyShader.js'),
                       ('shaders/', 'ConvolutionShader.js'),

                       ('postprocessing/', 'BloomPass.js'),
                       ('postprocessing/', 'DotScreenPass.js'),
                       ('postprocessing/', 'EffectComposer.js'),
                       ('postprocessing/', 'FilmPass.js'),
                       ('postprocessing/', 'MaskPass.js'),
                       ('postprocessing/', 'RenderPass.js'),
                       ('postprocessing/', 'SavePass.js'),
                       ('postprocessing/', 'ShaderPass.js'),
                       ('postprocessing/', 'TexturePass.js'),

                       ('controls/', 'EditorControls.js'),
                       ('controls/', 'FirstPersonControls.js'),
                       ('controls/', 'FlyControls.js'),
                       ('controls/', 'OrbitControls.js'),
                       ('controls/', 'PathControls.js'),
                       ('controls/', 'PointerLockControls.js'),
                       ('controls/', 'TrackballControls.js'),
                       
                       ## plenty more that could be added here
                       ## effects, renderers, more shaders, etc.
                       ]:
            js_subdir = os.path.join(js_dir, js_tpl[0])
            js_file = js_tpl[1]
            if not os.path.exists(js_subdir):
                os.makedirs(js_subdir)
            if not os.path.exists(os.path.join(js_subdir, js_file)):
                fetch(website + 'examples/js/' + js_tpl[0], js_file, js_file)
                shutil.copy(os.path.join(download_dir, js_file), js_subdir)

        website = 'https://raw.github.com/mrdoob/stats.js/master/'
        js_file = 'stats.min.js'
        if not os.path.exists(os.path.join(js_dir, js_file)):
            fetch(website + 'build/', js_file, js_file)
            shutil.copy(os.path.join(download_dir, js_file), js_dir)
