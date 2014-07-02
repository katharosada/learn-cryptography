import webapp2
import os
import jinja2
import string
import json

import model
import decrypt

from google.appengine.ext import ndb

jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


results = {}

default_levels = []

level_list = None

defaultLevels = ['caesar']

def getOrCreateLevel(level_key):
    level = level_key.get()
    if not level:
        level = model.Level(key=level_key)
    return level


def resetText(text_id, decryptor_id, decryptor_key_json):
    key = ndb.Key(model.Text, text_id)
    text = key.get()
    if not text:
        text = model.Text(key=key)
    text.content = open('texts/%s.txt' % text_id, 'rU').read()
    decryptor = {'id': decryptor_id, 'key':json.loads(decryptor_key_json)}
    text.encrypted = decrypt.decrypt(text.content, decryptor)
    text.put()


def resetLevel(level_id, text_id, unlock_list):
    level_key = ndb.Key(model.Level, level_id)

    level = getOrCreateLevel(level_key)
    level.text = ndb.Key(model.Text, text_id)
    level.unlock_levels = [ndb.Key(model.Level, id) for id in unlock_list]
    key = level.put()
    results[level_id] = level
    return level

def appendToLevelSequence(level_sequence, level_id_list):
    for level_id in level_id_list:
      level_key = ndb.Key(model.Level, level_id)
      if not level_key in level_list.levels:
          level_list.levels.append(level_key)
          level_list.put()


def resetAllTheThings():
    global default_levels
    global level_list

    level_list_key = ndb.Key(model.LevelSequence, model.LEVEL_LIST)
    level_list = level_list_key.get()
    if not level_list:
        # Create level list with level 1
        level_list = model.LevelSequence(key=level_list_key)
        level_list.name = 'default'
        level_list.put()

    # Level 1 - Caesar Cipher
    resetText('caesar1', 'rotate', '{"rotate": "3"}')
    resetLevel('caesar1', 'caesar1', ['caesar2'])

    # Caesar cipher 2 (ROT 13)
    resetText('caesar2', 'rotate', '{"rotate": "13"}')
    resetLevel('caesar2', 'caesar2', ['caesar3'])

    # Caesar cipher 3 (rotate -5)
    resetText('caesar3', 'rotate', '{"rotate": "21"}')
    resetLevel('caesar3', 'caesar3', ['translation1'])

    appendToLevelSequence(level_list, ['caesar1', 'caesar2', 'caesar3'])

    # Translation ciphers sequence
    def alephmap(newaleph):
      result = {}
      for a, b in zip(string.lowercase, newaleph):
        result[a] = b
      return json.dumps(result)

    # Backwards alphabet translation
    resetText('translation1', 'translate', alephmap('zyxwvutsrqponmlkjihgfedcba'))
    resetLevel('translation1', 'translation1', ['translation2'])

    # Translation Cipher 2: Vowels and constonants shifted separately
    resetText('translation2', 'translate', alephmap('ecdfighjoklmnpuqrstvawxyzb'))
    resetLevel('translation2', 'translation2', ['translation3'])

    # Translation Cipher 2: Scrambled alphabet
    resetText('translation3', 'translate', alephmap('kgxmqblwrjnydshzatoeuifpvc'))
    resetLevel('translation3', 'translation3', [])

    appendToLevelSequence(level_list, ['translation1', 'translation2', 'translation3'])


class ResetHandler(webapp2.RequestHandler):
    def get(self):
        resetAllTheThings()

        values = {'results':results, 'levels':default_levels, 'level_list':level_list}

        template = jinja_environment.get_template('reset.html')
        self.response.out.write(template.render(values))

app = webapp2.WSGIApplication([
    ('/resetdata', ResetHandler),
], debug=True)
