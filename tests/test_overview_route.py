import unittest
from unittest.mock import patch
from flask import url_for, session, get_flashed_messages
from main_app_folder import create_app, db
from main_app_folder.models.user import User
from main_app_folder.models.outcomes import Outcome
from werkzeug.security import generate_password_hash

class OverviewRoutesTest(unittest.TestCase):

    def create_app(self):
        app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test_secret_key',
            'MAIL_SUPPRESS_SEND': True,  # Suppress sending emails during tests
            'SERVER_NAME': 'localhost.localdomain'  # Required for URL building in tests
        })
        return app

    def setUp(self):
        self.app = self.create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_view_finances_redirects_when_not_logged_in(self):
        response = self.client.get(url_for('overview.view_finances'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_view_finances_loads_when_logged_in(self):
        user = User(
            Name='Test',
            LastName='User',
            Email='test@example.com',
            Password=generate_password_hash('Testpass1!'),
            Role='user',
            ProfileImage='icon1.png'
        )
        db.session.add(user)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['user_id'] = user.UserID

        response = self.client.get(url_for('overview.view_finances'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Expenses', response.data)
        self.assertIn(b'Incomes', response.data)
        self.assertIn(b'Savings', response.data)
        self.assertIn(b'Subscriptions', response.data)

    def test_view_finances_shows_correct_data(self):
        user = User(
            Name='Test',
            LastName='User',
            Email='test@example.com',
            Password=generate_password_hash('Testpass1!'),
            Role='user',
            ProfileImage='icon1.png'
        )
        db.session.add(user)
        db.session.commit()

        outcomes = [
            Outcome(UserID=user.UserID, Day=20240501, Name='Rent', Cost=1000, Type='Expense'),
            Outcome(UserID=user.UserID, Day=20240501, Name='Salary', Cost=3000, Type='Income'),
            Outcome(UserID=user.UserID, Day=20240501, Name='Savings Account', Cost=500, Type='Saving'),
            Outcome(UserID=user.UserID, Day=20240501, Name='Netflix', Cost=15, Type='Subscription'),
        ]
        db.session.bulk_save_objects(outcomes)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['user_id'] = user.UserID

        response = self.client.get(url_for('overview.view_finances'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Rent', response.data)
        self.assertIn(b'Salary', response.data)
        self.assertIn(b'Savings Account', response.data)
        self.assertIn(b'Netflix', response.data)

    def test_view_finances_with_incorrect_user_id(self):
        user = User(
            Name='Test',
            LastName='User',
            Email='test@example.com',
            Password=generate_password_hash('Testpass1!'),
            Role='user',
            ProfileImage='icon1.png'
        )
        db.session.add(user)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['user_id'] = 9999  # Invalid user ID

        response = self.client.get(url_for('overview.view_finances'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_unauthorized_access_view_finances(self):
        response = self.client.get(url_for('overview.view_finances'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_view_finances_mixed_data(self):
        user = User(
            Name='Test',
            LastName='User',
            Email='test@example.com',
            Password=generate_password_hash('Testpass1!'),
            Role='user',
            ProfileImage='icon1.png'
        )
        db.session.add(user)
        db.session.commit()

        outcomes = [
            Outcome(UserID=user.UserID, Day=20240501, Name='Rent', Cost=1000, Type='Expense'),
            Outcome(UserID=user.UserID, Day=20240501, Name='Salary', Cost=3000, Type='Income'),
            Outcome(UserID=user.UserID, Day=20240501, Name='Savings Account', Cost=500, Type='Saving'),
            Outcome(UserID=user.UserID, Day=20240501, Name='Netflix', Cost=15, Type='Subscription'),
            Outcome(UserID=user.UserID, Day=20240501, Name='Bonus', Cost=200, Type='Income'),
            Outcome(UserID=user.UserID, Day=20240501, Name='Electricity', Cost=100, Type='Expense'),
            Outcome(UserID=user.UserID, Day=20240501, Name='Gym Membership', Cost=30, Type='Subscription')
        ]
        db.session.bulk_save_objects(outcomes)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['user_id'] = user.UserID

        response = self.client.get(url_for('overview.view_finances'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Rent', response.data)
        self.assertIn(b'Salary', response.data)
        self.assertIn(b'Savings Account', response.data)
        self.assertIn(b'Netflix', response.data)
        self.assertIn(b'Bonus', response.data)
        self.assertIn(b'Electricity', response.data)
        self.assertIn(b'Gym Membership', response.data)

if __name__ == '__main__':
    unittest.main()
