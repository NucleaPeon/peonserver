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
    settings = {
        "static_path": STATIC_PATH,
        "cookie_secret": "1be9381b9b12698d307a84684b275225908667ed4cff4d2ccfc19bbf9ed7a2744afcff185397b03a4b2467cc7d2e3fb87fec0b9b412a5fc1bc6ff7d45f9c3200",
        "login_url": "/admin",
        "xsrf_cookies": True,
    }
    # tornado.autoreload.watch(os.path.join(settings['static_path'], 'css', 'wpc.css'))
    # tornado.autoreload.watch(os.path.join(settings['static_path'], 'sass', 'wpc.scss'))
    # tornado.autoreload.watch(os.path.join(settings['static_path'], 'js', 'wpc.js'))
    tornado.autoreload.watch(os.path.join(settings['static_path'], 'index.html'))
    # compile sass
    compile_sass_files(settings['static_path'])

    logging.LOG.info("Autoreloading is set to {}".format(kwargs.get("autoreload", kwargs.get("debug", False) )))

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
        autoreload=kwargs.get("autoreload", kwargs.get("debug", False) ),
        **settings
    )

class WPCDaemon(daemon.Daemon):

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
        daemon = WPCDaemon(
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

