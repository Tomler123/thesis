import unittest
from flask import url_for
from flask_testing import TestCase
from main_app_folder import create_app, db
from main_app_folder.models.outcomes import Outcome
from main_app_folder.models.user import User

class FinanceRoutesTest(TestCase):

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

    def test_incomes_page(self):
        self.login()
        response = self.client.get(url_for('finance.incomes'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Incomes', response.data)

    def test_add_income(self):
        self.login()
        response = self.client.post(url_for('finance.add_income'), data={
            'name': 'Salary',
            'cost': 1000,
            'day': 15,
            'csrf_token': ''
        })
        self.assertEqual(response.status_code, 302)
        income = Outcome.query.filter_by(Name='Salary').first()
        self.assertIsNotNone(income)
        self.assertEqual(income.Cost, 1000)

    def test_edit_income(self):
        self.login()
        income = Outcome(UserID=self.user.UserID, Name='Salary', Cost=1000, Day=15, Type='Income')
        db.session.add(income)
        db.session.commit()
        response = self.client.post(url_for('finance.edit_income', income_id=income.ID), data={
            'name': 'Updated Salary',
            'cost': 1200,
            'day': 20,
            'csrf_token': ''
        })
        self.assertEqual(response.status_code, 302)
        updated_income = db.session.get(Outcome, income.ID)
        self.assertEqual(updated_income.Name, 'Updated Salary')
        self.assertEqual(updated_income.Cost, 1200)
        self.assertEqual(updated_income.Day, 20)

    def test_delete_income(self):
        self.login()
        income = Outcome(UserID=self.user.UserID, Name='Salary', Cost=1000, Day=15, Type='Income')
        db.session.add(income)
        db.session.commit()
        response = self.client.post(url_for('finance.delete_income', income_id=income.ID))
        self.assertEqual(response.status_code, 302)
        deleted_income = db.session.get(Outcome, income.ID)
        self.assertIsNone(deleted_income)

    def test_savings_page(self):
        self.login()
        response = self.client.get(url_for('finance.savings'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Savings', response.data)

    def test_add_saving(self):
        self.login()
        response = self.client.post(url_for('finance.add_saving'), data={
            'name': 'Emergency Fund',
            'cost': 500,
            'csrf_token': ''
        })
        self.assertEqual(response.status_code, 302)
        saving = Outcome.query.filter_by(Name='Emergency Fund').first()
        self.assertIsNotNone(saving)
        self.assertEqual(saving.Cost, 500)

    def test_edit_saving(self):
        self.login()
        saving = Outcome(UserID=self.user.UserID, Name='Emergency Fund', Cost=500, Type='Saving')
        db.session.add(saving)
        db.session.commit()
        response = self.client.post(url_for('finance.edit_savings', saving_id=saving.ID), data={
            'name': 'Updated Emergency Fund',
            'cost': 700,
            'csrf_token': ''
        })
        self.assertEqual(response.status_code, 302)
        updated_saving = db.session.get(Outcome, saving.ID)
        self.assertEqual(updated_saving.Name, 'Updated Emergency Fund')
        self.assertEqual(updated_saving.Cost, 700)

    def test_delete_saving(self):
        self.login()
        saving = Outcome(UserID=self.user.UserID, Name='Emergency Fund', Cost=500, Type='Saving')
        db.session.add(saving)
        db.session.commit()
        response = self.client.post(url_for('finance.delete_saving', saving_id=saving.ID))
        self.assertEqual(response.status_code, 302)
        deleted_saving = db.session.get(Outcome, saving.ID)
        self.assertIsNone(deleted_saving)

    def test_outcomes_page(self):
        self.login()
        response = self.client.get(url_for('finance.outcomes'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Outcomes', response.data)

    def test_add_outcome(self):
        self.login()
        response = self.client.post(url_for('finance.add_outcome'), data={
            'name': 'Groceries',
            'cost': 150,
            'day': 5,
            'type': 'Expense',
            'csrf_token': ''
        })
        self.assertEqual(response.status_code, 302)
        outcome = Outcome.query.filter_by(Name='Groceries').first()
        self.assertIsNotNone(outcome)
        self.assertEqual(outcome.Cost, 150)

    def test_edit_outcome(self):
        self.login()
        outcome = Outcome(UserID=self.user.UserID, Name='Groceries', Cost=150, Day=5, Type='Expense')
        db.session.add(outcome)
        db.session.commit()
        response = self.client.post(url_for('finance.edit_outcome', outcome_id=outcome.ID), data={
            'name': 'Updated Groceries',
            'cost': 200,
            'day': 10,
            'type': 'Expense',
            'csrf_token': ''
        })
        self.assertEqual(response.status_code, 302)
        updated_outcome = db.session.get(Outcome, outcome.ID)
        self.assertEqual(updated_outcome.Name, 'Updated Groceries')
        self.assertEqual(updated_outcome.Cost, 200)
        self.assertEqual(updated_outcome.Day, 10)

    def test_delete_outcome(self):
        self.login()
        outcome = Outcome(UserID=self.user.UserID, Name='Groceries', Cost=150, Day=5, Type='Expense')
        db.session.add(outcome)
        db.session.commit()
        response = self.client.post(url_for('finance.delete_outcome', outcome_id=outcome.ID))
        self.assertEqual(response.status_code, 302)
        deleted_outcome = db.session.get(Outcome, outcome.ID)
        self.assertIsNone(deleted_outcome)

if __name__ == '__main__':
    unittest.main()
