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

                # Get default level sequence
                level_sequence = ndb.Key(model.LevelSequence, model.LEVEL_LIST).get()
                start_level_key = level_sequence.levels[0]
                # Generate initial level state key with userid and level id
                user_level_state = self._getOrCreateUserLevelState(start_level_key)
                user_level_state.status = model.Status.UNLOCKED

                # Put this at the end, so it's not created if something failed.
                user_level_state.put()
                self.userState.put()

    def getLevelSequencesData(self):
        "Returns a list of (level object, status) tuples for the levels that the user has completed."""
        level_sequences = model.LevelSequence.getAll()
        level_sequences_data = []
        for level_sequence in level_sequences:
            sequence_data = {
                'name': level_sequence.name,
                'levels': [],
            }
            for level_key in level_sequence.levels:
                # Add whole level data to list
                level_state = self._getLevelStateKey(level_key).get()
                level = level_key.get()
                level_data = {
                    'key': level_key.urlsafe(),
                    'level_type': level.level_type,
                    'status': model.Status.LOCKED,
                }
                if level_state:
                    level_data['status'] = level_state.status
                sequence_data['levels'].append(level_data)
            level_sequences_data.append(sequence_data)
        return level_sequences_data

    def _getOrCreateUserLevelState(self, level_key):
        level_sequence_state_key = self._getLevelSequenceStateKey(level_key.parent())
        if not level_sequence_state_key.get():
            level_sequence_state = model.UserLevelSequenceState(key=level_sequence_state_key)
            # New level sequences are unlocked by default
            level_sequence_state.status = model.Status.UNLOCKED
            level_sequence_state.put()
        level_state_key = self._getLevelStateKey(level_key)
        level_state = level_state_key.get()
        if not level_state:
            level_state = model.UserLevelState(key=level_state_key)
            # New level is locked by default
            level_state.status = model.Status.LOCKED
            level_state.put()
        return level_state

    def _getLevelSequenceStateKey(self, level_sequence_key):
        level_sequence_state_key = ndb.Key(pairs=
            self.userState.key.pairs() +
            ((model.UserLevelSequenceState, level_sequence_key.id()),))
        return level_sequence_state_key

    def _getLevelStateKey(self, level_key):
        # The level state key is define as such:
        # (UserState, user_state_id, UserLevelSequenceState, level_seq_id, UserLevelState, level_id)
        level_state_key = ndb.Key(pairs=
            self.userState.key.pairs() +
            ((model.UserLevelSequenceState, level_key.parent().id()),
             (model.UserLevelState, level_key.id())))
        return level_state_key
    
    def recordWin(self, level_key):
        """Mark this level as completed for this user, and unlock the next level(s)."""
        user_level_state = self._getOrCreateUserLevelState(level_key)
        # Don't allow completion of a locked level
        if user_level_state.status not in [model.Status.COMPLETED, model.Status.LOCKED]:
            user_level_state.status = model.Status.COMPLETED
            user_level_state.put()

            # Unlock all the linked levels
            for unlock_level_key in level_key.get().unlock_levels:
                level_state = self._getOrCreateUserLevelState(unlock_level_key)
                # Don't accidently un-complete a level
                if level_state.status not in [model.Status.COMPLETED]:
                    level_state.status = model.Status.UNLOCKED
                    level_state.put()


