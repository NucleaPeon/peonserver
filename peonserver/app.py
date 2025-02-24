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
from wpcwebsite import *
from wpcwebsite import logging
from wpcwebsite import db

LOG = logging.LOG

class MainHandler(tornado.web.RequestHandler):

    async def get(self):
        self.render(os.path.join(HERE, "static/index.html"))
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


class AdminLoginHandler(AuthenticatedHandler):

    async def get(self):
        user = await self.get_current_user()
        if user:
            LOG.info(f"User {user} already authenticated, redirecting")
            self.redirect("/admindashboard")
            return

        else:
            self.render(os.path.join(HERE, "admin.html"))  # Certain pages not available in static/.

    async def post(self):
        # Perform authentication
        username = self.get_argument("username", "")
        password = self.get_argument("password", "")
        LOG.info(f"Admin page login request attempted by {username}")
        LOG.info(str(db.adminlogin))
        LOG.info(f"{username}, {password}")
        if await db.adminlogin(username, password):
            LOG.info(f"db adminlogin successful for {username}")
            await self.set_current_user(f"{username}")
            LOG.info(f"Cookie set for {username}")
            self.redirect("/admindashboard")
            return

        else:
            LOG.info("render the admin page, login attempt failed")
            self.render(os.path.join(HERE, "admin.html"))

class AdminHandler(AuthenticatedHandler):

    @tornado.web.authenticated
    async def get(self):
        LOG.info("Authenticated against AdminHandler, checking current user then rendering page")
        user = await self.get_current_user()
        if not user:
            return

        subs = await db.subscribers()
        self.render(os.path.join(HERE, "admindash.html"), subscribers=subs)

class NewsletterHandler(tornado.web.RequestHandler):

    @tornado.web.authenticated
    async def get(self):
        all_emails = await db.subscribers()
        await self.finish(json.dumps(dict(emails=all_emails)))

    @Validator(NewsletterValidator)
    async def post(self, params={}, error=False):
        # Validated parameters means they are safe to use
        email = params.get("email")
        name  = params.get("name")
        if error:
            self.write(json.dumps(dict(error=error, message=params.get("error", "An error occured"))))
        else:
            is_new = await db.add_to_newsletter(email, name)
            self.write(json.dumps(dict(name=name, email=email, exists=not is_new)))
        await self.finish()


class UnsubscribeParamHandler(tornado.web.RequestHandler):
    """This is called with parameters in the url, similar to NewsletterUnsubscribeHandler's functionality
    """

    async def get(self, email):
        try:
            EmailValidator.to_python({"email": email})
            await db.unsubscribe(email)
            self.write("You have unsubscribed successfully")
        except Invalid as iE:
            self.write(f"There is a problem with the supplied information: {iE}")
        await self.finish()

    async def post(self, email):
        try:
            EmailValidator.to_python({"email": email})
            await db.unsubscribe(email)
            self.write("You have unsubscribed successfully")
        except Invalid as iE:
            self.write(f"There is a problem with the supplied information: {iE}")
        await self.finish()

class NewsletterUnsubscribeHandler(tornado.web.RequestHandler):
    """This is called without parameters in the url
    """

    @Validator(EmailValidator)
    async def post(self, params, error):
        if error:
            self.write(json.dumps(dict(error=error, message=params.get("error", "An error occured"))))
        else:
            email = params.get("email")
            if email:
                await db.unsubscribe(email)
            self.write(json.dumps(dict(email=email)))
        await self.finish()


class CommunityHandler(tornado.web.RequestHandler):

    def get(self):
        return self.redirect("https://www.facebook.com/groups/calligraphyforchristianmoms/", permanent=True)


class InsiderHandler(tornado.web.RequestHandler):

    def get(self):
        return self.redirect("https://wild-plains-calligraphy-2.kit.com/email-list", permanent=True)


class TalkToMeHandler(tornado.web.RequestHandler):

    def get(self):
        return self.redirect("https://forms.gle/nCAr6EJw7hk373N18", permanent=True)

class LogoutHandler(tornado.web.RequestHandler):

    async def get(self):
        self.clear_cookie("user")
        self.redirect("/")

    async def post(self):
        self.clear_cookie("user")
        self.redirect("/")
