# -*- coding: utf-8 -*-
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
# pylint: disable=W0105
"""
WX-based Graphical User Interface classes that extend the virtual classes
loaded from an XRC file and provide functionality to the GUI layout
"""

import sys
import os
import platform

from . import events
from . import gui

try:
    import warnings
    ## Eliminate "UserWarning: wxPython/wxWidgets release number mismatch"
    warnings.filterwarnings("ignore", category=UserWarning)
    import wx
    import wx.xrc as xrc
    warnings.resetwarnings()
    from . import wx_bmptoggle

    ##############################

    class XrcEvtHandler(wx.EvtHandler):
        """
        Wrapper for wxPython XRC objects
        See http://wiki.wxpython.org/UsingXmlResources
        """
        def __init__(self, other):
            wx.EvtHandler.__init__(self)
            self.this = other.this
            del other.this
            self.thisown = 1
            # pylint: disable=E1101
            if hasattr(self, '_setOORInfo'):
                self._setOORInfo(self)
            if hasattr(self, '_setCallbackInfo'):
                self._setCallbackInfo(self, self.__class__)


    class XrcFrame(wx.Frame, XrcEvtHandler):
        def __init__(self, other):
            XrcEvtHandler.__init__(self, other)
            wx.Frame.__init__(self)


    class XrcDialog(wx.Dialog, XrcEvtHandler):
        def __init__(self, other):
            XrcEvtHandler.__init__(self, other)
            wx.Dialog.__init__(self)


    ##############################
    ##############################

    class WX_GUI(gui.GUI, wx.App):
        def __init__(self, impl_mod, parent, resfile=None, has_log=True):
            gui.GUI.__init__(self)
            self.resource = None
            wx_bmptoggle.BitmapToggleButton.image_dir = self.app.IMAGE_DIR
            self.resource_file = None
            if resfile:
                self.resource_file = resfile + '.xrc'
            self.main_frame = None  ## defined by xrc
            self.helper_frame = None  ## defined by xrc
            wx.App.__init__(self, redirect=(not has_log))


        def OnInit(self):
            self.resource = xrc.XmlResource(self.resource_file)
            self.resource.InsertHandler(
                wx_bmptoggle.BitmapToggleButtonXmlHandler())
            wx.InitAllImageHandlers()
            xpm_icon = os.path.join(self.app.IMAGE_DIR,
                                    self.app.key + '_icon.xpm')
            try:
                __import__(self.implementation)
                impl = sys.modules[self.implementation]
                impl.wxSetup(self, xpm_icon)
            except (ImportError, AttributeError):
                sys.stderr.write('Application ' + self.implementation +
                                 ' not enabled/available\n' +
                                 str(sys.exc_info()[1]) + '\n')
                sys.exit(1)

            image = wx.Image(os.path.join(self.app.IMAGE_DIR,
                                          self.app.key + '_splash.xpm'),
                             wx.BITMAP_TYPE_XPM)
            bitmap = image.ConvertToBitmap()
            wx.SplashScreen(bitmap,
                            wx.SPLASH_CENTRE_ON_PARENT |
                            wx.SPLASH_TIMEOUT, gui.SPLASH_DURATION,
                            self.main_frame, wx.ID_ANY)
            self.main_frame.ShowAll()
            wx.YieldIfNeeded()
            return True

    
        def Beep(self):
            sys.stdout.write("Beep\n")
            if 'windows' in platform.system().lower():
                wx.Bell()
            else:
                sys.stdout.write(chr(7))
                sys.stdout.flush()


        def Run(self):
            self.app.InitGUI()
            self.MainLoop()


        def onExit(self):
            self.main_frame.Close()


        def onHelp(self):
            if self.helper_frame:
                self.helper_frame.ShowAll()


        def onAbout(self, _):
            wx.MessageBox(self.app.name + ' version ' + self.app.version +
                          '\n' + 'Copyright © ' + self.app.copyright,
                          'About ' + self.app.short_name)


        def onNotice(self, txt):
            self.main_frame.statusbarOneLiner(txt)


        def onMessage(self, txt, tpl):
            result = False
            idx = txt.find('|')
            fn = tpl[0]
            general_style = tpl[1]
            specific_style = 0
            if general_style & events.OK:
                specific_style |= wx.OK
            elif general_style & events.CANCEL:
                specific_style |= wx.CANCEL
            elif general_style & events.INFORMATION:
                specific_style |= wx.ICON_INFORMATION
            elif general_style & events.WARNING:
                specific_style |= wx.ICON_EXCLAMATION
            elif general_style & events.QUESTION:
                specific_style |= wx.ICON_QUESTION
            elif general_style & events.ERROR:
                specific_style |= wx.ICON_ERROR
            dialog = wx.MessageDialog(self.main_frame,
                                      txt[idx + 1:], txt[:idx],
                                      style = specific_style)
            if dialog.ShowModal() == wx.ID_OK:
                result = True
            dialog.Destroy()
            if fn != None:
                fn(result)



        def SetText(self, textctl, txt):
            if textctl == None:
                raise Exception("Attempting to write to an unknown control")
            textctl.Clear()
            textctl.AppendText(txt)


        def AppendText(self, textctl, txt):
            if textctl == None:
                raise Exception("Attempting to append to an unknown control")
            textctl.AppendText(txt)


        def Toggle(self, btn):
            state = btn.GetValue()
            btn.SetValue(not state)


        def GetText(self, textctl):
            if textctl == None:
                raise Exception("Attempting to read from an unknown control")
            return textctl.GetValue()


    ## end WX_GUI
    ##############################

except ImportError:
    print(sys.exc_info()[1])
