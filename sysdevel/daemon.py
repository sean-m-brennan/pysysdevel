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
Multi-platform service/daemon creator
"""

import sys
import os
import platform

if 'windows' in platform.system().lower():

    try:
        # pylint: disable=F0401
        #import pythoncom
        #import servicemanager
        import win32serviceutil
        import win32service
        import win32event
        import win32api
        import socket

        class Daemon(win32serviceutil.ServiceFramework):
            # pylint: disable=E1101
            """
            A generic Windows service class.
            Usage: subclass the Daemon class and override the run() method
            """
            _svc_name_ = "InvalidService"
            _svc_display_name_ = "Invalid Service"

            def __init__(self, log_file):
                win32serviceutil.ServiceFramework.__init__(self, [self._svc_name_])
                self.stop_event = win32event.CreateEvent(None, 0, 0, None)
                socket.setdefaulttimeout(60)
                self.log = log_file
                self._svc_reg_class_ = None  ## see start()


            def SvcStop(self):
                self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
                self.stop()
                win32event.SetEvent(self.stop_event)
                self.ReportServiceStatus(win32service.SERVICE_STOPPED)


            def SvcDoRun(self):
                self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
                try:
                    self.ReportServiceStatus(win32service.SERVICE_RUNNING)
                    self.run()
                    #win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
                except win32api.error:
                    self.SvcStop()


            def start(self):
                try:
                    module_path = sys.modules[self.__module__].__file__
                except AttributeError:
                    # maybe py2exe went by
                    module_path = sys.executable
                    module_file = os.path.splitext(os.path.abspath(module_path))[0]
                    self._svc_reg_class_ = '%s.%s' % (module_file, self.__name__)
                    try:
                        win32serviceutil.InstallService(self._svc_reg_class_,
                                                        self._svc_name_,
                                                        self._svc_display_name_,
                                                        startType=win32service.SERVICE_AUTO_START
                                                        )
                        print('Install ok')
                        win32serviceutil.StartService(self._svc_name_)
                        print('Start ok')
                    except win32api.error:
                        print(str(sys.exc_info()[1]))


            def force_stop(self):
                try:
                    win32serviceutil.StopService(self._svc_name_)
                    print('Start ok')
                except win32api.error:
                    print(str(sys.exc_info()[1]))
                try:
                    win32serviceutil.RemoveService(self._svc_name_)
                except win32api.error:
                    print(str(sys.exc_info()[1]))


            def sleep(self, sec):
                win32api.Sleep(sec*1000, True)


            def stop(self):
                """
                You should override this method when you subclass Daemon.
                Call force_stop at the end of your overridden method.
                """
                raise NotImplementedError('Daemon is abstract, ' +
                                          'choose a concrete class.')


            def run(self):
                """
                You should override this method when you subclass Daemon.
                """
                raise NotImplementedError('Daemon is abstract, ' +
                                          'choose a concrete class.')

    except:
        raise Exception("Support for Windows daemon not available (win32api).")

else:  ## UNIX assumed

    import signal
    import time
    import atexit
    import tempfile

    class Daemon(object):
        """
	A generic UNIX daemon class.
	Usage: subclass the Daemon class and override the run() method
	"""
        _svc_name_ = "InvalidDaemon"
        _svc_display_name_ = "Invalid Daemon"

        def __init__(self, log_file='/dev/null'):
            self.stdin = '/dev/null'
            self.stdout = log_file
            self.stderr = log_file
            self.pidfile = os.path.join(tempfile.gettempdir(),
                                        self._svc_name_ + '.pid')
            signal.signal(signal.SIGTERM, self._signal_handler)
	

        def _signal_handler(self, *unused):  # pylint: disable=W0613
            ## Must match signal handler signature
            self.stop()

        def _daemonize(self):
            """
            do the UNIX double-fork magic, see Stevens' "Advanced 
            Programming in the UNIX Environment" for details (ISBN 0201563177)
            http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
            """
            try: 
                pid = os.fork() 
                if pid > 0:
                    # exit first parent
                    sys.exit(0) 
            except OSError:
                e = sys.exc_info()[1]
                sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
                sys.exit(1)
	
            # decouple from parent environment
            os.chdir("/") 
            os.setsid() 
            os.umask(0) 
	
            # do second fork
            try: 
                pid = os.fork() 
                if pid > 0:
                    # exit from second parent
                    sys.exit(0) 
            except OSError:
                e = sys.exc_info()[1]
                sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
                sys.exit(1) 
	
            # redirect standard file descriptors
            sys.stdout.flush()
            sys.stderr.flush()
            si = open(self.stdin, 'r')
            so = open(self.stdout, 'a+')
            se = open(self.stderr, 'a+', 0)
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())
	
            # write pidfile
            atexit.register(self._delpid)
            pid = str(os.getpid())
            pf = open(self.pidfile, 'w+')
            pf.write("%s\n" % pid)
            pf.close()
	

        def _delpid(self):
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)


        def start(self):
            """
            Start the daemon
            """
            # Check for a pidfile to see if the daemon already runs
            try:
                pf = open(self.pidfile, 'r')
                pid = int(pf.read().strip())
                pf.close()
            except IOError:
                pid = None
            if pid:
                message = "pidfile %s already exist. Daemon already running?\n"
                sys.stderr.write(message % self.pidfile)
                sys.exit(1)
		
            # Start the daemon
            self._daemonize()
            self.run()


        def force_stop(self):
            # Get the pid from the pidfile
            try:
                pf = open(self.pidfile, 'r')
                pid = int(pf.read().strip())
                pf.close()
            except IOError:
                pid = None
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)
	
            if not pid:
                message = "pidfile %s does not exist. Daemon not running?\n"
                sys.stderr.write(message % self.pidfile)
                ## not an error in a restart
            else:
                ## Try forcibly killing the daemon process	
                try:
                    while True:
                        os.kill(pid, signal.SIGKILL)
                        time.sleep(0.1)
                except OSError:
                    e = sys.exc_info()[1]
                    err = str(e)
                    if err.find("No such process") < 0:
                        sys.stderr.write(err)
                        sys.exit(1)


        def sleep(self, sec):
            time.sleep(sec)


        def stop(self):
            """
            Override this method when subclassing Daemon.
            Call force_stop at the end of the overridden method.
            """
            raise NotImplementedError('Daemon is abstract, ' +
                                      'choose a concrete class.')

        def run(self):
            """
            Override this method when subclassing Daemon.
            """
            raise NotImplementedError('Daemon is abstract, ' +
                                      'choose a concrete class.')



##############################


if __name__ == "__main__":
    import tempfile

    class TestDaemon(Daemon):
        _svc_name_ = "TestDaemon"
        _svc_display_name_ = "Test Daemon"

        def __init__(self):
            super(TestDaemon, self).__init__(self,
                                             os.path.join(tempfile.gettempdir(),
                                                          'TestDaemon.log'))
            self.running = True

        def stop(self):
            self.running = False
            self.sleep(1)
            self.force_stop()

        def run(self):
            idx = 0
            while idx < 10:
                print(self._svc_name_ + " daemon running: " + str(self.running))
                self.sleep(10)
                idx += 1

    TestDaemon().start()
