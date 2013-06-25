"""
BitmapToggleButton
"""

import warnings, os

try:
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning)
    import wx
    from wx.lib.buttons import GenBitmapToggleButton
    import wx.xrc as xrc
    warnings.resetwarnings()


    IMAGE_DIR = 'img'

    def initialize(image_dir):
        """
        MUST be run before using the BitmapToggleButton
        """
        global IMAGE_DIR
        IMAGE_DIR = image_dir


    class BitmapToggleButton(GenBitmapToggleButton):
        """
        Implements the wx.lib.buttons BitmapToggleButton.
        """
        def __init__(self, parent, id=-1, bitmap=wx.NullBitmap,
                     pos=wx.DefaultPosition, size=wx.DefaultSize, style=0,
                     validator=wx.DefaultValidator, name='bitmaptogglebutton'):
            GenBitmapToggleButton.__init__(self, parent, id, bitmap, 
                                           pos, size, style, validator, name)


    class PreBitmapToggleButton(GenBitmapToggleButton):
        """
        Achieves two-stage creation for XRC implementation for the
        BitmapToggleButton.
        """
        def __init__(self):
            b = wx.PrePyControl()
            self.PostCreate(b)

        def Create(self, parent, id=-1, bitmap=wx.NullBitmap, 
                   pos=wx.DefaultPosition, size=wx.DefaultSize,
                   style=wx.BORDER_DEFAULT, validator=wx.DefaultValidator,
                   name='bitmaptogglebutton'):
            cstyle = style
            if cstyle & wx.BORDER_MASK == 0:
                cstyle = wx.BORDER_NONE
            wx.PyControl.Create(self, parent, id,
                                pos, size, style, validator, name)
            self.bmpDisabled = None
            self.bmpFocus = None
            self.bmpSelected = None
            self.SetBitmapLabel(bitmap)
            self.up = True
            self.hasFocus = False
            self.style = style
            if style & wx.BORDER_NONE:
                self.bezelWidth = 0
                self.useFocusInd = False
            else:
                self.bezelWidth = 2
                self.useFocusInd = True
            self.InheritAttributes()
            self.SetInitialSize(size)
            self.InitColours()
            self.Bind(wx.EVT_LEFT_DOWN,   self.OnLeftDown)
            self.Bind(wx.EVT_LEFT_UP,     self.OnLeftUp)
            self.Bind(wx.EVT_LEFT_DCLICK, self.OnLeftDown)
            self.Bind(wx.EVT_MOTION,      self.OnMotion)
            self.Bind(wx.EVT_SET_FOCUS,   self.OnGainFocus)
            self.Bind(wx.EVT_KILL_FOCUS,  self.OnLoseFocus)
            self.Bind(wx.EVT_KEY_DOWN,    self.OnKeyDown)
            self.Bind(wx.EVT_KEY_UP,      self.OnKeyUp)
            self.Bind(wx.EVT_PAINT,       self.OnPaint)
            self.Bind(wx.EVT_SIZE,        self.OnSize)
            self.InitOtherEvents()
        

    class BitmapToggleButtonXmlHandler(xrc.XmlResourceHandler):
        """
        Governs the XRC parsing for the BitmapToggleButton.
        """
        def __init__(self):
            xrc.XmlResourceHandler.__init__(self)
            self.AddStyle("wxBU_LEFT", wx.BU_LEFT)
            self.AddStyle("wxBU_RIGHT", wx.BU_RIGHT)
            self.AddStyle("wxBU_TOP", wx.BU_TOP)
            self.AddStyle("wxBU_BOTTOM", wx.BU_BOTTOM)
            self.AddStyle("wxBU_EXACTFIT", wx.BU_EXACTFIT)
            self.AddWindowStyles()

        def CanHandle(self, node):
            return self.IsOfClass(node, "BitmapToggleButton")

        def DoCreateResource(self):
            button = self.GetInstance()
            if button is None:
                button = PreBitmapToggleButton()
            filename = os.path.join(IMAGE_DIR, self.GetText('bitmap'))
            bmp = None
            if filename != None and filename != '':
                bmp = wx.Bitmap(filename, wx.BITMAP_TYPE_ANY)
            button.Create(self.GetParentAsWindow(), self.GetID(), bmp,
                          self.GetPosition(), self.GetSize(),
                          self.GetStyle("style"), wx.DefaultValidator,
                          self.GetName())
            self.SetupWindow(button)
            return button

except:
    pass
