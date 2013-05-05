
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

def get_user_template_info(current_url):
    """Returns a dict with either user object for signed in user and sign in/out links."""
    user = users.get_current_user()
    values = {}
    values['user'] = user
    values["signin_link"] = users.create_login_url(current_url)
    values["signout_link"] = users.create_logout_url("/")
    return values


class BaseTemplateHandler(webapp2.RequestHandler):
    def getTemplateValues(self):
        values = get_user_template_info(self.request.path_qs)
        return values


class MainHandler(BaseTemplateHandler):
    def get(self):
        values = self.getTemplateValues()
        level_seq = ndb.Key(model.LevelSequence, model.LEVEL_LIST).get()
        if level_seq and level_seq.levels and len(level_seq.levels) > 1:
            values['levels'] = level_seq
            values['start_id'] = level_seq.levels[0].urlsafe()
        else:
            values['resetdb'] = True
        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(values))

def getNextLevel(current):
    level_seq = ndb.Key(model.LevelSequence, model.LEVEL_LIST).get()
    l = level_seq.levels.index(current) + 1
    if l >= len(level_seq.levels):
        return None
    return level_seq.levels[l].urlsafe()


class LevelHandler(BaseTemplateHandler):
    def get(self):
        values = self.getTemplateValues()
        urlstring = self.request.get('level')
        level_key = ndb.Key(urlsafe=urlstring)
        level = level_key.get()
        text = level.text.get()
        values['level'] = level
        values['text'] = text
        values['alphabet'] = string.lowercase
        values['next_level'] = getNextLevel(level.key)
        template = jinja_environment.get_template('level.html')
        self.response.out.write(template.render(values))

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
], debug=True)
