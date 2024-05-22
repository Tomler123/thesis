import unittest
from flask import url_for
from main_app_folder import create_app, db
from main_app_folder.models.user import User
from main_app_folder.models.transactions import Transaction
import datetime

class TransactionsRoutesTest(unittest.TestCase):

    def create_app(self):
        app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SESSION_TYPE': 'filesystem',
            'SECRET_KEY': 'test_secret_key',
            'SERVER_NAME': 'localhost.localdomain'
        })
        return app

    def setUp(self):
        self.app = self.create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.user = User(Name='Test', LastName='User', Email='test@example.com', Password='testpass')
        db.session.add(self.user)
        db.session.commit()
        self.client = self.app.test_client()
        self.login()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def login(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user.UserID

    def test_add_transaction(self):
        response = self.client.post(url_for('transactions.add_transaction'), data={
            'amount': 100,
            'date': '2023-05-17',
            'category': 'Test Category',
            'description': 'Test Description'
        }, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get('message'), 'Transaction added successfully!')

    def test_edit_transaction(self):
        transaction = Transaction(UserID=self.user.UserID, Amount=100, Date=datetime.date(2023, 5, 17), Category='Test Category', Description='Test Description')
        db.session.add(transaction)
        db.session.commit()

        response = self.client.post(url_for('transactions.edit_transaction', transaction_id=transaction.TransactionID), data={
            'amount': 200,
            'date': '2023-06-17',
            'category': 'Updated Category',
            'description': 'Updated Description'
        }, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get('message'), 'Transaction updated successfully!')

    def test_delete_transaction(self):
        transaction = Transaction(UserID=self.user.UserID, Amount=100, Date=datetime.date(2023, 5, 17), Category='Test Category', Description='Test Description')
        db.session.add(transaction)
        db.session.commit()

        response = self.client.post(url_for('transactions.delete_transaction', transaction_id=transaction.TransactionID), headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json.get('message'), 'Transaction deleted successfully!')
        deleted_transaction = Transaction.query.get(transaction.TransactionID)
        self.assertIsNone(deleted_transaction)

    def test_view_transactions(self):
        # Add test data
        transactions = [
            Transaction(UserID=self.user.UserID, Amount=100, Date=datetime.date(2023, 5, 17), Category='Test Category', Description='Test Description'),
            Transaction(UserID=self.user.UserID, Amount=200, Date=datetime.date(2023, 6, 17), Category='Another Category', Description='Another Description')
        ]
        db.session.bulk_save_objects(transactions)
        db.session.commit()

        response = self.client.get(url_for('transactions.transactions'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Category', response.data)
        self.assertIn(b'Another Category', response.data)

    def test_view_transactions_not_logged_in(self):
        self.client.get(url_for('auth.logout'))  # Log out the user
        response = self.client.get(url_for('transactions.transactions'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_edit_non_existing_transaction(self):
        response = self.client.post(url_for('transactions.edit_transaction', transaction_id=9999), data={
            'amount': 200,
            'date': '2023-06-17',
            'category': 'Updated Category',
            'description': 'Updated Description'
        }, headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json.get('message'), 'Transaction not found.')

    def test_delete_non_existing_transaction(self):
        response = self.client.post(url_for('transactions.delete_transaction', transaction_id=9999), headers={'Accept': 'application/json'})
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json.get('message'), 'Transaction not found or you do not have permission to delete it.')

if __name__ == '__main__':
    unittest.main()