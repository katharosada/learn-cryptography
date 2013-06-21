"""
Useful accessor methods for looking up user progress information stored in the
the db.
"""

import logging
import model
from google.appengine.ext import ndb

class UserTracker(object):
    def __init__(self, userObject, userState=None):
        """Constructor for UserTracker.
        Keyword arguments:
        userObject -- the appengine user object (required)
        userState  -- the ndb.Model UserState object
        """
        assert userObject != None
        self.user = userObject
        if not userState:
            # Look up that user in the datastore
            userKey = ndb.Key(model.UserState, userObject.user_id())
            self.userState = userKey.get()
            if self.userState == None:
                # User state does not exist, create default empty user state
                self.userState = model.UserState(key=userKey)
                self.userState.put()

    def getLevelList(self):
        "Returns a list of level id's that the user has completed."""
        levels = []
        for level_id in self.userState.levels_completed:
            # Add whole level data to list
            level = level_id.get()
            if level:
                levels.append(level)
        return levels
    
    def recordWin(self, level_id):
        """Save the level id in the list of completed levels for this user."""
        level_key = ndb.Key(model.Level, level_id)
        if level_key not in self.userState.levels_completed:
            self.userState.levels_completed.append(level_key)
        ret = self.userState.put()


