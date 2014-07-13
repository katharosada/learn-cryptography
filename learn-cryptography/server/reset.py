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


def resetStandardDecryptLevel(level_sequence_key, level_id, text_id, unlock_list):
    level_key = ndb.Key(model.LevelSequence, level_sequence_key.id(), model.Level, level_id)

    level = getOrCreateLevel(level_key)
    level.level_type = model.LevelType.STANDARD_DECRYPT
    level.text = ndb.Key(model.Text, text_id)
    level.unlock_levels = [
        ndb.Key(model.LevelSequence, level_sequence_key.id(), model.Level, id) for id in unlock_list]
    key = level.put()
    return level

def appendToLevelSequence(level_sequence, level_id_list):
    for level_id in level_id_list:
      level_key = ndb.Key(model.LevelSequence, level_sequence.key.id(), model.Level, level_id)
      if not level_key in level_sequence.levels:
          level_sequence.levels.append(level_key)
          level_sequence.put()

def resetLevelSequence(level_sequence_id, name, unlock_sequence_ids):
    level_sequence_key = ndb.Key(model.LevelSequence, level_sequence_id)
    level_sequence = level_sequence_key.get()
    if not level_sequence:
        # Create level list with level 1
        level_sequence = model.LevelSequence(key=level_sequence_key)
    level_sequence.name = name
    level_sequence.unlock_sequences = []
    for sequence_id in unlock_sequence_ids:
        level_sequence.unlock_sequences.append(ndb.Key(model.LevelSequence, sequence_id))
    level_sequence.put()
    return level_sequence

def resetAllTheThings():
    caesar_sequence = resetLevelSequence(model.LEVEL_LIST, 'Caesar Ciphers', ['substitution'])

    # Level 1 - Caesar Cipher
    resetText('caesar1', 'rotate', '{"rotate": "3"}')
    resetStandardDecryptLevel(caesar_sequence.key, 'caesar1', 'caesar1', ['caesar2'])

    # Caesar cipher 2 (ROT 13)
    resetText('caesar2', 'rotate', '{"rotate": "13"}')
    resetStandardDecryptLevel(caesar_sequence.key, 'caesar2', 'caesar2', ['caesar3'])

    # Caesar cipher 3 (rotate -5)
    resetText('caesar3', 'rotate', '{"rotate": "21"}')
    resetStandardDecryptLevel(caesar_sequence.key, 'caesar3', 'caesar3', [])

    appendToLevelSequence(caesar_sequence, ['caesar1', 'caesar2', 'caesar3'])

    # Substitution/Translation ciphers sequence
    translation_sequence = resetLevelSequence('substitution', "Substitution Ciphers", [])

    def alephmap(newaleph):
      result = {}
      for a, b in zip(string.lowercase, newaleph):
        result[a] = b
      return json.dumps(result)

    # Backwards alphabet substitution
    resetText('translation1', 'translate', alephmap('zyxwvutsrqponmlkjihgfedcba'))
    resetStandardDecryptLevel(translation_sequence.key, 'translation1', 'translation1', ['translation2'])

    # Substitution Cipher 2: Vowels and constonants shifted separately
    resetText('translation2', 'translate', alephmap('ecdfighjoklmnpuqrstvawxyzb'))
    resetStandardDecryptLevel(translation_sequence.key, 'translation2', 'translation2', ['translation3'])

    # Substitution Cipher 2: Scrambled alphabet
    resetText('translation3', 'translate', alephmap('kgxmqblwrjnydshzatoeuifpvc'))
    resetStandardDecryptLevel(translation_sequence.key, 'translation3', 'translation3', [])

    appendToLevelSequence(translation_sequence, ['translation1', 'translation2', 'translation3'])

    return [caesar_sequence, translation_sequence]


class ResetHandler(webapp2.RequestHandler):
    def get(self):
        level_sequences = resetAllTheThings()

        level_data = []
        for level_sequence in level_sequences:
          for level_key in level_sequence.levels:
              level_data.append(level_key.get())

        values = {'level_list':level_sequences, 'level_data':level_data}

        template = jinja_environment.get_template('reset.html')
        self.response.out.write(template.render(values))

app = webapp2.WSGIApplication([
    ('/resetdata', ResetHandler),
], debug=True)
