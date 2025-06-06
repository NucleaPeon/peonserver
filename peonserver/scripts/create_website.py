#!/usr/bin/env python

import os
import shutil
from peonserver import HERE

GLOBALS_DEFAULT_CODE = """
import os
HERE = os.path.abspath(os.path.dirname(__file__))

WEBSITE = "Custom Website Project"
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
    create_path = os.path.normpath(os.path.join(HERE, "..", "website"))
    os.makedirs(create_path, exist_ok=True)
    static_path = os.path.normpath(os.path.join(create_path, 'static'))
    for subdir in ['css', 'scss', 'js']:
        path = os.path.join(static_path, subdir)
        print(f"\t:: Creating if not exists: {path}")
        os.makedirs(path, exist_ok=True)

    os.makedirs(os.path.join(create_path, 'html'), exist_ok=True)
    os.makedirs(os.path.join(create_path, 'routes'), exist_ok=True)
    initpath = os.path.join(create_path, "__init__.py")
    if not os.path.exists(initpath):
        with open(initpath, 'w') as f:
            f.write("")
            print(":: Writing __init__.py file")

    globalspath = os.path.join(create_path, "globals.py")
    if not os.path.exists(globalspath):
        with open(globalspath, 'w') as f:
            f.write(GLOBALS_DEFAULT_CODE)
            print(":: Writing globals.py file")

    htmlfile = os.path.join(static_path, 'index.html')
    if not os.path.exists(htmlfile):
        shutil.copyfile(os.path.join(HERE, "static", "index.html"), htmlfile)
        print(":: Copied default index.html file to new website")

if __name__ == "__main__":
    main()
