#!/usr/bin/env python

import os
import shutil
import argparse
from peonserver import HERE

def global_default_code(parsed):
    """
    :Parameters:
        - parsed: dict
    """
    return f"""
import os
HERE = os.path.abspath(os.path.dirname(__file__))

WEBSITE = "{parsed['title']}"
STATIC_PATH = os.path.join(HERE, "static")
TMPL_PATH = os.path.join(HERE, "html")
ROUTE_PATH = os.path.join(HERE, "routes")
WATCH_PATHS = [
    os.path.join(STATIC_PATH, "scss"),
    os.path.join(STATIC_PATH, "css"),
    os.path.join(STATIC_PATH, "js"),
    os.path.join(STATIC_PATH, "index.html"),
    TMPL_PATH,
    ROUTE_PATH
]
"""

def main():
    parser = argparse.ArgumentParser(prog="create-website", description="Generates a website template at a specified location")
    parser.add_argument("path", default=os.path.normpath(os.path.join(HERE, "..", "website")), help="Location to write the website data, defaults to the server directory.")
    parser.add_argument("-t", "--title",
                        default="Custom Website Project",
                        help="Window Title of the Webpage")

    args = parser.parse_args()
    path = args.path

    os.makedirs(path, exist_ok=True)
    static_path = os.path.normpath(os.path.join(path, 'static'))
    for subdir in ['css', 'scss', 'js']:
        jspath = os.path.join(static_path, subdir)
        print(f"\t:: Creating if not exists: {jspath}")
        os.makedirs(jspath, exist_ok=True)

    os.makedirs(os.path.join(path, 'html'), exist_ok=True)
    os.makedirs(os.path.join(path, 'routes'), exist_ok=True)
    initpath = os.path.join(path, "__init__.py")
    if not os.path.exists(initpath):
        print("no init.py")
        with open(initpath, 'w') as f:
            f.write("")
            print(":: Writing __init__.py file")

    globalspath = os.path.join(path, "globals.py")
    if not os.path.exists(globalspath):
        print("no globals.py", vars(args))
        with open(globalspath, 'w') as f:
            f.write(global_default_code(vars(args)))
            print(":: Writing globals.py file")

    htmlfile = os.path.join(static_path, 'index.html')
    if not os.path.exists(htmlfile):
        shutil.copyfile(os.path.join(HERE, "static", "index.html"), htmlfile)
        print(":: Copied default index.html file to new website")

if __name__ == "__main__":
    main()
