
from google.appengine.ext import ndb

class Level(ndb.Model):
    name = ndb.StringProperty()
    startstory = ndb.TextProperty()
    endstory = ndb.TextProperty()
    
    texts = ndb.KeyProperty(repeated=True) # set of texts used for this level
    unlock_decryptors = ndb.KeyProperty(repeated=True) # set of decryptor tools unlocked at this level
    unlock_tools = ndb.KeyProperty(repeated=True) # set of analysis tools unlocked at this level

class Texts(ndb.Model):
    name = ndb.StringProperty()
    path = ndb.StringProperty()
    # Some kind of blobstore key?

class LevelList(ndb.Model):
    levels = ndb.KeyProperty(repeated=True)

class User(ndb.Model):
###    userid = ???
    current_level = ndb.KeyProperty()
    unlocked


