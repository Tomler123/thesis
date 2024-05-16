import unittest
from main_app_folder.models.user import User
from main_app_folder.models.outcomes import Outcome
from tests.base_test import BaseTestCase

class UserModelTestCase(BaseTestCase):

    def test_create_user(self):
        session = self.Session()
        user = User(Name='Test', LastName='User', Email='test@example.com', Password='testpass')
        session.add(user)
        session.commit()

        # Retrieve the user
        retrieved_user = session.query(User).filter_by(Email='test@example.com').first()
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.Name, 'Test')
        self.assertEqual(retrieved_user.LastName, 'User')
        session.close()

    def test_create_outcome(self):
        session = self.Session()
        user = User(Name='Test', LastName='User', Email='test@example.com', Password='testpass')
        session.add(user)
        session.commit()

        outcome = Outcome(UserID=user.UserID, Name='Test Outcome', Cost=100.0, Day=15, Type='Income')
        session.add(outcome)
        session.commit()

        # Retrieve the outcome
        retrieved_outcome = session.query(Outcome).filter_by(Name='Test Outcome').first()
        self.assertIsNotNone(retrieved_outcome)
        self.assertEqual(retrieved_outcome.Cost, 100.0)
        self.assertEqual(retrieved_outcome.UserID, user.UserID)
        session.close()

if __name__ == '__main__':
    unittest.main()
