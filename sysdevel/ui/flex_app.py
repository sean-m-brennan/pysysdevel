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

class __OneTimeCustomException(Exception):
    pass


try:
    try:
        import pyjd
        if not pyjd.is_desktop:
            raise __OneTimeCustomException('Compiling with pyjs.')
    except ImportError:
        pass

    ## WxPython
    # FIXME wx ui objects

    from datetime.datetime import strptime
    from flex_ui import FlexUI, multiline_text
    UserInterface = FlexUI

except __OneTimeCustomException:
    ## Pyjamas
    from pyjamas import Window
    from pyjamas.ui.RootPanel import RootPanel
    from pyjamas.ui.SimplePanel import SimplePanel
    from pyjamas.ui.DecoratorPanel import DecoratedTabPanel
    from pyjamas.ui.DecoratorPanel import DecoratorPanel
    from pyjamas.ui.DecoratorPanel import DecoratorTitledPanel
    from pyjamas.ui.HorizontalPanel import HorizontalPanel
    from pyjamas.ui.VerticalPanel import VerticalPanel
    from pyjamas.ui.HTML import HTML
    from pyjamas.ui.Button import Button
    from pyjamas.ui.RadioButton import RadioButton
    from pyjamas.ui.FlexTable import FlexTable
    from pyjamas.ui.Label import Label
    from pyjamas.ui.Image import Image
    from pyjamas.ui.CheckBox import CheckBox
    from pyjamas.ui.TextArea import TextArea
    from pyjamas.ui.TextBox import TextBox
    from pyjamas.ui.Calendar import DateField
    from pyjamas.ui.Calendar import Calendar
    from pyjamas.ui import HasAlignment

    try:
        import gchartplot as plotter
    except:
        try:
            import raphaelplot as plotter
        except:
            raise ImportError('No plotting modules available')

    from web_ui import WebUI, strptime, multiline_text
    UserInterface = WebUI
