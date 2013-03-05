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

## Note web interfaces never see this module

(INVALID, WX, GTK, QT4, QT, FLTK, TK, BE_MAX) = (0, 1, 2, 4, 8, 16, 32, 63)
BE_MIN = WX
TEXT = 2 * (BE_MAX + 1)


Backends = dict({
    'wx'      : WX,
    'wxagg'   : WX,
    'gtk'     : GTK,
    'gtkagg'  : GTK,
    'qt4'     : QT4,
    'qt4agg'  : QT4,
    'qt'      : QT,
    'qtagg'   : QT,
    'fltk'    : FLTK,
    'fltkagg' : FLTK,
    'tk'      : TK,
    'tkagg'   : TK,
    })

BackendNames = dict({
    WX   : 'WXAgg',
    GTK  : 'GTKAgg',
    QT4  : 'QT4Agg',
    QT   : 'QTAgg',
    FLTK : 'FLTKAgg',
    TK   : 'TKAgg',
    TEXT : 'Textual',
    })


## default values
BACKEND        = BE_MIN
HANDLER_OBJECT = object


ENABLE_WX    = @@{WX_ENABLED}   ## requires wxPython
ENABLE_GTK   = @@{GTK_ENABLED}  ## requires PyGTK
ENABLE_QT4   = @@{QT4_ENABLED}  ## requires PyQt4
ENABLE_QT3   = @@{QT3_ENABLED}  ## requires PyQt
ENABLE_FLTK  = @@{FLTK_ENABLED} ## requires pyFLTK
ENABLE_TK    = @@{TK_ENABLED}   ## requires TkInter


def __be_setup__(be):
    import warnings
    if be == WX and ENABLE_WX:
        warnings.filterwarnings("ignore", category=UserWarning)
        import wx, wx.html, wx.xrc
        warnings.resetwarnings()
        return True
    elif be == GTK and ENABLE_GTK:
        warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
        import gtk, gobject, gtkhtml2, gtk.glade
        warnings.resetwarnings()
        return True
    elif be == QT4 and ENABLE_QT4:
        import PyQt4
        return True
    elif be == QT and ENABLE_QT3:
        import qt
        return True
    elif be == FLTK and ENABLE_FLTK:
        import fltk
        return True
    elif be == TK and ENABLE_TK:
        import Tkinter
        return True
    return False


def chooseBackend(preference=None, debug=False):
    global BACKEND
    if preference is None or preference == TEXT:
        BACKEND = TEXT
        return BACKEND

    if type(preference) == type(str()):
        BACKEND = Backends[preference.lower()]
    elif type(preference) == type(int()):
        BACKEND = preference

    tried = 0
    while tried < BE_MAX:
        try:
            if not __be_setup__(BACKEND):
                if debug:
                    sys.stderr.write(BackendNames[BACKEND][:-3] +
                                     ' disabled\n')
                tried |= BACKEND
                BACKEND <<= 1
            else:
                break
        except Exception, e:
            if debug:
                sys.stderr.write(BackendNames[BACKEND][:-3] +
                                 ': ' + str(e) + '\n')
            tried |= BACKEND
            BACKEND <<= 1
        if BACKEND > BE_MAX:
            BACKEND = BE_MIN

    if tried == BE_MAX:
        sys.stderr.write('No GUI backend available; textual only.\n')
        BACKEND = TEXT
    if debug:
        sys.stderr.write('Backend: ' + BackendNames[BACKEND][:-3] + '\n')
    return BACKEND



def UIFactory(app, has_log, pkg=None)
    be = chooseBackend(app.backend, app.debug_level)
    pkg_prefix = ''
    if pkg:
        pkg_prefix = pkg + '.'

    if be == TEXT:
        import txt_gui
        mod_name = pkg_prefix + 'txt_' + app.key
        return txt_gui.TXT_GUI(mod_name, app, app.resource_file, has_log)
    elif be == WX:
        import wx_gui
        mod_name = pkg_prefix + 'wx_' + app.key
        return wx_gui.WX_GUI(mod_name, app, app.resource_file, has_log)
    elif be == GTK:
        import gtk_gui
        mod_name = pkg_prefix + 'gtk_' + app.key
        return gtk_gui.GTK_GUI(mod_name, app, app.resource_file, has_log)
    # TODO: implement other backends
    else:
        raise NotImplementedError
