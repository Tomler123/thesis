import unittest
from unittest.mock import patch
from flask import url_for, get_flashed_messages
from flask_mail import Mail
from itsdangerous import Serializer
from main_app_folder import create_app, db
from main_app_folder.models.user import User
from main_app_folder.routes.auth_routes import pending_users, configure_mail
from werkzeug.security import generate_password_hash, check_password_hash

class AuthRoutesTest(unittest.TestCase):

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
        self.mail = configure_mail(self.app, 587, True, False)

        # Clear pending users before each test
        pending_users.clear()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_signup_page_loads(self):
        response = self.client.get(url_for('auth.signup'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)

    @patch('flask_mail.Mail.send')
    def test_signup_form_submission(self, mock_mail_send):
        mock_mail_send.return_value = None  # Mock the send method to do nothing

        with self.client:
            response = self.client.post(url_for('auth.signup'), data={
                'name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'password': 'Testpass1!',
                'confirm_password': 'Testpass1!'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            flashed_messages = [message for category, message in get_flashed_messages(with_categories=True)]
            self.assertIn('You have successfully signed up!', flashed_messages)
            self.assertIn('test@example.com', pending_users)
            self.assertEqual(pending_users['test@example.com']['name'], 'Test')
            self.assertEqual(pending_users['test@example.com']['last_name'], 'User')
            self.assertEqual(pending_users['test@example.com']['email'], 'test@example.com')

    @patch('flask_mail.Mail.send')
    def test_signup_form_submission_existing_email(self, mock_mail_send):
        mock_mail_send.return_value = None  # Mock the send method to do nothing

        # Create a user in the database with the same email
        user = User(
            Name='Existing',
            LastName='User',
            Email='test@example.com',
            Password=generate_password_hash('Existingpass1!'),
            Role='user',
            ProfileImage='icon1.png'
        )
        db.session.add(user)
        db.session.commit()

        with self.client:
            response = self.client.post(url_for('auth.signup'), data={
                'name': 'Test',
                'last_name': 'User',
                'email': 'test@example.com',
                'password': 'Testpass1!',
                'confirm_password': 'Testpass1!'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            flashed_messages = [message for category, message in get_flashed_messages(with_categories=True)]
            self.assertIn('You have successfully signed up!', flashed_messages)
            self.assertIn('test@example.com', pending_users)

    def test_login_page_loads(self):
        response = self.client.get(url_for('auth.login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Log In', response.data)

    def test_login_success(self):
        # Create a user in the database
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

        with self.client:
            response = self.client.post(url_for('auth.login'), data={
                'email': 'test@example.com',
                'password': 'Testpass1!'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)

    def test_login_failure(self):
        # Create a user in the database
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

        with self.client:
            response = self.client.post(url_for('auth.login'), data={
                'email': 'test@example.com',
                'password': 'WrongPassword1!'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            flashed_messages = [message for category, message in get_flashed_messages(with_categories=True)]
            self.assertIn('Invalid email or password', flashed_messages)

    @patch('flask_mail.Mail.send')
    def test_forgot_password_page_loads(self, mock_mail_send):
        response = self.client.get(url_for('auth.forgot_password'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Forgot Password', response.data)

    @patch('flask_mail.Mail.send')
    def test_forgot_password_form_submission(self, mock_mail_send):
        mock_mail_send.return_value = None  # Mock the send method to do nothing

        # Create a user in the database
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

        with self.client:
            response = self.client.post(url_for('auth.forgot_password'), data={
                'email': 'test@example.com'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)

    @patch('flask_mail.Mail.send')
    def test_forgot_password_form_submission_nonexistent_email(self, mock_mail_send):
        mock_mail_send.return_value = None  # Mock the send method to do nothing

        with self.client:
            response = self.client.post(url_for('auth.forgot_password'), data={
                'email': 'nonexistent@example.com'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            flashed_messages = [message for category, message in get_flashed_messages(with_categories=True)]
            self.assertIn('No account with that email address exists.', flashed_messages)

    def test_forgot_password_confirm_page_loads(self):
        response = self.client.get(url_for('auth.forgot_password_confirm'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Email Sent!', response.data)

    @patch('flask_mail.Mail.send')
    def test_reset_password_page_loads(self, mock_mail_send):
        mock_mail_send.return_value = None  # Mock the send method to do nothing

        # Create a user in the database
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

        # Simulate forgot password form submission to generate token
        with self.client:
            self.client.post(url_for('auth.forgot_password'), data={'email': 'test@example.com'}, follow_redirects=True)

            # Extract token directly using serializer
            serializer = Serializer(self.app.config['SECRET_KEY'])
            token = serializer.dumps('test@example.com', salt='password-reset-salt')

            response = self.client.get(url_for('auth.reset_password', token=token))
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'Reset Password', response.data)


    @patch('flask_mail.Mail.send')
    def test_reset_password_form_submission(self, mock_mail_send):
        mock_mail_send.return_value = None  # Mock the send method to do nothing

        # Create a user in the database
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

        # Simulate forgot password form submission to generate token
        with self.client:
            self.client.post(url_for('auth.forgot_password'), data={'email': 'test@example.com'}, follow_redirects=True)

            # Extract token directly using serializer
            serializer = Serializer(self.app.config['SECRET_KEY'])
            token = serializer.dumps('test@example.com', salt='password-reset-salt')

            # Simulate resetting the password
            with self.client.session_transaction() as sess:
                sess['reset_email'] = 'test@example.com'

            response = self.client.post(url_for('auth.reset_password', token=token), data={
                'password': 'NewTestpass1!',
                'confirm_password': 'NewTestpass1!'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)
            flashed_messages = [message for category, message in get_flashed_messages(with_categories=True)]
            self.assertIn('Your password has been reset successfully. You can now log in with your new password.', flashed_messages)

    @patch('flask_mail.Mail.send')
    def test_contact_page_loads(self, mock_mail_send):
        mock_mail_send.return_value = None  # Mock the send method to do nothing

        # Create a user in the database
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

        with self.client:
            # Log in the user
            self.client.post(url_for('auth.login'), data={
                'email': 'test@example.com',
                'password': 'Testpass1!'
            }, follow_redirects=True)

            response = self.client.get(url_for('auth.contact'))
            self.assertIn(response.status_code, [200, 302])
            
    @patch('flask_mail.Mail.send')
    def test_contact_form_submission(self, mock_mail_send):
        mock_mail_send.return_value = None  # Mock the send method to do nothing

        # Create a user in the database
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

        with self.client:
            # Log in the user
            self.client.post(url_for('auth.login'), data={
                'email': 'test@example.com',
                'password': 'Testpass1!'
            }, follow_redirects=True)

            response = self.client.post(url_for('auth.contact'), data={
                'message': 'This is a test message.'
            }, follow_redirects=True)

            self.assertEqual(response.status_code, 200)

    @patch('flask_mail.Mail.send')
    def test_contact_page_requires_login(self, mock_mail_send):
        mock_mail_send.return_value = None  # Mock the send method to do nothing

        with self.client:
            response = self.client.get(url_for('auth.contact'), follow_redirects=True)
            self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
