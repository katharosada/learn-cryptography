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

                # Generate initial level state key with userid and level id
                # TODO: Don't hard-code the starting level. bad bad bad.
                userLevelState = model.UserLevelState(key=self.getLevelStateKey('caesar'))
                userLevelState.status = model.Status.UNLOCKED
                userLevelState.put()

    def getLevelList(self):
        "Returns a list of level id's that the user has completed."""
        levels = []
        level_sequence = ndb.Key(model.LevelSequence, model.LEVEL_LIST)
        for level_key in level_sequence.get().levels:
            # Add whole level data to list
            level_state = self.getLevelStateKey(level_key.id()).get()
            if level_state:
                level = level_key.get()
                levels.append((level, level_state.status))
        return levels

    def getLevelStateKey(self, level_id):
        level_state_key = ndb.Key(pairs=self.userState.key.pairs()+((model.UserLevelState, level_id),))
        return level_state_key
    
    def recordWin(self, level_key):
        """Save the level id in the list of completed levels for this user."""
        levelStateKey = self.getLevelStateKey(level_key.id())

        # Find existing UserLevelState (should either be already completed or at least unlocked)
        userLevelState = levelStateKey.get()
        if userLevelState == None:
            # TODO: Once we add locked/unlocked state a check here that the user didn't just solve a locked level 
            logging.warning("User just solved a level which had no exisitng unlock state.")
            userLevelState = model.UserLevelState(key=levelStateKey)
        # The state already exists, just update the status to completed.
        userLevelState.status = model.Status.COMPLETED
        userLevelState.put()

        # Unlock all the linked levels
        for unlock_level_key in level_key.get().unlock_levels:
            level_state_key = self.getLevelStateKey(unlock_level_key.id())
            level_state = level_state_key.get()
            if not level_state:
                level_state = model.UserLevelState(key=level_state_key)
            if level_state.status not in [model.Status.COMPLETED]:
                level_state.status = model.Status.UNLOCKED
                level_state.put()


