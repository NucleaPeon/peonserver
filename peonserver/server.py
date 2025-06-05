import os
import sys
import argparse
import random
import string
import asyncio
import tornado
import tornado.web
from tornado.log import enable_pretty_logging
import sass

from peonserver import app
from peonserver import daemon
from peonserver import HERE
from peonserver import logging

NAME = "PeonServer"

PIDPATH = os.path.join(HERE, '..')
PIDNAME = f"{NAME.lower()}.pid"
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

def get_cookie_key(cookiefile=os.path.join(HERE, "cookie.secret"), keylength=80):
    cookiekey = ""
    if not os.path.exists(cookiefile):
        logging.LOG.warn(f"Cookie secret file not found at {cookiefile}")
        logging.LOG.warn(f"Create {cookiefile} and add in key to ignore this warning")

    else:
        with open(cookiefile, 'r') as cf:
            cookiekey = cf.read()
            if not cookiekey:
                logging.LOG.warn("Cookie secret file is empty")

        if not cookiekey:
            logging.LOG.warn("Cookie secret key is empty, generating a random string instead")
            cookiekey = ''.join(random.choices(string.ascii_letters + string.digits, k=keylength))

    return cookiekey


def make_app(**kwargs):
    enable_pretty_logging()
    autoreload = kwargs.get("autoreload", kwargs.get("debug", False) )
    settings = {
        "static_path": STATIC_PATH,
        "cookie_secret": get_cookie_key(),
        "login_url": "/admin",
        "xsrf_cookies": True,
    }
    if autoreload:
        for _dir in [os.path.join(settings['static_path'], 'scss'), os.path.join(settings['static_path'], 'js'),
                     os.path.join(settings['static_path'], 'css')]:
            files = os.listdir(_dir)
            for f in files:
                if f.startswith("."):
                    continue
                logging.LOG.info(f"Watching file {f}")
                tornado.autoreload.watch(os.path.join(settings['static_path'], _dir, f))

        tornado.autoreload.watch(os.path.join(settings['static_path'], 'index.html'))
    # compile sass
    compile_sass_files(settings['static_path'])

    return tornado.web.Application([
            # Tab names/router for website
            (r"/", app.MainHandler),
            #
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": settings['static_path']}),
        ],
        debug=kwargs.get("debug", False),
        autoreload=autoreload,
        **settings
    )

class ServerDaemon(daemon.Daemon):

    async def run(self):
        self.log.info(f"Running {NAME}")
        try:
            app = make_app(debug=self.debug)
            logging.LOG.info(f"App created, debug mode {self.debug}")
            app.listen(self.port)
            asyncio.run(await asyncio.Event().wait())
        except Exception as E:
            logging.LOG.error(str(E))

async def run_tornado(debug=True, port=8085):
    try:
        app = make_app(debug=debug)
        logging.LOG.info(f"App created, debug mode {debug}")
        app.listen(port)
        asyncio.run(await asyncio.Event().wait())
    except Exception as E:
        logging.LOG.error(str(E))

def main():
    parser = argparse.ArgumentParser(prog=f"{NAME.lower()}", description=f"{NAME} webserver host")
    parser.add_argument("--port", default=8085, help="Port to run on")
    parser.add_argument("--logfile", default=os.path.join(HERE, '..', f"{__name__}.log"),
                        help="Log file to write to")
    parser.add_argument("--pid-path", default=PIDPATH, help="Directory for pid files")
    parser.add_argument("--pid-name", default=PIDNAME, help="Name of the server pid file")
    parser.add_argument("--silent", default=False, help="Daemon should be silent")
    parser.add_argument("--debug", action="store_true", default=False, help="Enable debugging logs and autoreloading")
    parser.add_argument("--no-daemon", default=False, action="store_true",
                        help="Use the tornado event loop for running the website (useful for debugging)")
    subparsers = parser.add_subparsers(help="daemon actions", dest="action")
    subparsers.required = False
    parser_start = subparsers.add_parser('start', help=f"Start the {NAME.lower()} daemon")
    parser_stop = subparsers.add_parser('stop', help=f"Stop the {NAME.lower()} daemon")
    parser_restart = subparsers.add_parser('restart', help=f"Restart the {NAME.lower()} daemon")
    parser_status = subparsers.add_parser('status', help=f"Print out {NAME.lower()} daemon status")

    args = parser.parse_args()
    if args.no_daemon:
        asyncio.run(run_tornado())
    else:
        daemon = ServerDaemon(
            pidname=args.pid_name, pidpath=args.pid_path, silent=args.silent,
            logfile=args.logfile, port=args.port, debug=args.debug)

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

