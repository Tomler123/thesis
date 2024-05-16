from flask import jsonify, redirect, request, render_template, url_for, session, flash, session
import datetime
import json
from sqlalchemy import func, extract

from main_app_folder.utils import helpers
from main_app_folder.forms import forms
from main_app_folder.models.transactions import Transaction
from main_app_folder.models.outcomes import Outcome
from main_app_folder.ai_algorithms import transaction_algo
from main_app_folder import db

def init_app(app):
    @app.route('/transactions')
    def transactions():
        if 'user_id' not in session:
            flash('Please log in to view your transactions.')
            return redirect(url_for('login'))

        try:
            user_id = session['user_id']
            transactions = Transaction.query.filter_by(UserID=user_id).order_by(Transaction.Date.desc()).all()
            return render_template('transactions.html', transactions=transactions)
        except Exception as e:
            flash('An error occurred while fetching transactions.')
            return render_template('transactions.html', transactions=[])

    @app.route('/add_transaction', methods=['GET', 'POST'])
    def add_transaction():
        if 'user_id' not in session:
            flash('Please log in to add a transaction.')
            return redirect(url_for('login'))

        form = forms.TransactionForm()

        if request.method == 'GET':
            form.date.data = datetime.date.today()
            form.amount.data = 0

        if form.validate_on_submit():
            try:
                new_transaction = Transaction(
                    UserID=session['user_id'],
                    Amount=form.amount.data,
                    Date=form.date.data,
                    Category=form.category.data,
                    Description=form.description.data
                )
                db.session.add(new_transaction)
                db.session.commit()
                flash('Transaction added successfully!')
                return redirect(url_for('transactions'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while adding the transaction. Please try again.')
                
        return render_template('add_transaction.html', form=form)

    @app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
    def edit_transaction(transaction_id):
        if 'user_id' not in session:
            flash('Please log in to edit a transaction.')
            return redirect(url_for('login'))

        transaction = Transaction.query.filter_by(TransactionID=transaction_id, UserID=session['user_id']).first()
        if not transaction:
            flash('Transaction not found.')
            return redirect(url_for('transactions'))

        form = forms.TransactionForm(obj=transaction)

        if request.method == 'POST' and form.validate_on_submit():
            try:
                transaction.Amount = form.amount.data
                transaction.Date = form.date.data
                transaction.Category = form.category.data
                transaction.Description = form.description.data
                db.session.commit()
                flash('Transaction updated successfully!')
                return redirect(url_for('transactions'))
            except Exception as e:
                db.session.rollback()
                flash('An error occurred while updating the transaction. Please try again.')
        else:
            # Manually populate the form fields with the transaction data
            form.amount.data = transaction.Amount
            form.date.data = transaction.Date
            form.category.data = transaction.Category
            form.description.data = transaction.Description

        return render_template('edit_transaction.html', form=form, transaction_id=transaction_id)

    @app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
    def delete_transaction(transaction_id):
        if 'user_id' not in session:
            flash('Please log in to delete a transaction.')
            return redirect(url_for('login'))

        transaction = Transaction.query.filter_by(TransactionID=transaction_id, UserID=session['user_id']).first()
        if not transaction:
            flash('Transaction not found or you do not have permission to delete it.')
            return redirect(url_for('transactions'))

        try:
            db.session.delete(transaction)
            db.session.commit()
            flash('Transaction deleted successfully!')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while deleting the transaction. Please try again.')

        return redirect(url_for('transactions'))

    @app.route('/predict_next_month', methods=['GET'])
    def predict_next_month():
        if 'user_id' not in session:
            return json.dumps({'success': False, 'message': 'User not logged in'}), 401

        user_id = session['user_id']
        conn = helpers.get_db_connection()
        cursor = conn.cursor()

        # Get the earliest transaction date
        cursor.execute("SELECT MIN(Date) FROM transactions WHERE UserID = ?", user_id)
        min_date_row = cursor.fetchone()
        if not min_date_row or not min_date_row[0]:
            return json.dumps({'success': False, 'message': 'No transactions found.'}), 404
        
        total_income = db.session.query(func.sum(Outcome.Cost)).filter(Outcome.UserID == user_id, Outcome.Type == 'Income').scalar() or 0
        # Calculate the number of months since the earliest transaction
        earliest_date = min_date_row[0]
        months_count = (datetime.date.today().year - earliest_date.year) * 12 + (datetime.date.today().month - earliest_date.month + 1)
        
        # Prepare month labels and sums
        months = list(map(str, range(1, months_count + 1)))
        sums = [0] * months_count  # Default sums to zero

        # Iterate over each month since the earliest transaction and calculate sums
        for i in range(months_count):
            month = (earliest_date.month - 1 + i) % 12 + 1
            year = earliest_date.year + ((earliest_date.month - 1 + i) // 12)
            monthly_sum = db.session.query(func.sum(Transaction.Amount)).filter(Transaction.UserID == user_id, extract('year', Transaction.Date) == year, extract('month', Transaction.Date) == month).scalar()
            sums[i] = float(monthly_sum or 0)
        cursor.close()
        conn.close()

        # Convert months and sums to space-separated strings
        month_str = ' '.join(map(str, months))
        sum_str = ' '.join(map(lambda x: f"{x:.1f}", sums))  # Format floats to one decimal place

        # Call your prediction algorithm
        try:
            # Assuming your function can take lists of months and their corresponding sums
            prediction = transaction_algo.main(month_str, sum_str)

            return json.dumps({
                'success': True, 
                'prediction': float(prediction), 
                'total_income': total_income
            }), 200
        except Exception as e:
            return json.dumps({'success': False, 'message': str(e)}), 500