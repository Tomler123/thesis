from flask import Blueprint, jsonify, redirect, request, render_template, url_for, session, flash, current_app
import datetime
import json
from sqlalchemy import func, extract

from main_app_folder.utils import helpers
from main_app_folder.forms import forms
from main_app_folder.models.transactions import Transaction
from main_app_folder.models.outcomes import Outcome
from main_app_folder.ai_algorithms import transaction_algo
from main_app_folder.extensions import db

transactions_bp = Blueprint('transactions', __name__)

def is_testing():
    return current_app.config['TESTING']

@transactions_bp.route('/transactions')
def transactions():
    if 'user_id' not in session:
        flash('Please log in to view your transactions.', 'danger')
        return redirect(url_for('auth.login'))
    try:
        user_id = session['user_id']
        return handle_get_transactions(user_id)
    except Exception as e:
        flash('An error occurred while fetching transactions.', 'danger')
        return render_template('transactions.html', transactions=[])

@transactions_bp.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'user_id' not in session:
        flash('Please log in to add a transaction.', 'danger')
        return redirect(url_for('auth.login'))
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
            if is_testing():
                return jsonify({'message': 'Transaction added successfully!'}), 200
            flash('Transaction added successfully!', 'success')
            return redirect(url_for('transactions.transactions'))
        except Exception as e:
            db.session.rollback()
            if is_testing():
                return jsonify({'message': 'An error occurred while adding the transaction. Please try again.'}), 500
            flash('An error occurred while adding the transaction. Please try again.', 'danger')
    return render_template('add_transaction.html', form=form)

@transactions_bp.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    if 'user_id' not in session:
        flash('Please log in to edit a transaction.', 'danger')
        return redirect(url_for('auth.login'))
    transaction = Transaction.query.filter_by(TransactionID=transaction_id, UserID=session['user_id']).first()
    if not transaction:
        if is_testing():
            return jsonify({'message': 'Transaction not found.'}), 404
        flash('Transaction not found.', 'danger')
        return redirect(url_for('transactions.transactions'))
    form = forms.TransactionForm(obj=transaction)
    if request.method == 'POST' and form.validate_on_submit():
        try:
            transaction.Amount = form.amount.data
            transaction.Date = form.date.data
            transaction.Category = form.category.data
            transaction.Description = form.description.data
            db.session.commit()
            if is_testing():
                return jsonify({'message': 'Transaction updated successfully!'}), 200
            flash('Transaction updated successfully!', 'success')
            return redirect(url_for('transactions.transactions'))
        except Exception as e:
            db.session.rollback()
            if is_testing():
                return jsonify({'message': 'An error occurred while updating the transaction. Please try again.'}), 500
            flash('An error occurred while updating the transaction. Please try again.', 'danger')
    else:
        form.amount.data = transaction.Amount
        form.date.data = transaction.Date
        form.category.data = transaction.Category
        form.description.data = transaction.Description
    return render_template('edit_transaction.html', form=form, transaction_id=transaction_id)

@transactions_bp.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    if 'user_id' not in session:
        flash('Please log in to delete a transaction.', 'danger')
        return redirect(url_for('auth.login'))
    transaction = Transaction.query.filter_by(TransactionID=transaction_id, UserID=session['user_id']).first()
    if not transaction:
        if is_testing():
            return jsonify({'message': 'Transaction not found or you do not have permission to delete it.'}), 404
        flash('Transaction not found or you do not have permission to delete it.', 'danger')
        return redirect(url_for('transactions.transactions'))
    try:
        db.session.delete(transaction)
        db.session.commit()
        if is_testing():
            return jsonify({'message': 'Transaction deleted successfully!'}), 200
        flash('Transaction deleted successfully!', 'success')
        return redirect(url_for('transactions.transactions'))
    except Exception as e:
        db.session.rollback()
        if is_testing():
            return jsonify({'message': 'An error occurred while deleting the transaction. Please try again.'}), 500
        flash('An error occurred while deleting the transaction. Please try again.', 'danger')

@transactions_bp.route('/predict_next_month', methods=['GET'])
def predict_next_month():
    if 'user_id' not in session:
        return json.dumps({'success': False, 'message': 'User not logged in'}), 401
    user_id = session['user_id']
    conn = helpers.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT MIN(Date) FROM transactions WHERE UserID = ?", (user_id,))
    min_date_row = cursor.fetchone()
    if not min_date_row or not min_date_row[0]:
        return json.dumps({'success': False, 'message': 'No transactions found.'}), 404

    total_income = db.session.query(func.sum(Outcome.Cost)).filter(Outcome.UserID == user_id, Outcome.Type == 'Income').scalar() or 0
    earliest_date = min_date_row[0]
    months_count = (datetime.date.today().year - earliest_date.year) * 12 + (datetime.date.today().month - earliest_date.month + 1)
    months = list(map(str, range(1, months_count + 1)))
    sums = [0] * months_count
    for i in range(months_count):
        month = (earliest_date.month - 1 + i) % 12 + 1
        year = earliest_date.year + ((earliest_date.month - 1 + i) // 12)
        monthly_sum = db.session.query(func.sum(Transaction.Amount)).filter(Transaction.UserID == user_id, extract('year', Transaction.Date) == year, extract('month', Transaction.Date) == month).scalar()
        sums[i] = float(monthly_sum or 0)
    cursor.close()
    conn.close()
    month_str = ' '.join(map(str, months))
    sum_str = ' '.join(map(lambda x: f"{x:.1f}", sums))
    try:
        prediction = transaction_algo.main(month_str, sum_str)
        return json.dumps({
            'success': True, 
            'prediction': float(prediction), 
            'total_income': total_income
        }), 200
    except Exception as e:
        return json.dumps({'success': False, 'message': str(e)}), 500

def handle_get_transactions(user_id):
    transactions = Transaction.query.filter_by(UserID=user_id).order_by(Transaction.Date.desc()).all()
    return render_template('transactions.html', transactions=transactions)
