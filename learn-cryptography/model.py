
from google.appengine.ext import ndb

LEVEL_LIST = "default"

class Level(ndb.Model):
    """A single level in the game.
    Contains intro and end story and an encrypted text which must be decrypted.
    """
    name = ndb.StringProperty()
    startstory = ndb.TextProperty()
    endstory = ndb.TextProperty()
    
    text = ndb.KeyProperty() # text used for this level
    unlock_decryptors = ndb.KeyProperty(repeated=True) # set of decryptor tools unlocked at this level
    unlock_tools = ndb.KeyProperty(repeated=True) # set of analysis tools unlocked at this level
    unlock_levels = ndb.KeyProperty(repeated=True)


class LevelSequence(ndb.Model):
    """One set of levels which are part of a theme or in a sequence."""
    name = ndb.StringProperty()
    levels = ndb.KeyProperty(repeated=True)


class Text(ndb.Model):
    """A cipher text, stored encrypted and in plain text."""
    name = ndb.StringProperty()
    content = ndb.TextProperty()
    encrypted = ndb.TextProperty()


class UserState(ndb.Model):
    """All game-relevant information stored about a user.
    Currently just the completion/unlock state of levels."""
    # Maybe we want to store more stuff here lated but for now it's just a
    # holder for the per-user key.
    pass


class Status(object):
    """Enum for the per-user completion status of a level."""
    LOCKED = 0 # Generally not used because the UserLevelState is non-existant in this case
    UNLOCKED = 1
    COMPLETED = 3


class UserLevelState(ndb.Model):
    """One user's current state for one level.
    The keys for these objects are the level id with the user id as a parent key"""
    # Enum for current state defined by Status class
    status = ndb.IntegerProperty() 


