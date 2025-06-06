import os
import json
import asyncio
import datetime
import tornado
import tornado.web
import tornado.escape

from argparse import Namespace
from formencode import Invalid

# tornado.web.authenticated
from peonserver import *
import peonserver.log as plog

LOG = plog.LOG

class MainHandler(tornado.web.RequestHandler):

    async def get(self):
        self.render(os.path.join(self.settings.get("static_path"), "index.html"),
                    **self.settings)
        # self.static_url("index.html")


class AuthenticatedHandler(tornado.web.RequestHandler):

    async def prepare(self):
        self.current_user = await self.get_current_user()

    async def get_current_user(self):
        return self.get_secure_cookie("user")

    async def set_current_user(self, user):
        user = str(user)
        if user:
            self.set_secure_cookie("user", tornado.escape.json_encode(user))
        else:
            self.clear_cookie("user")

class TemplateTestHandler(tornado.web.RequestHandler):

    async def get(self):
        self.render("test.html", value1="one", value2="two")

#
# class AdminLoginHandler(AuthenticatedHandler):
#
#     async def get(self):
#         # Ignore this for now
#         return self.render(os.path.join(HERE, "static/index.html"))
#
#         user = await self.get_current_user()
#         if user:
#             LOG.info(f"User {user} already authenticated, redirecting")
#             self.redirect("/admindashboard")
#             return
#
#         else:
#             self.render(os.path.join(HERE, "admin.html"))  # Certain pages not available in static/.
#
#     async def post(self):
#         # Perform authentication
#         username = self.get_argument("username", "")
#         password = self.get_argument("password", "")
#         return self.render(os.path.join(HERE, "static/index.html"))
#
#         # if await db.adminlogin(username, password):
#         #     LOG.info(f"db adminlogin successful for {username}")
#         #     await self.set_current_user(f"{username}")
#         #     LOG.info(f"Cookie set for {username}")
#         #     self.redirect("/admindashboard")
#         #     return
#         #
#         # else:
#         #     LOG.info("render the admin page, login attempt failed")
#         #     self.render(os.path.join(HERE, "admin.html"))
#
# class AdminHandler(AuthenticatedHandler):
#
#     @tornado.web.authenticated
#     async def get(self):
#         LOG.info("Authenticated against AdminHandler, checking current user then rendering page")
#         user = await self.get_current_user()
#         if not user:
#             return
#
#         self.render(os.path.join(HERE, "admindash.html"))
#
# class LogoutHandler(tornado.web.RequestHandler):
#
#     async def get(self):
#         self.clear_cookie("user")
#         self.redirect("/")
#
#     async def post(self):
#         self.clear_cookie("user")
#         self.redirect("/")
