#!/usr/bin/env python

import sys, os, time, atexit
import logging
from signal import SIGTERM
import asyncio
import typing

LOOP = asyncio.get_event_loop()
DEFAULT_LOG_PATH = '/tmp/peonserver.dameon.log'

"""
TODO:

    [ ] Run as a set user
    [ ] Autoreload functionality
"""

class Daemon():
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method

    We redirect errors to the logfile so user/developer can understand what is
    going wrong when the daemon suddenly stops or the process dies and daemon exits.

    Set stderr to /dev/null (has to be a file object)
    """
    def __init__(self, **kwargs):
        """
        :Parameters:
            - logger: logging.getLogger(name), "daemon " name if unset
            - logfile: path for log file, or DEFAULT_LOG_PATH if unset
            - stdin: path or "/dev/null" if unset
            - stdout: path or logfile if unset
            - stderr: path or logfile if unset
            - silent: default is False
            - pidpath + pidfile: defaults to "/var/run/" + "wpcwebsite.pid"
        """
        self.log = kwargs.get("logger", logging.getLogger('daemon '))
        self.logfile = kwargs.get("logfile", DEFAULT_LOG_PATH)
        self.stdin = kwargs.get("stdin", "/dev/null")
        self.stdout = kwargs.get("stdout", self.logfile)
        self.stderr = kwargs.get("stderr", self.logfile)
        self.silent = kwargs.get("silent", False)
        self.pidfile = os.path.join(kwargs.get("pidpath", f"{__name__}.pid"),
                                    kwargs.get("pidname", "/var/run/"))
        self.debug = kwargs.get("debug", False)
        self.port = kwargs.get("port", 8085)
        logging.basicConfig(level=kwargs.get("loglevel", logging.DEBUG),
            filename=self.logfile,
            filemode='a',
            format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
            datefmt='%H:%M:%S'
        )


    async def daemonize(self):
        """un
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as osE:
            self.log.error(str(osE))
            sys.stderr.write("fork #1 failed: %d (%s)\n" % (osE.errno, osE.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir(os.sep)
        os.setsid()
        os.umask(0)
        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as osE:
            self.log.error(str(osE))
            sys.stderr.write("fork #2 failed: %d (%s)\n" % (osE.errno, osE.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        if self.silent:
            si = open(self.stdin, 'r')
            so = open(self.stdout, 'a+')
            se = open(self.stderr, 'a+')
            os.dup2(si.fileno(), sys.stdin.fileno())
            os.dup2(so.fileno(), sys.stdout.fileno())
            os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        open(self.pidfile,'w+').write("%s\n" % pid)
        return pid

    def delpid(self):
        """On an exit signal/handle, call this function which removes pid file"""
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

    async def status(self):
        print("Daemon Status:", end="")
        if os.path.exists(self.pidfile):
            print(" Running")
        else:
            print(" Not Running")

        print(f"\tLogfile: {os.path.normpath(self.logfile)}")
        print(f"\tPort: {self.port}")

    async def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            sys.stderr.write(message % self.pidfile)
            self.log.error(message % self.pidfile)
            sys.exit(1)

        # Start the daemon
        result = await self.daemonize()
        LOOP.run_until_complete(self.run())

    async def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "pidfile %s does not exist. Daemon not running?\n"
            sys.stderr.write(message % self.pidfile)
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while True:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError as osE:
            err = str(osE)
            self.log.error(str(osE))
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
            else:
                print(str(osE))
                sys.exit(1)

    async def restart(self):
        """
        Restart the daemon
        """
        await self.stop()
        await self.start()


    async def run(self):
        """
        You should override this method when you subclass Daemon. It will be called after the process has been
        daemonized by start() or restart().
        """
        await asyncio.sleep(2)
        self.log.info("default daemon run()")

class TestDaemon(Daemon):

    async def sleep(self):
        while True:
            self.log.info("sleeping")
            await asyncio.sleep(2)
            self.log.info("slept")
            await asyncio.sleep(2)

    async def run(self):
        self.log.info("run")
        await super().run()
        await self.sleep()

PIDPATH = os.getcwd()
PIDNAME = "daemon.pid"
PID = os.path.join(PIDPATH, PIDNAME)

def stop():
    daemon = TestDaemon(pidname=PIDNAME, pidpath=PIDPATH, silent=True)
    asyncio.run(daemon.stop())

def main():
    daemon = TestDaemon(pidname=PIDNAME, pidpath=PIDPATH, silent=True)
    print(daemon)
    asyncio.run(daemon.start() if not os.path.exists(PID) else daemon.restart())

if __name__ == "__main__":
    main()
