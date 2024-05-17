import unittest
from unittest.mock import MagicMock, patch
from main_app_folder.routes.loans_routes import handle_get_loans, handle_add_loan, handle_edit_loan, handle_delete_loan
from main_app_folder.models.loans import Loan
from flask import Flask
from main_app_folder import create_app, db
from main_app_folder.models.user import User

class TestLoansLogic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test_secret_key'
        })
        with cls.app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        with cls.app.app_context():
            db.session.remove()
            db.drop_all()

    def setUp(self):
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch('main_app_folder.routes.loans_routes.Loan.query')
    @patch('main_app_folder.routes.loans_routes.functions.loans_pie_chart')
    @patch('main_app_folder.routes.loans_routes.render_template')
    def test_handle_get_loans(self, mock_render_template, mock_loans_pie_chart, mock_query):
        # Mock data
        mock_query.filter_by.return_value.all.side_effect = [
            [
                Loan(UserID=1, LenderName='Bank A', LoanAmount=1000.0, IsBorrower=True),
                Loan(UserID=1, LenderName='Bank B', LoanAmount=2000.0, IsBorrower=True)
            ],
            [
                Loan(UserID=1, LenderName='Person A', LoanAmount=500.0, IsBorrower=False),
                Loan(UserID=1, LenderName='Person B', LoanAmount=1500.0, IsBorrower=False)
            ]
        ]

        user = User(UserID=1, Name='Test', LastName='User', Email='test@example.com', Password='testpass')
        result = handle_get_loans(user)

        # Assertions
        mock_query.filter_by.assert_any_call(UserID=1, IsBorrower=True)
        mock_query.filter_by.assert_any_call(UserID=1, IsBorrower=False)
        mock_render_template.assert_called_once()
        args, kwargs = mock_render_template.call_args
        self.assertEqual(args[0], 'loans.html')
        self.assertIn('borrowed_loans', kwargs)
        self.assertIn('lent_loans', kwargs)
        self.assertIn('lent_loans_pie_chart_img', kwargs)
        self.assertIn('borrowed_loans_pie_chart_img', kwargs)
        self.assertIn('total_borrowed_loans', kwargs)
        self.assertIn('total_lent_loans', kwargs)
        self.assertEqual(kwargs['total_borrowed_loans'], 3000.0)
        self.assertEqual(kwargs['total_lent_loans'], 2000.0)

    @patch('main_app_folder.routes.loans_routes.db.session')
    @patch('main_app_folder.routes.loans_routes.flash')
    @patch('main_app_folder.routes.loans_routes.redirect')
    @patch('main_app_folder.routes.loans_routes.url_for')
    def test_handle_add_loan(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        new_loan = Loan(UserID=1, LenderName='Bank C', LoanAmount=3000.0, InterestRate=3.5, MonthlyPayment=300.0, StartDate='2023-01-01', DueDate='2025-01-01', RemainingBalance=2500.0, IsBorrower=True, Notes='Test note')

        # Call the function
        result = handle_add_loan(new_loan)

        # Assertions
        mock_session.add.assert_called_once_with(new_loan)
        mock_session.commit.assert_called_once()
        mock_flash.assert_called_once_with('Loan added successfully!')
        mock_redirect.assert_called_once_with(mock_url_for('loans'))

    @patch('main_app_folder.routes.loans_routes.db.session')
    @patch('main_app_folder.routes.loans_routes.flash')
    @patch('main_app_folder.routes.loans_routes.redirect')
    @patch('main_app_folder.routes.loans_routes.url_for')
    def test_handle_edit_loan(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        loan = Loan(UserID=1, LenderName='Bank A', LoanAmount=1000.0, InterestRate=3.5, MonthlyPayment=100.0, StartDate='2023-01-01', DueDate='2025-01-01', RemainingBalance=800.0, IsBorrower=True, Notes='Test note')
        form = MagicMock()
        form.lender_name.data = 'Updated Bank'
        form.loan_amount.data = 1500.0
        form.interest_rate.data = 4.0
        form.monthly_payment.data = 150.0
        form.start_date.data = '2023-02-01'
        form.due_date.data = '2025-02-01'
        form.remaining_balance.data = 1200.0
        form.is_borrower.data = '1'
        form.notes.data = 'Updated note'

        # Call the function
        result = handle_edit_loan(loan, form)

        # Assertions
        self.assertEqual(loan.LenderName, 'Updated Bank')
        self.assertEqual(loan.LoanAmount, 1500.0)
        self.assertEqual(loan.InterestRate, 4.0)
        self.assertEqual(loan.MonthlyPayment, 150.0)
        self.assertEqual(loan.StartDate, '2023-02-01')
        self.assertEqual(loan.DueDate, '2025-02-01')
        self.assertEqual(loan.RemainingBalance, 1200.0)
        self.assertEqual(loan.IsBorrower, True)
        self.assertEqual(loan.Notes, 'Updated note')
        mock_session.commit.assert_called_once()
        mock_flash.assert_called_once_with('Loan updated successfully!')
        mock_redirect.assert_called_once_with(mock_url_for('loans'))

    @patch('main_app_folder.routes.loans_routes.db.session')
    @patch('main_app_folder.routes.loans_routes.flash')
    @patch('main_app_folder.routes.loans_routes.redirect')
    @patch('main_app_folder.routes.loans_routes.url_for')
    def test_handle_delete_loan(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        loan = Loan(UserID=1, LenderName='Bank A', LoanAmount=1000.0, InterestRate=3.5, MonthlyPayment=100.0, StartDate='2023-01-01', DueDate='2025-01-01', RemainingBalance=800.0, IsBorrower=True, Notes='Test note')

        # Call the function
        result = handle_delete_loan(loan)

        # Assertions
        mock_session.delete.assert_called_once_with(loan)
        mock_session.commit.assert_called_once()
        mock_flash.assert_called_once_with('Loan deleted successfully!')
        mock_redirect.assert_called_once_with(mock_url_for('loans'))

    @patch('main_app_folder.routes.loans_routes.Loan.query')
    @patch('main_app_folder.routes.loans_routes.functions.loans_pie_chart')
    @patch('main_app_folder.routes.loans_routes.render_template')
    def test_handle_get_loans_no_loans(self, mock_render_template, mock_loans_pie_chart, mock_query):
        # Mock data
        mock_query.filter_by.return_value.all.return_value = []

        user = User(UserID=1, Name='Test', LastName='User', Email='test@example.com', Password='testpass')
        result = handle_get_loans(user)

        # Assertions
        mock_query.filter_by.assert_any_call(UserID=1, IsBorrower=True)
        mock_query.filter_by.assert_any_call(UserID=1, IsBorrower=False)
        mock_render_template.assert_called_once()
        args, kwargs = mock_render_template.call_args
        self.assertEqual(args[0], 'loans.html')
        self.assertIn('borrowed_loans', kwargs)
        self.assertIn('lent_loans', kwargs)
        self.assertIn('lent_loans_pie_chart_img', kwargs)
        self.assertIn('borrowed_loans_pie_chart_img', kwargs)
        self.assertIn('total_borrowed_loans', kwargs)
        self.assertIn('total_lent_loans', kwargs)
        self.assertEqual(kwargs['total_borrowed_loans'], 0.0)
        self.assertEqual(kwargs['total_lent_loans'], 0.0)

    # test_handle_add_loan_invalid_data
    @patch('main_app_folder.routes.loans_routes.db.session')
    @patch('main_app_folder.routes.loans_routes.flash')
    @patch('main_app_folder.routes.loans_routes.render_template')
    def test_handle_add_loan_invalid_data(self, mock_render_template, mock_flash, mock_session):
        # Mock data
        invalid_loan = Loan(UserID=1, LenderName='', LoanAmount=-1000.0, InterestRate=0.0, MonthlyPayment=0.0, StartDate='2023-01-01', DueDate='2025-01-01', RemainingBalance=0.0, IsBorrower=True, Notes='')

        with self.app.test_request_context():
            # Call the function
            result = handle_add_loan(invalid_loan)

            # Assertions
            mock_session.add.assert_not_called()
            mock_session.commit.assert_not_called()
            mock_flash.assert_called_once_with('Invalid loan data. Please check the details and try again.')
            mock_render_template.assert_called_once_with('add_loan.html', form=invalid_loan)



    # test_handle_edit_loan_no_changes
    @patch('main_app_folder.routes.loans_routes.db.session')
    @patch('main_app_folder.routes.loans_routes.flash')
    @patch('main_app_folder.routes.loans_routes.redirect')
    @patch('main_app_folder.routes.loans_routes.url_for')
    def test_handle_edit_loan_no_changes(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        loan = Loan(UserID=1, LenderName='Bank A', LoanAmount=1000.0, InterestRate=3.5, MonthlyPayment=100.0, StartDate='2023-01-01', DueDate='2025-01-01', RemainingBalance=800.0, IsBorrower=True, Notes='Test note')
        form = MagicMock()
        form.lender_name.data = 'Bank A'
        form.loan_amount.data = 1000.0
        form.interest_rate.data = 3.5
        form.monthly_payment.data = 100.0
        form.start_date.data = '2023-01-01'
        form.due_date.data = '2025-01-01'
        form.remaining_balance.data = 800.0
        form.is_borrower.data = '1'
        form.notes.data = 'Test note'

        # Call the function
        result = handle_edit_loan(loan, form)

        # Assertions
        mock_session.commit.assert_called_once()
        mock_flash.assert_called_once_with('Loan updated successfully!')
        mock_redirect.assert_called_once_with(mock_url_for('loans'))

    # test_handle_delete_loan_not_found
    @patch('main_app_folder.routes.loans_routes.db.session')
    @patch('main_app_folder.routes.loans_routes.flash')
    @patch('main_app_folder.routes.loans_routes.redirect')
    @patch('main_app_folder.routes.loans_routes.url_for')
    def test_handle_delete_loan_not_found(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        loan = None

        with self.app.test_request_context():
            # Call the function
            result = handle_delete_loan(loan)

            # Assertions
            mock_session.delete.assert_not_called()
            mock_session.commit.assert_not_called()
            mock_flash.assert_called_once_with('Loan not found or you do not have permission to delete it.')
            mock_redirect.assert_called_once_with(mock_url_for('loans'))

    # test_handle_add_loan_valid_data
    @patch('main_app_folder.routes.loans_routes.db.session')
    @patch('main_app_folder.routes.loans_routes.flash')
    @patch('main_app_folder.routes.loans_routes.redirect')
    @patch('main_app_folder.routes.loans_routes.url_for')
    def test_handle_add_loan_valid_data(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        new_loan = Loan(UserID=1, LenderName='Bank B', LoanAmount=5000.0, InterestRate=4.5, MonthlyPayment=200.0, StartDate='2023-02-01', DueDate='2026-02-01', RemainingBalance=5000.0, IsBorrower=True, Notes='New loan')

        with self.app.test_request_context():
            # Call the function
            result = handle_add_loan(new_loan)

            # Assertions
            mock_session.add.assert_called_once_with(new_loan)
            mock_session.commit.assert_called_once()
            mock_flash.assert_called_once_with('Loan added successfully!')
            mock_redirect.assert_called_once_with(mock_url_for('loans'))


if __name__ == '__main__':
    unittest.main()
