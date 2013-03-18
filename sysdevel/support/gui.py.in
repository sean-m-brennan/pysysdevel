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

import sys

SPLASH_DURATION        = 1000  ## in milliseconds


class GUI(object):
    def __init__(self, impl_mod, parent):
        self.app = parent
        self.implementation = impl_mod

    def Run(self):
        raise NotImplementedError

    def onExit(self):
        raise NotImplementedError

    def onFatal(self):
        self.app.log.info("Fatal exception encountered. Exiting.")
        sys.exit(1)

    def onError(self, txt):
        self.app.log.error(txt)

    def onWarning(self, txt):
        self.app.log.warning(txt)

    def onInfo(self, txt):
        self.app.log.info(txt)
            
    def onDebug(self, txt):
        self.app.log.debug(txt)



##############################
## function wrapper to add class methods at runtime

class transplant(object):
    def __init__(self, method, host, method_name=None):
        self.host = host
        self.method = method
        setattr(host, method_name or method.__name__, self)

    def __call__(self, *args, **kwargs):
        nargs = [self.host]
        nargs.extend(args)
        return apply(self.method, nargs, kwargs)


