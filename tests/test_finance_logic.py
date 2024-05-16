import unittest
from unittest.mock import MagicMock, patch
from collections import namedtuple
from main_app_folder.routes.finance_routes import (
    handle_get_incomes, handle_add_income, handle_edit_income, handle_delete_income,
    handle_get_savings, handle_add_saving, handle_edit_saving, handle_delete_saving,
    handle_get_outcomes, handle_add_outcome, handle_edit_outcome, handle_delete_outcome
)
from main_app_folder.models.outcomes import Outcome
from flask import Flask
from main_app_folder import create_app, db

class TestFinanceLogic(unittest.TestCase):

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

    @patch('main_app_folder.routes.finance_routes.Outcome.query')
    @patch('main_app_folder.routes.finance_routes.render_template')
    def test_handle_get_incomes(self, mock_render_template, mock_query):
        # Mock data
        mock_query.filter_by.return_value.all.return_value = [
            Outcome(UserID=1, Name='Test Income 1', Cost=100.0, Day=1, Type='Income'),
            Outcome(UserID=1, Name='Test Income 2', Cost=200.0, Day=15, Type='Income')
        ]
        
        # Call the function
        result = handle_get_incomes(1)
        
        # Assertions
        mock_query.filter_by.assert_called_with(UserID=1, Type='Income')
        mock_render_template.assert_called_once()
        args, kwargs = mock_render_template.call_args
        self.assertEqual(args[0], 'incomes.html')
        self.assertIn('incomes', kwargs)
        self.assertIn('incomes_pie_chart_img', kwargs)
        self.assertIn('total_incomes', kwargs)
        self.assertEqual(kwargs['total_incomes'], 300.0)

    @patch('main_app_folder.routes.finance_routes.db.session')
    @patch('main_app_folder.routes.finance_routes.flash')
    @patch('main_app_folder.routes.finance_routes.redirect')
    @patch('main_app_folder.routes.finance_routes.url_for')
    def test_handle_add_income(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        new_income = Outcome(UserID=1, Name='Test Income 3', Cost=300.0, Day=20, Type='Income')

        # Call the function
        result = handle_add_income(new_income)

        # Assertions
        mock_session.add.assert_called_once_with(new_income)
        mock_session.commit.assert_called_once()
        mock_flash.assert_called_once_with('Income added successfully!')
        mock_redirect.assert_called_once_with(mock_url_for('incomes'))
    
    @patch('main_app_folder.routes.finance_routes.db.session')
    @patch('main_app_folder.routes.finance_routes.flash')
    @patch('main_app_folder.routes.finance_routes.redirect')
    @patch('main_app_folder.routes.finance_routes.url_for')
    def test_handle_edit_income(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        income = Outcome(UserID=1, Name='Test Income', Cost=100.0, Day=1, Type='Income')
        form = MagicMock()
        form.name.data = 'Updated Income'
        form.cost.data = 150.0
        form.day.data = 2

        # Call the function
        result = handle_edit_income(income, form)

        # Assertions
        self.assertEqual(income.Name, 'Updated Income')
        self.assertEqual(income.Cost, 150.0)
        self.assertEqual(income.Day, 2)
        mock_session.commit.assert_called_once()
        mock_flash.assert_called_once_with('Income updated successfully!')
        mock_redirect.assert_called_once_with(mock_url_for('incomes'))

    @patch('main_app_folder.routes.finance_routes.db.session')
    @patch('main_app_folder.routes.finance_routes.flash')
    @patch('main_app_folder.routes.finance_routes.redirect')
    @patch('main_app_folder.routes.finance_routes.url_for')
    def test_handle_delete_income(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        income = Outcome(UserID=1, Name='Test Income', Cost=100.0, Day=1, Type='Income')

        # Call the function
        result = handle_delete_income(income)

        # Assertions
        mock_session.delete.assert_called_once_with(income)
        mock_session.commit.assert_called_once()
        mock_flash.assert_called_once_with('Income deleted successfully!')
        mock_redirect.assert_called_once_with(mock_url_for('incomes'))

    @patch('main_app_folder.routes.finance_routes.helpers.get_db_connection')
    @patch('main_app_folder.routes.finance_routes.functions.generate_pie_chart')
    @patch('main_app_folder.routes.finance_routes.render_template')
    def test_handle_get_savings(self, mock_render_template, mock_generate_pie_chart, mock_get_db_connection):
        # Mock data
        conn = MagicMock()
        cursor = conn.cursor.return_value
        MockSaving = namedtuple('MockSaving', ['Cost'])
        cursor.fetchall.return_value = [
            MockSaving(Cost=100.0),
            MockSaving(Cost=200.0)
        ]
        mock_get_db_connection.return_value = conn

        # Call the function
        result = handle_get_savings(1)

        # Assertions
        cursor.execute.assert_called_with("SELECT * FROM outcomes WHERE UserID = ? AND Type = 'Saving'", (1,))
        mock_generate_pie_chart.assert_called_once()
        mock_render_template.assert_called_once_with(
            'saving.html',
            savings=cursor.fetchall(),
            total_savings=300.0,
            savings_pie_chart_img=mock_generate_pie_chart.return_value
        )

    @patch('main_app_folder.routes.finance_routes.db.session')
    @patch('main_app_folder.routes.finance_routes.flash')
    @patch('main_app_folder.routes.finance_routes.redirect')
    @patch('main_app_folder.routes.finance_routes.url_for')
    def test_handle_add_saving(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        new_saving = Outcome(UserID=1, Name='Test Saving 3', Cost=300.0, Type='Saving')

        # Call the function
        result = handle_add_saving(new_saving)

        # Assertions
        mock_session.add.assert_called_once_with(new_saving)
        mock_session.commit.assert_called_once()
        mock_flash.assert_called_once_with('Saving added successfully!')
        mock_redirect.assert_called_once_with(mock_url_for('savings'))
    
    @patch('main_app_folder.routes.finance_routes.db.session')
    @patch('main_app_folder.routes.finance_routes.flash')
    @patch('main_app_folder.routes.finance_routes.redirect')
    @patch('main_app_folder.routes.finance_routes.url_for')
    def test_handle_edit_saving(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        saving = Outcome(UserID=1, Name='Test Saving', Cost=100.0, Type='Saving')
        form = MagicMock()
        form.name.data = 'Updated Saving'
        form.cost.data = 150.0

        # Call the function
        result = handle_edit_saving(saving, form)

        # Assertions
        self.assertEqual(saving.Name, 'Updated Saving')
        self.assertEqual(saving.Cost, 150.0)
        mock_session.commit.assert_called_once()
        mock_flash.assert_called_once_with('Saving updated successfully!')
        mock_redirect.assert_called_once_with(mock_url_for('savings'))

    @patch('main_app_folder.routes.finance_routes.db.session')
    @patch('main_app_folder.routes.finance_routes.flash')
    @patch('main_app_folder.routes.finance_routes.redirect')
    @patch('main_app_folder.routes.finance_routes.url_for')
    def test_handle_delete_saving(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        saving = Outcome(UserID=1, Name='Test Saving', Cost=100.0, Type='Saving')

        # Call the function
        result = handle_delete_saving(saving)

        # Assertions
        mock_session.delete.assert_called_once_with(saving)
        mock_session.commit.assert_called_once()
        mock_flash.assert_called_once_with('Saving deleted successfully!')
        mock_redirect.assert_called_once_with(mock_url_for('savings'))

    @patch('main_app_folder.routes.finance_routes.Outcome.query')
    @patch('main_app_folder.routes.finance_routes.render_template')
    def test_handle_get_outcomes(self, mock_render_template, mock_query):
        # Mock data
        mock_query.filter_by.return_value.all.return_value = [
            Outcome(UserID=1, Name='Test Expense 1', Cost=100.0, Day=1, Type='Expense'),
            Outcome(UserID=1, Name='Test Subscription 1', Cost=50.0, Day=1, Type='Subscription')
        ]
        
        # Call the function
        result = handle_get_outcomes(1)
        
        # Assertions
        mock_query.filter_by.assert_called_with(UserID=1)
        mock_render_template.assert_called_once()
        args, kwargs = mock_render_template.call_args
        self.assertEqual(args[0], 'outcomes.html')
        self.assertIn('outcomes', kwargs)
        self.assertIn('expenses_pie_chart_img', kwargs)
        self.assertIn('subscriptions_pie_chart_img', kwargs)
        self.assertIn('total_expenses', kwargs)
        self.assertIn('total_subscriptions', kwargs)
        self.assertEqual(kwargs['total_expenses'], 100.0)
        self.assertEqual(kwargs['total_subscriptions'], 50.0)

    @patch('main_app_folder.routes.finance_routes.db.session')
    @patch('main_app_folder.routes.finance_routes.flash')
    @patch('main_app_folder.routes.finance_routes.redirect')
    @patch('main_app_folder.routes.finance_routes.url_for')
    def test_handle_add_outcome(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        new_outcome = Outcome(UserID=1, Name='Test Outcome 3', Cost=300.0, Day=20, Type='Expense')

        # Call the function
        result = handle_add_outcome(new_outcome)

        # Assertions
        mock_session.add.assert_called_once_with(new_outcome)
        mock_session.commit.assert_called_once()
        mock_flash.assert_called_once_with('Outcome added successfully!')
        mock_redirect.assert_called_once_with(mock_url_for('outcomes'))
    
    @patch('main_app_folder.routes.finance_routes.db.session')
    @patch('main_app_folder.routes.finance_routes.flash')
    @patch('main_app_folder.routes.finance_routes.redirect')
    @patch('main_app_folder.routes.finance_routes.url_for')
    def test_handle_edit_outcome(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        outcome = Outcome(UserID=1, Name='Test Outcome', Cost=100.0, Day=1, Type='Expense')
        form = MagicMock()
        form.name.data = 'Updated Outcome'
        form.cost.data = 150.0
        form.day.data = 2
        form.type.data = 'Subscription'

        # Call the function
        result = handle_edit_outcome(outcome, form)

        # Assertions
        self.assertEqual(outcome.Name, 'Updated Outcome')
        self.assertEqual(outcome.Cost, 150.0)
        self.assertEqual(outcome.Day, 2)
        self.assertEqual(outcome.Type, 'Subscription')
        mock_session.commit.assert_called_once()
        mock_flash.assert_called_once_with('Outcome updated successfully!')
        mock_redirect.assert_called_once_with(mock_url_for('outcomes'))

    @patch('main_app_folder.routes.finance_routes.db.session')
    @patch('main_app_folder.routes.finance_routes.flash')
    @patch('main_app_folder.routes.finance_routes.redirect')
    @patch('main_app_folder.routes.finance_routes.url_for')
    def test_handle_delete_outcome(self, mock_url_for, mock_redirect, mock_flash, mock_session):
        # Mock data
        outcome = Outcome(UserID=1, Name='Test Outcome', Cost=100.0, Day=1, Type='Expense')

        # Call the function
        result = handle_delete_outcome(outcome)

        # Assertions
        mock_session.delete.assert_called_once_with(outcome)
        mock_session.commit.assert_called_once()
        mock_flash.assert_called_once_with('Outcome deleted successfully!')
        mock_redirect.assert_called_once_with(mock_url_for('outcomes'))

if __name__ == '__main__':
    unittest.main()
