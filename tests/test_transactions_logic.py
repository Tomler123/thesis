# import unittest
# from unittest.mock import MagicMock, patch
# from main_app_folder.routes.transactions import handle_get_transactions, handle_add_transaction, handle_edit_transaction, handle_delete_transaction
# from main_app_folder.models.transactions import Transaction
# from flask import Flask
# from main_app_folder import create_app, db

# class TestTransactionsLogic(unittest.TestCase):

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
#         self.app_context = self.app.app_context()
#         self.app_context.push()

#     def tearDown(self):
#         self.app_context.pop()

#     @patch('main_app_folder.routes.transactions.Transaction.query')
#     @patch('main_app_folder.routes.transactions.render_template')
#     def test_handle_get_transactions(self, mock_render_template, mock_query):
#         # Mock data
#         mock_query.filter_by.return_value.order_by.return_value.all.return_value = [
#             Transaction(UserID=1, Amount=100.0, Date='2023-01-01', Category='Food', Description='Groceries'),
#             Transaction(UserID=1, Amount=50.0, Date='2023-01-02', Category='Transport', Description='Bus ticket')
#         ]
        
#         # Call the function
#         result = handle_get_transactions(1)
        
#         # Assertions
#         mock_query.filter_by.assert_called_with(UserID=1)
#         mock_render_template.assert_called_once()
#         args, kwargs = mock_render_template.call_args
#         self.assertEqual(args[0], 'transactions.html')
#         self.assertIn('transactions', kwargs)
#         self.assertEqual(len(kwargs['transactions']), 2)

#     @patch('main_app_folder.routes.transactions.db.session')
#     @patch('main_app_folder.routes.transactions.flash')
#     @patch('main_app_folder.routes.transactions.redirect')
#     @patch('main_app_folder.routes.transactions.url_for')
#     def test_handle_add_transaction(self, mock_url_for, mock_redirect, mock_flash, mock_session):
#         # Mock data
#         new_transaction = Transaction(UserID=1, Amount=200.0, Date='2023-01-03', Category='Entertainment', Description='Movies')

#         # Call the function
#         result = handle_add_transaction(new_transaction)

#         # Assertions
#         mock_session.add.assert_called_once_with(new_transaction)
#         mock_session.commit.assert_called_once()
#         mock_flash.assert_called_once_with('Transaction added successfully!')
#         mock_redirect.assert_called_once_with(mock_url_for('transactions'))

#     @patch('main_app_folder.routes.transactions.db.session')
#     @patch('main_app_folder.routes.transactions.flash')
#     @patch('main_app_folder.routes.transactions.redirect')
#     @patch('main_app_folder.routes.transactions.url_for')
#     def test_handle_edit_transaction(self, mock_url_for, mock_redirect, mock_flash, mock_session):
#         # Mock data
#         transaction = Transaction(UserID=1, Amount=100.0, Date='2023-01-01', Category='Food', Description='Groceries')
#         form = MagicMock()
#         form.amount.data = 150.0
#         form.date.data = '2023-01-02'
#         form.category.data = 'Transport'
#         form.description.data = 'Bus ticket'

#         # Call the function
#         result = handle_edit_transaction(transaction, form)

#         # Assertions
#         self.assertEqual(transaction.Amount, 150.0)
#         self.assertEqual(transaction.Date, '2023-01-02')
#         self.assertEqual(transaction.Category, 'Transport')
#         self.assertEqual(transaction.Description, 'Bus ticket')
#         mock_session.commit.assert_called_once()
#         mock_flash.assert_called_once_with('Transaction updated successfully!')
#         mock_redirect.assert_called_once_with(mock_url_for('transactions'))

#     @patch('main_app_folder.routes.transactions.db.session')
#     @patch('main_app_folder.routes.transactions.flash')
#     @patch('main_app_folder.routes.transactions.redirect')
#     @patch('main_app_folder.routes.transactions.url_for')
#     def test_handle_delete_transaction(self, mock_url_for, mock_redirect, mock_flash, mock_session):
#         # Mock data
#         transaction = Transaction(UserID=1, Amount=100.0, Date='2023-01-01', Category='Food', Description='Groceries')

#         # Call the function
#         result = handle_delete_transaction(transaction)

#         # Assertions
#         mock_session.delete.assert_called_once_with(transaction)
#         mock_session.commit.assert_called_once()
#         mock_flash.assert_called_once_with('Transaction deleted successfully!')
#         mock_redirect.assert_called_once_with(mock_url_for('transactions'))

#     @patch('main_app_folder.routes.transactions.db.session')
#     @patch('main_app_folder.routes.transactions.flash')
#     @patch('main_app_folder.routes.transactions.redirect')
#     @patch('main_app_folder.routes.transactions.url_for')
#     def test_handle_delete_transaction_not_found(self, mock_url_for, mock_redirect, mock_flash, mock_session):
#         # Mock data
#         transaction = None

#         # Call the function
#         result = handle_delete_transaction(transaction)

#         # Assertions
#         mock_session.delete.assert_not_called()
#         mock_session.commit.assert_not_called()
#         mock_flash.assert_called_once_with('Transaction not found or you do not have permission to delete it.')
#         mock_redirect.assert_called_once_with(mock_url_for('transactions'))

# if __name__ == '__main__':
#     unittest.main()
