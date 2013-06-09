
from google.appengine.ext import ndb

LEVEL_LIST = "default"

class Level(ndb.Model):
    name = ndb.StringProperty()
    startstory = ndb.TextProperty()
    endstory = ndb.TextProperty()
    
    text = ndb.KeyProperty() # text used for this level
    unlock_decryptors = ndb.KeyProperty(repeated=True) # set of decryptor tools unlocked at this level
    unlock_tools = ndb.KeyProperty(repeated=True) # set of analysis tools unlocked at this level

class LevelSequence(ndb.Model):
    name = ndb.StringProperty()
    levels = ndb.KeyProperty(repeated=True)

class Text(ndb.Model):
    name = ndb.StringProperty()
    content = ndb.TextProperty()
    encrypted = ndb.TextProperty()

class LevelList(ndb.Model):
    levels = ndb.KeyProperty(repeated=True)

class UserState(ndb.Model):
    levels_completed = ndb.KeyProperty(repeated=True)


