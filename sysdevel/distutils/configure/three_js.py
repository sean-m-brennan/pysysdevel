
import os
import shutil

from ..fetching import fetch
from ..configuration import file_config
from .. import options

class configuration(file_config):
    """
    Fetch THREE
    """
    def __init__(self):
        file_config.__init__(self, 'three.min.js',
                             os.path.join(options.target_build_dir,
                                          options.javascript_dir),
                             debug=False)
        self.targets = ['three.min.js', 'three.js',

                        ('', 'Detector.js'),
                        ('shaders', 'FXAAShader.js'),
                        ('shaders', 'CopyShader.js'),
                        ('shaders', 'ConvolutionShader.js'),

                        ('postprocessing', 'BloomPass.js'),
                        ('postprocessing', 'DotScreenPass.js'),
                        ('postprocessing', 'EffectComposer.js'),
                        ('postprocessing', 'FilmPass.js'),
                        ('postprocessing', 'MaskPass.js'),
                        ('postprocessing', 'RenderPass.js'),
                        ('postprocessing', 'SavePass.js'),
                        ('postprocessing', 'ShaderPass.js'),
                        ('postprocessing', 'TexturePass.js'),

                        ('controls', 'EditorControls.js'),
                        ('controls', 'FirstPersonControls.js'),
                        ('controls', 'FlyControls.js'),
                        ('controls', 'OrbitControls.js'),
                        ('controls', 'PathControls.js'),
                        ('controls', 'PointerLockControls.js'),
                        ('controls', 'TrackballControls.js'),
                        
                        ## plenty more that could be added here
                        ## effects, renderers, more shaders, etc.
                        ]


    def install(self, environ, version, strict=False, locally=True):
        website = 'https://raw.github.com/mrdoob/three.js/master/'
        js_dir = self.target_dir
        if not os.path.exists(js_dir):
            os.makedirs(js_dir)
        for t in self.targets[:2]:
            js_file = t
            if not os.path.exists(os.path.join(js_dir, js_file)):
                fetch(website + 'build/', js_file, js_file)
                shutil.copy(os.path.join(options.download_dir, js_file), js_dir)

        for t in self.targets[2:]:
            js_subdir = os.path.join(js_dir, t[0])
            js_file = t[1]
            if not os.path.exists(js_subdir):
                os.makedirs(js_subdir)
            if not os.path.exists(os.path.join(js_subdir, js_file)):
                fetch(website + 'examples/js/' + t[0], js_file, js_file)
                shutil.copy(os.path.join(options.download_dir, js_file),
                            js_subdir)
