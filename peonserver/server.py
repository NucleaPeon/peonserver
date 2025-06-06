import os
import sys
import argparse
import random
import string
import asyncio
import importlib
import logging
import traceback
import tornado
import tornado.web
from tornado.log import enable_pretty_logging
import sass

from peonserver import app
from peonserver import daemon
from peonserver import HERE
import peonserver.log as plog

NAME = "PeonServer"

PIDPATH = os.path.join(HERE, '..')
PIDNAME = f"{NAME.lower()}.pid"
PID = os.path.join(PIDPATH, PIDNAME)
STATIC_PATH = os.path.join(HERE, "static")
TMPL_PATH = os.path.join(HERE, "html")

COMMON_WATCH_PATHS = [

]


def compile_sass_files(static_path=STATIC_PATH):
    sassdir = os.path.join(static_path, 'sass')
    if not os.path.exists(sassdir):
        sassdir = os.path.join(static_path, 'scss')

    if os.path.exists(sassdir):
        files = os.listdir(sassdir)
        for f in files:
            plog.LOG.info(f"Compiling scss file {f}")
            if f.endswith(".scss"):
                sass.compile(dirname=(sassdir, os.path.join(static_path, "css")))

def get_cookie_key(cookiefile=os.path.join(HERE, "cookie.secret"), keylength=80):
    cookiekey = ""
    if not os.path.exists(cookiefile):
        plog.LOG.warn(f"Cookie secret file not found at {cookiefile}")
        plog.LOG.warn(f"Create {cookiefile} and add in key to ignore this warning")

    else:
        with open(cookiefile, 'r') as cf:
            cookiekey = cf.read()
            if not cookiekey:
                plog.LOG.warn("Cookie secret file is empty")

        if not cookiekey:
            plog.LOG.warn("Cookie secret key is empty, generating a random string instead")
            cookiekey = ''.join(random.choices(string.ascii_letters + string.digits, k=keylength))

    return cookiekey

def find_website(path=os.path.join(HERE, "..", "website")):
    websitekw = {}
    if not os.path.exists(path):
        plog.LOG.info(f"Optional user content website path `{os.path.normpath(path)}` does not exist.")
        plog.LOG.info("Use `create-website` script to generate a templated website structure")
        return websitekw

    plog.LOG.info("Found user website, adding to path.")
    sys.path.insert(0, path)
    try:
        import website.globals
        #LEFT OFF FIXME: If attrs not found, ignore but warn unless critical
        plog.LOG.info(f"Found website <{website.globals.WEBSITE}>")
        websitekw['WATCH_PATHS'] = []
        for wp in website.globals.WATCH_PATHS:
            found = os.path.exists(wp)
            plog.LOG.debug(f"\t\t: {'Ignoring missing' if not found else 'Found'} watch path {wp}")
            if found:
                websitekw['WATCH_PATHS'].append(wp)

        websitekw['STATIC_PATH'] = website.globals.STATIC_PATH
        plog.LOG.debug(f"\t:: STATIC_PATH found {websitekw['STATIC_PATH']}")
        websitekw['WEBSITE'] = website.globals.WEBSITE
    except ImportError as iE:
        plog.LOG.error(str(iE))
        plog.LOG.error(traceback.format_exc())
    except AttributeError as aE:
        plog.LOG.error(str(aE))


    return websitekw

def make_app(**kwargs):
    autoreload = kwargs.get("autoreload", kwargs.get("debug", False) )
    plog.LOG.setLevel(logging.DEBUG if kwargs.get("debug") else logging.INFO)
    userwebsite = find_website()
    settings = {
        "static_path": userwebsite.get("STATIC_PATH") or STATIC_PATH,
        "cookie_secret": get_cookie_key(),
        "login_url": "/admin",
        "xsrf_cookies": True,
        "WEBSITE": "Default PeonServer Webpage",
    }

    settings.update(userwebsite)
    COMMON_WATCH_PATHS.extend([
        os.path.join(settings['static_path'], 'index.html'),
        TMPL_PATH,
        os.path.join(settings['static_path'], 'scss'),
        os.path.join(settings['static_path'], 'js'),
        os.path.join(settings['static_path'], 'css')
    ])
    COMMON_WATCH_PATHS.extend(userwebsite.get("WATCH_PATHS", []))

    if autoreload:
        # Remove duplicates
        for _dir in set(COMMON_WATCH_PATHS):
            plog.LOG.debug(f"Watching in directory path {_dir}")

            if not os.path.isfile(_dir):
                files = os.listdir(_dir)

            else:
                files = [_dir]

            for f in files:
                if f.startswith("."):
                    continue
                plog.LOG.info(f"Watching file {f}")
                tornado.autoreload.watch(os.path.join(settings['static_path'], _dir, f))

    # compile sass
    compile_sass_files(settings['static_path'])

    return tornado.web.Application([
            (r"/", app.MainHandler),
            (r"/templ", app.TemplateTestHandler),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": settings['static_path']}),
        ],
        template_path=TMPL_PATH,
        debug=kwargs.get("debug", False),
        autoreload=autoreload,
        **settings
    )

class ServerDaemon(daemon.Daemon):

    async def run(self):
        self.log.info(f"Running {NAME}")
        try:
            app = make_app(debug=self.debug)
            plog.LOG.info(f"App created, debug mode {self.debug}")
            app.listen(self.port)
            asyncio.run(await asyncio.Event().wait())
        except Exception as E:
            plog.LOG.error(str(E))
            plog.LOG.error(traceback.format_exc())

async def run_tornado(debug=True, port=8085):
    try:
        app = make_app(debug=debug)
        plog.LOG.info(f"App created, debug mode {'enabled' if debug else 'disabled'}")
        app.listen(port)
        asyncio.run(await asyncio.Event().wait())
    except Exception as E:
        plog.LOG.error(str(E))
        plog.LOG.error(traceback.format_exc())

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
    enable_pretty_logging()
    if args.no_daemon:
        plog.set_logger(name=NAME)
        plog.LOG.info(f"Setting logfile to use stdout")
        asyncio.run(run_tornado())
    else:
        if args.logfile:
            plog.set_logger(args.logfile, name=NAME)
            plog.LOG.info(f"Setting logfile to {args.logfile}")
        else:
            plog.set_logger(name=NAME)
            plog.LOG.info(f"Setting logfile to use stdout")
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

