import unittest
from flask import url_for, session
from main_app_folder import create_app, db
from main_app_folder.models.user import User

class HomeRoutesTest(unittest.TestCase):

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

    def test_home_page_loads(self):
        response = self.client.get(url_for('home.home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Home', response.data)

    def test_root_page_redirects_to_home(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/home', response.location)

    def test_home_page_css_loaded(self):
        response = self.client.get(url_for('home.home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'rel="stylesheet"', response.data)
        self.assertIn(b'css/style.css', response.data)

    def test_home_page_js_loaded(self):
        response = self.client.get(url_for('home.home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'script src', response.data)
        self.assertIn(b'js/main.js', response.data)

    def test_home_page_logged_in_user(self):
        # Create a test user
        user = User(Name='Test', LastName='User', Email='test@example.com', Password='testpass')
        db.session.add(user)
        db.session.commit()

        with self.client.session_transaction() as sess:
            sess['user_id'] = user.UserID

        response = self.client.get(url_for('home.home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to WalletBuddyAI', response.data)

    def test_home_page_specific_elements(self):
        response = self.client.get(url_for('home.home'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome to WalletBuddyAI', response.data)
        self.assertIn(b'Mission', response.data)
        self.assertIn(b'How It Works', response.data)
        self.assertIn(b'Key Features', response.data)
        self.assertIn(b'Personal Information', response.data)
        self.assertIn(b'Get Started', response.data)

if __name__ == '__main__':
    unittest.main()