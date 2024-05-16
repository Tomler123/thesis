import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from main_app_folder import create_app, db as db_instance

class BaseTestCase(unittest.TestCase):

    def setUp(self):
        # Set up an in-memory SQLite database
        self.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test_secret_key'
        })
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.engine = create_engine('sqlite:///:memory:')
        db_instance.metadata.create_all(self.engine)
        self.Session = scoped_session(sessionmaker(bind=self.engine))

    def tearDown(self):
        db_instance.session.remove()
        db_instance.metadata.drop_all(self.engine)
        self.app_context.pop()
