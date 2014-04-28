
import os
from sysdevel.distutils.fetching import fetch
from sysdevel.distutils.configuration import file_config
from sysdevel.distutils import options

class configuration(file_config):
    """
    Fetch THREE
    """
    def __init__(self):
        website = 'https://raw.github.com/mrdoob/three.js/master/'
        file_config.__init__(self, 'three.min.js',
                             os.path.join(options.target_build_dir,
                                          options.javascript_dir),
                             website, debug=False)
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


    def download(self, environ, version, strict=False):
        for t in self.targets[:2]:
            fetch(self.website + 'build/', t, t)
        for t in self.targets[2:]:
            fetch(self.website + 'examples/js/' + t[0], t[1], t[1])
        return ''
