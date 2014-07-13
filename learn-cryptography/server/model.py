
from google.appengine.ext import ndb

# The id of the LevelSequence to start on.
LEVEL_LIST = "default"

class LevelType(object):
    STANDARD_DECRYPT = 0
    NEW_CIPHER_INRO = 1
    UNKNOWN_CIPHER_CHALLENGE = 2 # Not implemented

class Level(ndb.Model):
    """A single level in the game.
    Contains an encrypted text which must be decrypted to pass.
    """
    # Level type (enum of LevelType)
    level_type = ndb.IntegerProperty()

    # Custom angular partial template for a custom level
    # Must be a template in the client/partials directory.
    custom_template = ndb.StringProperty()
    
    # Reference to the text used for this level (for normal decryption levels)
    text = ndb.KeyProperty()
    # TODO: In future, we should separate the text and the encryption method so
    # we can randomly generate new challenges from a subset of ciphers.

    # [unused] Set of decryptor tools unlocked at this level
    unlock_decryptors = ndb.KeyProperty(repeated=True)

    # [unused] Set of analysis tools unlocked at this level
    unlock_tools = ndb.KeyProperty(repeated=True)
    unlock_levels = ndb.KeyProperty(repeated=True)


class LevelSequence(ndb.Model):
    """One set of levels which are part of a theme or in a sequence."""
    name = ndb.StringProperty()
    levels = ndb.KeyProperty(repeated=True)
    unlock_sequences = ndb.KeyProperty(repeated=True)

    @classmethod
    def getAll(cls):
        return cls.query().fetch()


class Text(ndb.Model):
    """A cipher text, stored encrypted and in plain text."""
    content = ndb.TextProperty()
    encrypted = ndb.TextProperty()


class UserState(ndb.Model):
    """All game-relevant information stored about a user.
    Currently just the completion/unlock state of levels."""
    # Maybe we want to store more stuff here later but for now it's just a
    # holder for the per-user key.
    pass


class Status(object):
    """Enum for the per-user completion status of a level."""
    LOCKED = 0 # Generally not used because the UserLevelState is non-existant in this case
    UNLOCKED = 1
    COMPLETED = 3

class UserLevelSequenceState(ndb.Model):
    """One user's current state for the levelSequence."""
    # Enum for current state defined by Status class
    status = ndb.IntegerProperty()

class UserLevelState(ndb.Model):
    """One user's current state for one level.
    The keys for these objects are the level id with the user id as a parent key"""
    # Enum for current state defined by Status class
    status = ndb.IntegerProperty() 


