# import unittest
# from unittest.mock import patch, MagicMock
# from flask import session
# from main_app_folder import create_app, db
# from main_app_folder.models.user import User

# class TestRecommendations(unittest.TestCase):

#     @classmethod
#     def setUpClass(cls):
#         cls.app = create_app({
#             'TESTING': True,
#             'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
#             'WTF_CSRF_ENABLED': False,
#             'SECRET_KEY': 'test_secret_key'
#         })
#         with cls.app.app_context():
#             db.create_all()

#     @classmethod
#     def tearDownClass(cls):
#         with cls.app.app_context():
#             db.session.remove()
#             db.drop_all()

#     def setUp(self):
#         self.client = self.app.test_client()
#         self.app_context = self.app.app_context()
#         self.app_context.push()
#         with self.app.app_context():
#             user = User(Name='Test', LastName='User', Email='test@example.com', Password='testpassword')
#             db.session.add(user)
#             db.session.commit()
#             self.user_id = user.UserID

#     def tearDown(self):
#         with self.app.app_context():
#             db.session.query(User).delete()
#             db.session.commit()
#         self.app_context.pop()

#     def login(self):
#         with self.client.session_transaction() as sess:
#             sess['user_id'] = self.user_id

#     @patch('main_app_folder.utils.helpers.get_db_connection')
#     def test_access_recommendations_not_logged_in(self, mock_get_db_connection):
#         response = self.client.get('/recommendations', follow_redirects=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn(b'Log In', response.data)

#     @patch('main_app_folder.utils.helpers.get_db_connection')
#     def test_access_recommendations_logged_in(self, mock_get_db_connection):
#         self.login()
#         mock_conn = MagicMock()
#         mock_cursor = MagicMock()
#         mock_get_db_connection.return_value = mock_conn
#         mock_conn.cursor.return_value = mock_cursor

#         response = self.client.get('/recommendations')
#         self.assertEqual(response.status_code, 200)
#         self.assertIn(b'recommendations', response.data)

# if __name__ == '__main__':
#     unittest.main()
