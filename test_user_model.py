"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


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
    def test_valid_signup(self):
        u_test = User.signup("testtesttest", "testtest@test.com", "password", None) #usimg signup method to create u to test against
        uid = 99999 #creating an id
        u_test.id = uid #assigning it to the u_test user
        db.session.commit() #committing to session

        u_test = User.query.get(uid) #fetching the test user from the session using uid
        self.assertIsNotNone(u_test) #testing that a value is there
        self.assertEqual(u_test.username, "testtesttest") #testing that the username is the same as the test user's
        self.assertEqual(u_test.email, "testtest@test.com") #testing that the email is the same as the test user's
        self.assertNotEqual(u_test.password, "password") #testing that the password is the same as the test user's
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$")) #making sure the bcrypt strings are on the level

# Does User.create fail to create a new user if any of the validations (e.g. uniqueness, non-nullable fields) fail?
    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test@test.com", "password", None) #try to create user without username using signup method
        uid = 123456789 #creating id for invalid test user 
        invalid.id = uid #assigning the id to the invalid test user
        with self.assertRaises(exc.IntegrityError) as context: #use assertRaises to make sure the IntegrityError pops up
            db.session.commit() #commit to session

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password", None) #try to create user without email using signup method
        uid = 123789 #creating id for invalid test user 
        invalid.id = uid #assigning the id to the invalid test user
        with self.assertRaises(exc.IntegrityError) as context: #use assertRaises to make sure the IntegrityError pops up
            db.session.commit() #commit to session
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context: #make sure that when use signs up without entering pword a ValueError is raised
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context: 
            User.signup("testtest", "email@email.com", None, None)

# Does User.authenticate successfully return a user when given a valid username and password?
    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password") #give a valid username/password
        self.assertIsNotNone(u) #check user existence
        self.assertEqual(u.id, self.uid1) #check u.id = u1 uid
# Does User.authenticate fail to return a user when the username is invalid?
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password")) #check that a bad username is assertedFalse

# Does User.authenticate fail to return a user when the password is invalid?
    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword")) #check that a bad pword is assertedFalse


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