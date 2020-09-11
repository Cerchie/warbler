"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows, Likes

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

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.uid = 94566
        u = User.signup("testing", "testing@test.com", "password", None)
        u.id = self.uid
        db.session.commit()

        self.u = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown() #calling super on teardown allows us to test more than one heirarchy multiple times
        db.session.rollback() 
        return res

# Does the model work on a basic level?
    def test_message_model(self):
        """Does basic model work?"""
        
        m = Message( #creating message
            text="a warble",
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit() #adding to sesh

        # User should have 1 message
        self.assertEqual(len(self.u.messages), 1) #check that there is one msg
        self.assertEqual(self.u.messages[0].text, "a warble") #check that msg text is the same as the msg added



# Does the model successfully detect when user1 creates message1?
# Does the model successfully prevent user2 from creating message1?
# Does the model  successfully detect when message1 belongs to user1?
# Does the model successfully detect when user2 likes message1?
# Does the model successfully prevent user1 from liking message1?
# Does the model successfully detect when message1 belongs to the likes of user2?
# Does the model successfully prevent user1 from creating a second message with the same id as the first?
# Does the model successfully prevent user2 from liking user1's message multiple times?

