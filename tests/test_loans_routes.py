import unittest
from flask import url_for
from flask_testing import TestCase
from main_app_folder import create_app, db
from main_app_folder.models.loans import Loan
from main_app_folder.models.user import User

class LoansRoutesTest(TestCase):

    def create_app(self):
        app = create_app({
            'TESTING': True,
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'WTF_CSRF_ENABLED': False,
            'SESSION_TYPE': 'filesystem',
            'SECRET_KEY': 'test_secret_key'
        })
        return app

    def setUp(self):
        db.create_all()
        self.user = User(Name='Test', LastName='User', Email='test@example.com', Password='testpass')
        db.session.add(self.user)
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def login(self):
        with self.client.session_transaction() as session:
            session['user_id'] = self.user.UserID

    def test_loans_page(self):
        self.login()
        response = self.client.get(url_for('loans.loans'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Loans', response.data)

    def test_add_loan(self):
        self.login()
        response = self.client.post(url_for('loans.add_loan'), data={
            'lender_name': 'Test Lender',
            'loan_amount': 1000,
            'interest_rate': 5.0,
            'monthly_payment': 100,
            'start_date': '2024-01-01',
            'due_date': '2025-01-01',
            'remaining_balance': 500,
            'is_borrower': '1',
            'notes': 'Test notes',
            'csrf_token': ''
        })
        self.assertEqual(response.status_code, 302)
        loan = Loan.query.filter_by(LenderName='Test Lender').first()
        self.assertIsNotNone(loan)
        self.assertEqual(loan.LoanAmount, 1000)

    def test_edit_loan(self):
        self.login()
        loan = Loan(
            UserID=self.user.UserID, LenderName='Test Lender', LoanAmount=1000,
            InterestRate=5.0, MonthlyPayment=100, StartDate='2024-01-01',
            DueDate='2025-01-01', RemainingBalance=500, IsBorrower=True, Notes='Test notes'
        )
        db.session.add(loan)
        db.session.commit()
        response = self.client.post(url_for('loans.edit_loan', loan_id=loan.LoanID), data={
            'lender_name': 'Updated Lender',
            'loan_amount': 1200,
            'interest_rate': 4.5,
            'monthly_payment': 150,
            'start_date': '2024-02-01',
            'due_date': '2025-02-01',
            'remaining_balance': 700,
            'is_borrower': '1',
            'notes': 'Updated notes',
            'csrf_token': ''
        })
        self.assertEqual(response.status_code, 302)
        updated_loan = db.session.get(Loan, loan.LoanID)
        self.assertEqual(updated_loan.LenderName, 'Updated Lender')
        self.assertEqual(updated_loan.LoanAmount, 1200)

    def test_delete_loan(self):
        self.login()
        loan = Loan(
            UserID=self.user.UserID, LenderName='Test Lender', LoanAmount=1000,
            InterestRate=5.0, MonthlyPayment=100, StartDate='2024-01-01',
            DueDate='2025-01-01', RemainingBalance=500, IsBorrower=True, Notes='Test notes'
        )
        db.session.add(loan)
        db.session.commit()
        response = self.client.post(url_for('loans.delete_loan', loan_id=loan.LoanID))
        self.assertEqual(response.status_code, 302)
        deleted_loan = db.session.get(Loan, loan.LoanID)
        self.assertIsNone(deleted_loan)

if __name__ == '__main__':
    unittest.main()
