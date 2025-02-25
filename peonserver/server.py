import os
import sys
import argparse
import asyncio
import tornado
import tornado.web
from tornado.log import enable_pretty_logging
import sass

from peonserver import app
from peonserver import daemon
from peonserver import HERE
from peonserver import logging
# from wpcwebsite import db as database

PIDPATH = os.path.join(HERE, '..')
PIDNAME = "peonserver.pid"
PID = os.path.join(PIDPATH, PIDNAME)
STATIC_PATH = os.path.join(HERE, "static")

def compile_sass_files(static_path=STATIC_PATH):
    sassdir = os.path.join(static_path, 'sass')
    if os.path.exists(sassdir):
        files = os.listdir(sassdir)
        for f in files:
            logging.LOG.info(f"Compiling scss file {f}")
            if f.endswith(".scss"):
                sass.compile(dirname=(sassdir, os.path.join(static_path, "css")))

def make_app(**kwargs):
    enable_pretty_logging()
    autoreload = kwargs.get("autoreload", kwargs.get("debug", False) )
    settings = {
        "static_path": STATIC_PATH,
        "cookie_secret": "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e",
        "login_url": "/admin",
        "xsrf_cookies": True,
    }
    if autoreload:
        for _dir in [os.path.join(settings['static_path'], 'scss'), os.path.join(settings['static_path'], 'js'),
                     os.path.join(settings['static_path'], 'css')]:
            files = os.listdir(_dir)
            for f in files:
                logging.LOG.info(f"Watching file {f}")
                tornado.autoreload.watch(os.path.join(settings['static_path'], _dir, f))

        tornado.autoreload.watch(os.path.join(settings['static_path'], 'index.html'))
    # compile sass
    compile_sass_files(settings['static_path'])

    return tornado.web.Application([
            # Tab names/router for website
            (r"/", app.MainHandler),
            #
            # (r"/logout", app.LogoutHandler),
            # (r"/admin", app.AdminLoginHandler),
            # (r"/admindashboard", app.AdminHandler),
            # API routes
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": settings['static_path']}),
        ],
        debug=kwargs.get("debug", False),
        autoreload=autoreload,
        **settings
    )

class ServerDaemon(daemon.Daemon):

    async def run(self):
        self.log.info("Running PeonServer")
        # await database.initialize_database()
        # logging.LOG.info("Initialized DBs.")
        try:
            app = make_app(debug=self.debug)
            logging.LOG.info(f"App created, debug mode {self.debug}")
            app.listen(self.port)
            asyncio.run(await asyncio.Event().wait())
        except Exception as E:
            logging.LOG.error(str(E))

async def run_tornado(debug=True, port=8085):
    # await database.initialize_database()
    # logging.LOG.info("Initialized DBs.")
    try:
        app = make_app(debug=debug)
        logging.LOG.info(f"App created, debug mode {debug}")
        app.listen(port)
        asyncio.run(await asyncio.Event().wait())
    except Exception as E:
        logging.LOG.error(str(E))

def main():
    """This main method will run the daemon to host the wpcwebsite if not running,
    otherwise it will stop the running wpcwebsite.

    Basically you run wpcserver command to start, then again to stop.
    """
    parser = argparse.ArgumentParser(prog="peonserver", description="PeonServer webserver host")
    parser.add_argument("--port", default=8085, help="Port to run on")
    parser.add_argument("--logfile", default=os.path.join(HERE, '..', f"{__name__}.log"),
                        help="Log file to write to")
    parser.add_argument("--pid-path", default=PIDPATH, help="Directory for pid files")
    parser.add_argument("--pid-name", default=PIDNAME, help="Name of the server pid file")
    parser.add_argument("--silent", default=False, help="Daemon should be silent")
    parser.add_argument("--debug", action="store_true", default=False, help="Enable debugging logs")
    parser.add_argument("--no-daemon", default=False, action="store_true",
                        help="Use the tornado event loop for running the website (useful for debugging)")
    subparsers = parser.add_subparsers(help="daemon actions", dest="action")
    subparsers.required = False
    parser_start = subparsers.add_parser('start', help="Start the wpcwebsite daemon")
    parser_stop = subparsers.add_parser('stop', help="Stop the wpcwebsite daemon")
    parser_restart = subparsers.add_parser('restart', help="Restart the wpcwebsite daemon")
    parser_status = subparsers.add_parser('status', help="Print out server status")

    args = parser.parse_args()
    #logging.set_logger(logfile=args.logfile)
    if args.no_daemon:
        asyncio.run(run_tornado())
    else:
        daemon = ServerDaemon(
            pidname=args.pid_name, pidpath=args.pid_path, silent=args.silent, logfile=args.logfile, port=args.port, debug=args.debug)

        if args.action == "start":
            asyncio.run(daemon.start())

        elif args.action == "stop":
            asyncio.run(daemon.stop())

        elif args.action == "restart":
            asyncio.run(daemon.restart())

        elif args.action == "status":
            asyncio.run(daemon.status())

if __name__ == "__main__":
    main()

