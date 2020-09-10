"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

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


class UserModelTestCase(TestCase):
    """Test views for messages."""

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

        db.session.commit() #committing the user copies to the session

        u1 = User.query.get(uid1) #establishing the variables
        u2 = User.query.get(uid2)

        self.u1 = u1 #storing all this info in self
        self.uid1 = uid1

        self.u2 = u2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown() #calling super on teardown allows us to test more than one heirarchy multiple times
        db.session.rollback() 
        return res

# Does the repr method work as expected? 
# Does is_following successfully detect when user1 is following user2?
    def test_is_following(self):
        self.u1.following.append(self.u2) #making u2 a follower of u1
        db.session.commit() #committing to session

        self.assertTrue(self.u1.is_following(self.u2)) #use assertTrue to see if it successfully detects u1 following u2

        self.assertFalse(self.u2.is_following(self.u1)) #use assertFalse to detect the relationship going in the other direction


# Does is_followed_by successfully detect when user1 is followed by user2?

    def test_is_followed_by(self):
        self.u1.following.append(self.u2) #making u2 a follower of u1
        db.session.commit() #committing to session

        self.assertTrue(self.u2.is_followed_by(self.u1)) # check to see that u1 is follwoing u2 with assertTrue
        self.assertFalse(self.u1.is_followed_by(self.u2)) #check relationship in other direction

# Does is_following successfully detect when user1 is not following user2?
# Does is_followed_by successfully detect when user1 is not followed by user2?
    def test_user_follows(self):
        self.u1.following.append(self.u2) #make u1 a follower of u2
        db.session.commit() #commit to session

        self.assertEqual(len(self.u2.following), 0) #checking to see that u2 is following no one
        self.assertEqual(len(self.u2.followers), 1) #checking to see that u2 has no other followers
        self.assertEqual(len(self.u1.followers), 0) #checking to see that u1 has no followers
        self.assertEqual(len(self.u1.following), 1) #checking to see that u1 is only following u2

        self.assertEqual(self.u2.followers[0].id, self.u1.id) #checking to see that the ids of u2's follower and u1 match
        self.assertEqual(self.u1.following[0].id, self.u2.id) #checking to see that u1's following id matches u2's

# Does User.create successfully create a new user given valid credentials?
# Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?
# Does User.authenticate successfully return a user when given a valid username and password?
# Does User.authenticate fail to return a user when the username is invalid?
# Does User.authenticate fail to return a user when the password is invalid?

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)