"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all() #create and drop db

        u1 = User.signup("test1", "email1@email.com", "password", None) #use signup method to create a user instance
        uid1 = 1111 #designate the uid to make referencing it easier
        u1.id = uid1

        u2 = User.signup("test2", "email2@email.com", "password", None) #making another user copy
        uid2 = 2222
        u2.id = uid2

        msg1 = Message("hi there", default, 1)
        msgid = 3333
        msg1.id = msgid

        like = Likes(2222, 3333)

        db.session.commit() #committing the copies to the session

        u1 = User.query.get(uid1) #establishing the variables
        u2 = User.query.get(uid2)

        self.u1 = u1 #storing all this info in self
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.msg1 = msg1

        self.like = like

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown() #calling super on teardown allows us to test more than one heirarchy multiple times
        db.session.rollback() 
        return res

# Does the repr method work as expected?
# Does the model successfully detect when user1 creates message1?
# Does the model successfully prevent user2 from creating message1?
# Does the model  successfully detect when message1 belongs to user1?
# Does the model successfully detect when user2 likes message1?
# Does the model successfully prevent user1 from liking message1?
# Does the model successfully detect when message1 belongs to the likes of user2?
# Does the model successfully prevent user1 from creating a second message with the same id as the first?
# Does the model successfully prevent user2 from liking user1's message multiple times?

