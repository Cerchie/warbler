"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


from app import app
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
        # calling super on teardown allows us to test more than one heirarchy multiple times
        res = super().tearDown()
        db.session.rollback()
        return res

# Does the model work on a basic level?
# Does the model successfully detect when user1 creates message1?
# Does the model  successfully detect when message1 belongs to user1?
    def test_message_model(self):
        """Does basic model work?"""

        m = Message(  # creating message
            text="a warble",
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit()  # adding to sesh

        # User should have 1 message
        # check that there is one msg
        self.assertEqual(len(self.u.messages), 1)
        # check that msg text is the same as the msg added
        self.assertEqual(self.u.messages[0].text, "a warble")


# Does the model successfully prevent user2 from creating message1? not addressed in solution code. check to see if addressed in views


# Does the model successfully prevent user1 from creating a second message with the same id as the first? not addressed in solution code. check to see if addressed in views

# Does the model successfully prevent user2 from liking user1's message multiple times?
# Does the model successfully detect when user2 likes message1?
# Does the model successfully prevent user1 from liking message1?
# Does the model successfully detect when message1 belongs to the likes of user2?

    def test_message_likes(self):
        m1 = Message(  # creating first msg instance
            text="a warble",
            user_id=self.uid
        )

        m2 = Message(
            text="a very interesting warble",  # creating second msg instance
            user_id=self.uid
        )

        # creating a test user instance
        u = User.signup("yetanothertest", "t@email.com", "password", None)
        uid = 888  # creating an id
        u.id = uid  # assigning it to our test user
        db.session.add_all([m1, m2, u])  # adding to sesh
        db.session.commit()  # committing

        u.likes.append(m1)  # adding m1 to user likes

        db.session.commit()  # committing

        # find likes where their user id = the test user id
        l = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(l), 1)  # there should be one
        # the id of the first message in the likes list should be the same as our test liked message
        self.assertEqual(l[0].message_id, m1.id)
