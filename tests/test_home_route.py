import unittest
from flask import url_for
from main_app_folder import create_app, db

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
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Home', response.data)

if __name__ == '__main__':
    unittest.main()
