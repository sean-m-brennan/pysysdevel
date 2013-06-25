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


