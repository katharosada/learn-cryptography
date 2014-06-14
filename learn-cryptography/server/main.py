
import webapp2
import os
import jinja2
import logging
import json

import model
import decrypt
import user_tracker
from google.appengine.ext import ndb
from google.appengine.api import users
import string

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


class BaseHandler(webapp2.RequestHandler):
    """Base class for any handler that might want to use user info."""

    # Set to true to redirect un-signed-in users to the sign in page.
    REQUIRE_SIGN_IN = False

    def isRequireSignIn(self):
        """Whether to redirect the user to sign in or not.

        Override this function to have more fine-grain control for whether to
        redirect or not.
        """
        return self.REQUIRE_SIGN_IN

    def getUserTracker(self):
        """Pulls user information from the db."""
        return user_tracker.UserTracker(users.get_current_user())

class UserDataHandler(BaseHandler):
    def get(self):
      signed_in = False
      user = users.get_current_user()
      name = ""
      if user:
        signed_in = True
        name = user.nickname()
      out = {
          "is_signed_in":signed_in,
          "name": name,
          "sign_out_link": users.create_logout_url("/"),
          "sign_in_link": users.create_login_url("/"),
      }
      self.response.out.write(json.dumps(out))


class BaseTemplateHandler(BaseHandler):
    """Wrapper around RequestHandler to support common operations.
    
    Handles user sign in and sign out operations, including filling in the base
    template (base.html) values like the username, current signed in state etc.

    A few class-level variables are used to set per-page constants.
    """
    # Name of the template file e.g. index.html
    TEMPLATE = None

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

    if os.environ['OVERRIDE_ROOT_TEMPLATE'].lower() != "none":
      TEMPLATE = os.environ['OVERRIDE_ROOT_TEMPLATE']
      logging.info("Using experimental UI  " + repr(TEMPLATE))
    else:
      TEMPLATE = 'index.html'

    def fillValues(self, values):
        level_seq = ndb.Key(model.LevelSequence, model.LEVEL_LIST).get()
        if level_seq and level_seq.levels and len(level_seq.levels) > 1:
            values['levels'] = level_seq
            values['start_id'] = level_seq.levels[0].urlsafe()
        else:
            values['resetdb'] = True

class LevelDataHandler(BaseHandler):
    def get(self):
        self.request.get('level')
        urlstring = self.request.get('level')
        level_key = ndb.Key(urlsafe=urlstring)
        level = level_key.get()
        text = level.text.get()
        values = {'key': level_key.urlsafe(), 'name': level.name}
        values['text'] = {'key': text.key.urlsafe(), 'encrypted': text.encrypted, 'cleartext': ''}
        values['next_level'] = self.getNextLevel(level.key)
        self.response.out.write(json.dumps(values))

    def getNextLevel(self, current):
        """Given a level id, look up the next level in the sequence."""
        level_seq = ndb.Key(model.LevelSequence, model.LEVEL_LIST).get()
        l = level_seq.levels.index(current) + 1
        if l >= len(level_seq.levels):
            return None
        return level_seq.levels[l].urlsafe()


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

    def getNextLevel(self, current):
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
        userTracker = self.getUserTracker()
        values['levels_completed'] = userTracker.getLevelList()

class ProgressDataHandler(BaseHandler):
    # TODO: Fix this it's actually useless here, it's never checked.
    # It should be replaced with a function decorator
    REQUIRE_SIGN_IN = True

    def get(self):
        userTracker = self.getUserTracker()
        levels = [
            {'key': level.key.urlsafe(),
             'name': level.name,
             'status': status} for level,status in userTracker.getLevelList()]
        self.response.out.write(json.dumps(levels))

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

class DecryptDataHandler(BaseHandler):
    def post(self):
        payload = self.request.body
        data = json.loads(payload)
        text = ndb.Key(urlsafe=data['text_key']).get()
        level_key = ndb.Key(urlsafe=data['level_key'])
        # TODO verify input (text must exist, decryptor valid etc.)
        
        decrypted = decrypt.decrypt(text.encrypted, data['decryptor']);
        win = decrypt.check_result(text, decrypted)
        self.response.out.write(
                json.dumps({'win':win, 'text':decrypted}))
        user = users.get_current_user()
        if user and win:
            # if the user is signed in, record they passed this level
            self.getUserTracker().recordWin(level_key)


class DecryptHandler(BaseHandler):
    def post(self):
        text_key = self.request.get('text')
        level_key = self.request.get('level')
        logging.info(
                'Decrypting text key: %s, with decryption algorithm: %s' 
                % (text_key, self.request.get('decryptor')))
        text = ndb.Key(model.Text, text_key).get()
        if self.request.get('decryptor') == 'rotate':
            decrypted = decrypt.rotate(text.encrypted, self.request)
        else:
            decrypted = decrypt.translate(text.encrypted, self.request)
        win = decrypt.check_result(text, decrypted)
        self.response.out.write(
                json.dumps({'win':win, 'text':decrypted}))
        user = users.get_current_user()
        if user and win:
            # if the user is signed in, record they passed this level
            level_key = ndb.Key(model.Level, level_key)
            self.getUserTracker().recordWin(level_key)


app = webapp2.WSGIApplication([
    ('/old_index', MainHandler),
    ('/user_data', UserDataHandler),
    ('/level', LevelHandler),
    ('/level_data', LevelDataHandler),
    ('/decrypt_data', DecryptDataHandler),
    ('/analysis', AnalysisPaneHandler),
    ('/texts', TextsPaneHandler),
    ('/decryptors', DecryptorsPaneHandler),
    ('/decrypt', DecryptHandler),
    ('/progress', ProgressHandler),
    ('/progress_data', ProgressDataHandler),
], debug=True)
