from flask import jsonify, redirect, request, render_template, url_for, session, flash, session
from main_app_folder.utils import helpers
from main_app_folder.forms import forms
from main_app_folder.ai_algorithms import transaction_algo
import datetime
import json

def init_app(app):
    @app.route('/transactions')
    def transactions():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        conn = helpers.get_db_connection()
        cursor = conn.cursor()

        # Fetch transactions sorted by date
        cursor.execute("SELECT TransactionID, Amount, Date, Category, Description FROM transactions WHERE UserID = ? ORDER BY Date DESC", user_id)
        transactions = cursor.fetchall()

        cursor.close()
        conn.close()

        return render_template('transactions.html', transactions=transactions)

    @app.route('/add_transaction', methods=['GET', 'POST'])
    def add_transaction():
        if 'user_id' not in session:
            flash('Please log in to add an income.')
            return redirect(url_for('login'))

        form = forms.TransactionForm()
        # Set default values when the form is initially presented
        if request.method == 'GET':
            form.date.data = datetime.date.today()
            form.amount.data = 0
        if form.validate_on_submit():
            conn = helpers.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO transactions (UserID, Amount, Date, Category, Description) VALUES (?, ?, ?, ?, ?)",
                        (session['user_id'], form.amount.data, form.date.data, form.category.data, form.description.data))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect(url_for('transactions'))
        return render_template('add_transaction.html', form=form)

    @app.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
    def edit_transaction(transaction_id):
        if 'user_id' not in session:
            flash('Please log in to add an income.')
            return redirect(url_for('login'))
        
        conn = helpers.get_db_connection()
        cursor = conn.cursor()
        form = forms.TransactionForm()
        if request.method == 'POST':
            if form.validate_on_submit():
                cursor.execute("UPDATE transactions SET Amount=?, Date=?, Category=?, Description=? WHERE TransactionID=? AND UserID=?",
                            (form.amount.data, form.date.data, form.category.data, form.description.data, transaction_id, session['user_id']))
                conn.commit()
                cursor.close()
                conn.close()
                return redirect(url_for('transactions'))
        else:
            # Fetch the current transaction details and pre-fill the form
            cursor.execute("SELECT Amount, Date, Category, Description FROM transactions WHERE TransactionID=? AND UserID=?", (transaction_id, session['user_id']))
            transaction = cursor.fetchone()
            form.amount.data = transaction.Amount
            form.date.data = transaction.Date
            form.category.data = transaction.Category
            form.description.data = transaction.Description
        cursor.close()
        conn.close()
        return render_template('edit_transaction.html', form=form, transaction_id=transaction_id)

    @app.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
    def delete_transaction(transaction_id):
        if 'user_id' not in session:
            flash('Please log in to add an income.')
            return redirect(url_for('login'))

        conn = helpers.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM transactions WHERE TransactionID=? AND UserID=?", (transaction_id, session['user_id']))
        conn.commit()
        cursor.close()
        conn.close()
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
        
        cursor.execute("""
                SELECT SUM(Cost) AS total_income FROM outcomes 
                WHERE UserID = ? AND Type = 'Income'
                """, (user_id,))
        result = cursor.fetchone()
        total_income = result.total_income if result.total_income else 0
        
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
            cursor.execute("SELECT SUM(Amount) FROM transactions WHERE UserID = ? AND YEAR(Date) = ? AND MONTH(Date) = ?", (user_id, year, month))
            sum_result = cursor.fetchone()
            if sum_result and sum_result[0] is not None:
                sums[i] = float(sum_result[0])
        
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