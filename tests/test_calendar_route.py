import unittest
from unittest.mock import patch
from flask import url_for, session
from main_app_folder import create_app, db
from main_app_folder.models.user import User
from main_app_folder.models.outcomes import Outcome  # Make sure to import the Outcome model
from werkzeug.security import generate_password_hash
import json

class CalendarRoutesTest(unittest.TestCase):

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

    def test_calendar_page_redirects_when_not_logged_in(self):
        response = self.client.get(url_for('calendar.calendar'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_calendar_page_loads_when_logged_in(self):
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

        response = self.client.get(url_for('calendar.calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Calendar', response.data)

    def test_get_outcomes_redirects_when_not_logged_in(self):
        response = self.client.post(url_for('calendar.get_outcomes'), json={'day': '2024-05-01'})
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_get_outcomes_returns_data_when_logged_in(self):
        # Create a test user
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

        # Create a test outcome for the user
        outcome = Outcome(UserID=user.UserID, Day=1, Month=5, Year=2024, Name='Test Outcome', Cost=100, Fulfilled=False)
        db.session.add(outcome)
        db.session.commit()

        # Set the user in the session
        with self.client.session_transaction() as sess:
            sess['user_id'] = user.UserID

        # Mocking the cursor and connection to use SQLAlchemy directly
        with patch('main_app_folder.utils.helpers.get_db_connection') as mock_get_db_connection:
            mock_conn = mock_get_db_connection.return_value
            mock_cursor = mock_conn.cursor.return_value

            # Mock the cursor to return the inserted outcome
            mock_cursor.fetchall.return_value = [
                (outcome.ID, outcome.Name, outcome.Cost, outcome.Fulfilled)
            ]

            response = self.client.post(url_for('calendar.get_outcomes'), json={'day': '1'})
            
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['name'], 'Test Outcome')
        self.assertEqual(data[0]['amount'], 100)
        self.assertFalse(data[0]['fulfilled'])
    
    def test_get_outcomes_status_by_day(self):
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

        outcome1 = Outcome(UserID=user.UserID, Day=1, Month=5, Year=2024, Name='Test Outcome 1', Cost=100, Fulfilled=True)
        outcome2 = Outcome(UserID=user.UserID, Day=1, Month=5, Year=2024, Name='Test Outcome 2', Cost=200, Fulfilled=True)
        outcome3 = Outcome(UserID=user.UserID, Day=2, Month=5, Year=2024, Name='Test Outcome 3', Cost=150, Fulfilled=False)
        db.session.add_all([outcome1, outcome2, outcome3])
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['user_id'] = user.UserID

        response = self.client.post(url_for('calendar.get_outcomes_status_by_day'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['1'])
        self.assertFalse(data['2'])

    def test_reset_finances(self):
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

        outcome1 = Outcome(UserID=user.UserID, Day=1, Month=5, Year=2024, Name='Test Subscription', Cost=100, Fulfilled=True, Type='Subscription')
        outcome2 = Outcome(UserID=user.UserID, Day=1, Month=5, Year=2024, Name='Test Expense', Cost=50, Fulfilled=True, Type='Expense')
        db.session.add_all([outcome1, outcome2])
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['user_id'] = user.UserID

        response = self.client.post(url_for('calendar.reset_finances'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)

        self.assertTrue(data['success'])
        reset_outcomes = Outcome.query.filter_by(UserID=user.UserID).all()
        self.assertTrue(all(outcome.Fulfilled == False for outcome in reset_outcomes))

    def test_get_outcomes_for_specific_day(self):
        # Create a test user
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

        # Create outcomes for the user
        outcome1 = Outcome(UserID=user.UserID, Name='Outcome 1', Cost=100, Day=1, Month=5, Year=2024, Fulfilled=False, Type='Expense')
        outcome2 = Outcome(UserID=user.UserID, Name='Outcome 2', Cost=200, Day=1, Month=5, Year=2024, Fulfilled=True, Type='Expense')
        db.session.add_all([outcome1, outcome2])
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['user_id'] = user.UserID

        # Note: Ensure the date format is 'YYYY-MM-DD'
        response = self.client.post(url_for('calendar.get_outcomes'), json={'day': 1})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['name'], 'Outcome 1')
        self.assertEqual(data[0]['amount'], 100)
        self.assertFalse(data[0]['fulfilled'])
        self.assertEqual(data[1]['name'], 'Outcome 2')
        self.assertEqual(data[1]['amount'], 200)
        self.assertTrue(data[1]['fulfilled'])

    def test_unauthorized_update_outcome_status(self):
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

        outcome = Outcome(UserID=user.UserID, Day=1, Month=5, Year=2024, Name='Test Outcome', Cost=100, Fulfilled=False)
        db.session.add(outcome)
        db.session.commit()

        response = self.client.post(url_for('calendar.update_outcome_status'), json={
            'out_id': outcome.ID,
            'status': True
        })
        self.assertEqual(response.status_code, 401)
        data = json.loads(response.data)
        self.assertEqual(data['message'], 'Unauthorized')

    def test_reset_finances_with_no_outcomes(self):
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

        response = self.client.post(url_for('calendar.reset_finances'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])

    def test_get_outcomes_when_none_exist(self):
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

        response = self.client.post(url_for('calendar.get_outcomes'), json={'day': 1})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(len(data), 0)
if __name__ == '__main__':
    unittest.main()
