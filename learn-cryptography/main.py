
import webapp2
import os
import jinja2

import model
import decrypt
from google.appengine.ext import ndb
from google.appengine.api import users
import string

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


class BaseTemplateHandler(webapp2.RequestHandler):
    """Wrapper around RequestHandler to support common operations.
    
    Handles user sign in and sign out operations, including filling in the base
    template (base.html) values like the username, current signed in state etc.

    A few class-level variables are used to set per-page constants.
    """
    # Name of the template file e.g. index.html
    TEMPLATE = None
    # Set to true to redirect un-signed-in users to the sign in page.
    REQUIRE_SIGN_IN = False

    def isRequireSignIn(self):
        """Whether to redirect the user to sign in or not.

        Override this function to have more fine-grain control for whether to
        redirect or not.
        """
        return self.REQUIRE_SIGN_IN

    def fillValues(self, values):
        """Fills in page-specific template information into the given dict."""
        pass

    def getUserTemplateInfo(self):
        """Returns a dict with either user object for signed in user and sign in/out links."""
        user = users.get_current_user()
        values = {}
        values['user'] = user
        values["signin_link"] = users.create_login_url(self.request.uri)
        values["signout_link"] = users.create_logout_url("/")
        return values

    def get(self):
        """Serve http get method."""
        if self.isRequireSignIn():
            user = users.get_current_user()
            if not user:
                # Redirect to sign in page
                self.redirect(users.create_login_url(self.request.uri))
                return
        values = self.getUserTemplateInfo()
        self.fillValues(values)
        template = jinja_environment.get_template(self.TEMPLATE)
        self.response.out.write(template.render(values))


class MainHandler(BaseTemplateHandler):
    """Handler for landing/home page."""
    TEMPLATE = 'index.html'

    def fillValues(self, values):
        level_seq = ndb.Key(model.LevelSequence, model.LEVEL_LIST).get()
        if level_seq and level_seq.levels and len(level_seq.levels) > 1:
            values['levels'] = level_seq
            values['start_id'] = level_seq.levels[0].urlsafe()
        else:
            values['resetdb'] = True



class LevelHandler(BaseTemplateHandler):
    """Hanlder for the main level page.

    Each level contains some cipher text to decrypt and whatever analysis and
    decryptor tools which the user has currently unlocked.
    """
    TEMPLATE = 'level.html'

    def fillValues(self, values):
        urlstring = self.request.get('level')
        level_key = ndb.Key(urlsafe=urlstring)
        level = level_key.get()
        text = level.text.get()
        values['level'] = level
        values['text'] = text
        values['alphabet'] = string.lowercase
        values['next_level'] = self.getNextLevel(level.key)

    def getNextLevel(current):
        """Given a level id, look up the next level in the sequence."""
        level_seq = ndb.Key(model.LevelSequence, model.LEVEL_LIST).get()
        l = level_seq.levels.index(current) + 1
        if l >= len(level_seq.levels):
            return None
        return level_seq.levels[l].urlsafe()

class ProgressHandler(BaseTemplateHandler):
    """Handler for the progress page showing a user's completed levels."""
    TEMPLATE = 'progress.html'
    REQUIRE_SIGN_IN = True

    def fillValues(self, values):
        pass

class AnalysisPaneHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('analysis.html')
        self.response.out.write(template.render({}))

class TextsPaneHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('texts.html')
        self.response.out.write(template.render({}))

class DecryptorsPaneHandler(webapp2.RequestHandler):
    def get(self):
        template = jinja_environment.get_template('decryptors.html')
        self.response.out.write(template.render({}))

class DecryptHandler(webapp2.RequestHandler):
    def get(self):
        self.response.out.write("GET was called")

    def post(self):
        rotate = self.request.get('rotate')
        self.response.out.write("POST was called %s " % rotate)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/level', LevelHandler),
    ('/analysis', AnalysisPaneHandler),
    ('/texts', TextsPaneHandler),
    ('/decryptors', DecryptorsPaneHandler),
    ('/decrypt', decrypt.DecryptHandler),
    ('/progress', ProgressHandler),
], debug=True)
