"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User

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

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()
# When you’re logged in, can you add a message as yourself?

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_message_show(self):

        m = Message(
            id=1234,
            text="a test message",
            user_id=self.testuser_id
        )

        db.session.add(m)
        db.session.commit()  # create msg instance and add to session

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id  # auth

            m = Message.query.get(1234)  # grab msg

            resp = c.get(f'/messages/{m.id}')  # grab route

            self.assertEqual(resp.status_code, 200)  # page shows
            # check that msg text appears
            self.assertIn(m.text, str(resp.data))

# When you’re logged out, are you prohibited from adding messages?

    def test_add_no_session(self):
        with self.client as c:
            resp = c.post("/messages/new",
                          data={"text": "Hello"}, follow_redirects=True)  # grabbing route without auth
            self.assertEqual(resp.status_code, 200)  # page shows up
            self.assertIn("Access unauthorized", str(
                resp.data))  # err msg shows
# When you’re logged in, are you prohibiting from adding a message as another user?

    def test_add_invalid_user(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 99222224  # user does not exist

            # grabbing route
            resp = c.post("/messages/new",
                          data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)  # page shows up
            self.assertIn("Access unauthorized", str(
                resp.data))  # err msg shows

    def test_invalid_message_show(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id  # user logged in

            resp = c.get('/messages/99999999')  # msg doesn not exist

            self.assertEqual(resp.status_code, 404)  # check that 404 is thrown
# When you’re logged in, can you delete a message as yourself?

    def test_message_delete(self):

        m = Message(
            id=1234,
            text="a test message",
            user_id=self.testuser_id  # create test message
        )
        db.session.add(m)
        db.session.commit()  # committing to session

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id  # user logged in

            resp = c.post("/messages/1234/delete",
                          follow_redirects=True)  # grab route
            self.assertEqual(resp.status_code, 200)  # make sure it exists

            m = Message.query.get(1234)  # grab the message
            self.assertIsNone(m)  # make sure its value is None


# When you’re logged out, are you prohibited from deleting messages?


    def test_unauthorized_message_delete(self):

        # A second user that will try to delete the message
        u = User.signup(username="unauthorized-user",
                        email="testtest@test.com",
                        password="password",
                        image_url=None)  # create 2nd user
        u.id = 76543

        # Message is owned by testuser
        m = Message(
            id=1234,
            text="a test message",
            user_id=self.testuser_id
        )
        db.session.add_all([u, m])
        db.session.commit()  # committing to session

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 76543  # logged in

            resp = c.post("/messages/1234/delete",
                          follow_redirects=True)  # grabbing route
            self.assertEqual(resp.status_code, 200)  # status code 200
            self.assertIn("Access unauthorized", str(
                resp.data))  # err msg shows

            m = Message.query.get(1234)  # get msg
            self.assertIsNotNone(m)  # make sure its value is not None

# When you’re logged in, are you prohibiting from deleting a message as another user?
    def test_message_delete_no_authentication(self):

        m = Message(  # test msg
            id=1234,
            text="a test message",
            user_id=self.testuser_id
        )
        db.session.add(m)
        db.session.commit()  # commit to session

        with self.client as c:
            resp = c.post("/messages/1234/delete",
                          follow_redirects=True)  # grab route
            self.assertEqual(resp.status_code, 200)  # assert route present
            self.assertIn("Access unauthorized", str(
                resp.data))  # err msg shows

            m = Message.query.get(1234)  # grab msg
            self.assertIsNotNone(m)  # ensure msg is still there
