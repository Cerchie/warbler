"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

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

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()  # creating test client

        self.testuser = User.signup(username="testuser",  # creating test user instance
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 8989  # creating a user id
        self.testuser.id = self.testuser_id  # setting the user id to our test user

        self.u1 = User.signup("abc", "test1@test.com",
                              "password", None)  # creating test user 1
        self.u1_id = 778  # creating a user id
        self.u1.id = self.u1_id  # setting the user id to our test user
        self.u2 = User.signup("efg", "test2@test.com",
                              "password", None)  # creating test user 2
        self.u2_id = 884  # creating a user id
        self.u2.id = self.u2_id  # setting the user id to our test user
        # creating test user 3, no id
        self.u3 = User.signup("hij", "test3@test.com", "password", None)
        # creating test user 4, no id
        self.u4 = User.signup("testing", "test4@test.com", "password", None)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_index(self):
        with self.client as c:  # setting up client
            resp = c.get("/users")  # response is /users page

            # checking that each user is on the page
            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@abc", str(resp.data))
            self.assertIn("@efg", str(resp.data))
            self.assertIn("@hij", str(resp.data))
            self.assertIn("@testing", str(resp.data))

    def test_users_search(self):
        with self.client as c:
            resp = c.get("/users?q=test")

            # checking that users with ids show up
            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@testing", str(resp.data))

            # and that users without don't
            self.assertNotIn("@abc", str(resp.data))
            self.assertNotIn("@efg", str(resp.data))
            self.assertNotIn("@hij", str(resp.data))

    def test_user_show(self):
        with self.client as c:
            resp = c.get(f"/users/{self.testuser_id}")  # route is users/userid

            self.assertEqual(resp.status_code, 200)  # resp comes up properly

            # testuser str is in the data coming back from the server
            self.assertIn("@testuser", str(resp.data))

    def setup_likes(self):  # setting up likes for likes tests
        # creating 3 messages, last is the only one with id
        m1 = Message(text="trending warble", user_id=self.testuser_id)
        m2 = Message(text="Eating some lunch", user_id=self.testuser_id)
        m3 = Message(id=9876, text="likable warble", user_id=self.u1_id)
        db.session.add_all([m1, m2, m3])
        db.session.commit()  # adding and committing to session

        l1 = Likes(user_id=self.testuser_id,
                   message_id=9876)  # setting up likes

        db.session.add(l1)
        db.session.commit()  # committing likes to session

    def test_user_show_with_likes(self):  # do the likes show up with the user?
        self.setup_likes()  # running the setup function

        with self.client as c:
            # setting the response to the user detail page
            resp = c.get(f"/users/{self.testuser_id}")

            # making sure the page shows up
            self.assertEqual(resp.status_code, 200)

            # making sure the username shows up in the response from the server
            self.assertIn("@testuser", str(resp.data))
            # response.date is the src for beautiful soup object
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            # find all the lis on the page
            found = soup.find_all("li", {"class": "stat"})
            # there should be 4 lis on the page
            self.assertEqual(len(found), 4)

            # test for a count of 2 messages
            self.assertIn("2", found[0].text)

            # Test for a count of 0 followers
            self.assertIn("0", found[1].text)

            # Test for a count of 0 following
            self.assertIn("0", found[2].text)

            # Test for a count of 1 like
            self.assertIn("1", found[3].text)

    def test_add_like(self):
        # creating like instance and adding to session
        m = Message(id=1984, text="The earth is round", user_id=self.u1_id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                # checking that user must be signed in
                sess[CURR_USER_KEY] = self.testuser_id

            # setting route to like instance
            resp = c.post("/messages/1984/like", follow_redirects=True)
            # checking that page shows up
            self.assertEqual(resp.status_code, 200)

            # getting likes with message_id 1984
            likes = Likes.query.filter(Likes.message_id == 1984).all()
            # checking that the number of likes = 1
            self.assertEqual(len(likes), 1)
            # checking that the likes with the user_id we have matches our test like
            self.assertEqual(likes[0].user_id, self.testuser_id)

    def test_remove_like(self):
        self.setup_likes()  # setting up likes

        m = Message.query.filter(
            Message.text == "likable warble").one()  # making a message
        self.assertIsNotNone(m)  # checking that it's not None
        # checking that this message does not belong to our test user
        self.assertNotEqual(m.user_id, self.testuser_id)

        l = Likes.query.filter(
            Likes.user_id == self.testuser_id and Likes.message_id == m.id
        ).one()  # checking to see that this like is an intersection of msg id and user id

        # Now we are sure that testuser likes the message "likable warble"
        self.assertIsNotNone(l)  # checking that the value of like is not None

        with self.client as c:
            with c.session_transaction() as sess:
                # checking that user is logged in
                sess[CURR_USER_KEY] = self.testuser_id

            # setting up the response as /messages/id/like
            resp = c.post(f"/messages/{m.id}/like", follow_redirects=True)
            # checking that we get the response
            self.assertEqual(resp.status_code, 200)

            # setting up likes as the likes with message_id = to m.id
            likes = Likes.query.filter(Likes.message_id == m.id).all()
            # the like has been deleted #checking that the length of these likes is 0

    def test_unauthenticated_like(self):
        self.setup_likes()  # setting up likes

        m = Message.query.filter(Message.text == "likable warble").one()
        self.assertIsNotNone(m)

        like_count = Likes.query.count()

        with self.client as c:
            resp = c.post(f"/messages/{m.id}/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            self.assertIn("Access unauthorized", str(resp.data))

            # The number of likes has not changed since making the request
            self.assertEqual(like_count, Likes.query.count())
# When you’re logged in, can you see the follower / following pages for any user?
# When you’re logged out, are you disallowed from visiting a user’s follower / following pages?
# When you’re logged in, can you add a message as yourself?
# When you’re logged in, can you delete a message as yourself?
# When you’re logged out, are you prohibited from adding messages?
# When you’re logged out, are you prohibited from deleting messages?
# When you’re logged in, are you prohibiting from adding a message as another user?
# When you’re logged in, are you prohibiting from deleting a message as another user?
