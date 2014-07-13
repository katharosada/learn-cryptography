
import webapp2
import logging
import json

import model
import decrypt
import user_tracker
from google.appengine.ext import ndb
from google.appengine.api import users


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
      level_seq = ndb.Key(model.LevelSequence, model.LEVEL_LIST).get()
      next_level = level_seq.levels[0].urlsafe()
      if user:
        signed_in = True
        name = user.nickname()
      out = {
          "is_signed_in":signed_in,
          "name": name,
          "sign_out_link": users.create_logout_url("/"),
          "sign_in_link": users.create_login_url("/"),
          # TODO: If the user is signed in, this should be the level they are up to.
          "next_level_key": next_level,
      }
      self.response.out.write(json.dumps(out))


class LevelDataHandler(BaseHandler):
    def get(self):
        self.request.get('level')
        urlstring = self.request.get('level')
        level_key = ndb.Key(urlsafe=urlstring)
        level = level_key.get()
        text = level.text.get()

        level_sequence = level_key.parent().get()
        values = {
            'key': level_key.urlsafe(),
            'name': level_sequence.name,
            # Slow but probably not slow enough to warrant caring:
            'place_in_sequence': level_sequence.levels.index(level_key) + 1,
            'max_levels_in_sequence': len(level_sequence.levels)}
        values['text'] = {'key': text.key.urlsafe(), 'encrypted': text.encrypted, 'cleartext': ''}
        values['next_level'] = self.getNextLevel(level.key)
        self.response.out.write(json.dumps(values))

    def getNextLevel(self, current):
        """Given a level id, look up the next level in the sequence."""
        level_seq = current.parent().get()
        l = level_seq.levels.index(current) + 1
        if l >= len(level_seq.levels):
            return None
        return level_seq.levels[l].urlsafe()


class ProgressDataHandler(BaseHandler):
    # TODO: Fix this it's actually useless here, it's never checked.
    # It should be replaced with a function decorator
    REQUIRE_SIGN_IN = True

    def get(self):
        user_tracker = self.getUserTracker()
        level_sequence_data = user_tracker.getLevelSequencesData()
        self.response.out.write(json.dumps(level_sequence_data))


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


app = webapp2.WSGIApplication([
    ('/user_data', UserDataHandler),
    ('/level_data', LevelDataHandler),
    ('/decrypt_data', DecryptDataHandler),
    ('/progress_data', ProgressDataHandler),
], debug=True)
