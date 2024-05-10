from flask import jsonify, redirect, render_template, request, url_for, session, flash, session
import datetime
from main_app_folder.forms import forms  # Assuming your form is in a forms.py file
# from main_app_folder.models import User  # Assuming you have the User model
from main_app_folder.utils import helpers
from main_app_folder.utils import functions

def init_app(app):
    @app.route('/loans')
    def loans():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        conn = helpers.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM loans WHERE UserID = ? AND IsBorrower = 1", user_id)
        borrowed_loans = cursor.fetchall()
        
        borrowed_loans_pie_chart_img = functions.loans_pie_chart(borrowed_loans) if borrowed_loans else None
        total_borrowed_loans = sum(loan.LoanAmount for loan in borrowed_loans)

        cursor.execute("SELECT * FROM loans WHERE UserID = ? AND IsBorrower = 0", user_id)
        lent_loans = cursor.fetchall()

        lent_loans_pie_chart_img = functions.loans_pie_chart(lent_loans) if lent_loans else None
        total_lent_loans = sum(loan.LoanAmount for loan in lent_loans)

        cursor.close()
        conn.close()

        return render_template('loans.html', borrowed_loans=borrowed_loans, lent_loans=lent_loans, lent_loans_pie_chart_img=lent_loans_pie_chart_img, borrowed_loans_pie_chart_img=borrowed_loans_pie_chart_img, total_borrowed_loans=total_borrowed_loans, total_lent_loans=total_lent_loans)

    @app.route('/add_loan', methods=['GET', 'POST'])
    def add_loan():
        if 'user_id' not in session:
            flash('Please log in to add a loan.')
            return redirect(url_for('login'))

        form = forms.AddLoanForm()
        if form.validate_on_submit():
            # Form data is valid, proceed to add the loan
            lender_name = form.lender_name.data
            loan_amount = form.loan_amount.data
            interest_rate = form.interest_rate.data
            monthly_payment = form.monthly_payment.data
            start_date = form.start_date.data
            due_date = form.due_date.data
            remaining_balance = form.remaining_balance.data
            is_borrower = form.is_borrower.data
            notes = form.notes.data
            user_id = session['user_id']

            # Add loan to database
            # Assuming conn is your database connection
            query = """INSERT INTO loans (UserID, LenderName, LoanAmount, InterestRate, MonthlyPayment, StartDate, DueDate, RemainingBalance,IsBorrower, Notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
            with helpers.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (user_id, lender_name, loan_amount, interest_rate, monthly_payment, start_date, due_date, remaining_balance, is_borrower, notes))
                    conn.commit()

            flash('Loan added successfully!')
            return redirect(url_for('loans'))  # Redirect to the loans overview page

        return render_template('add_loan.html', form=form)

    @app.route('/edit_loan/<int:loan_id>', methods=['GET', 'POST'])
    def edit_loan(loan_id):
        # Check if user is logged in
        if 'user_id' not in session:
            flash('Please log in to edit records.')
            return redirect(url_for('login'))

        # Connect to your database
        conn = helpers.get_db_connection()
        cursor = conn.cursor()

        form = forms.EditLoanForm()

        if request.method == 'POST' or form.validate_on_submit():
            lender_name = form.lender_name.data
            loan_amount = form.loan_amount.data
            interest_rate = form.interest_rate.data
            monthly_payment = form.monthly_payment.data
            start_date = form.start_date.data
            due_date = form.due_date.data
            remaining_balance = form.remaining_balance.data
            is_borrower = form.is_borrower.data
            notes = form.notes.data

            # Update the loan details in the database
            update_query = """UPDATE loans SET LenderName=?, LoanAmount=?, InterestRate=?, MonthlyPayment=?,StartDate=?, DueDate=?, RemainingBalance=?, IsBorrower=?, Notes=? WHERE LoanID=?"""
            cursor.execute(update_query, (lender_name, loan_amount, interest_rate, monthly_payment, start_date, due_date, remaining_balance, is_borrower, notes, loan_id))
            conn.commit()

            # Redirect to a confirmation page or back to the loan list
            return redirect(url_for('loans'))

        else:
            # For a GET request, fetch the loan's current details to prefill the form
            cursor.execute("SELECT * FROM loans WHERE LoanID=?", (loan_id,))
            loan = cursor.fetchone()

            form.lender_name.data = loan.LenderName
            form.loan_amount.data = loan.LoanAmount
            form.interest_rate.data = loan.InterestRate
            form.monthly_payment.data = loan.MonthlyPayment
            form.start_date.data = loan.StartDate
            form.due_date.data = loan.DueDate
            form.remaining_balance.data = loan.RemainingBalance
            form.is_borrower.data = loan.IsBorrower
            form.notes.data = loan.Notes

            # Render the edit page template with the loan details
            return render_template('edit_loan.html', form=form)

    @app.route('/delete_loan/<int:loan_id>', methods=['POST'])
    def delete_loan(loan_id):
        if 'user_id' not in session:
            return jsonify({'message': 'Please log in to delete loans.'}), 401
        
        try:
            user_id = session['user_id']
            # Ensure that the user deleting the loan is the owner
            conn = helpers.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM loans WHERE LoanID = ? AND UserID = ?", (loan_id, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Loan deleted successfully!')
            return redirect(url_for('loans'))
        except Exception as e:
            return jsonify({'message': 'An error occurred while deleting the loan.'}), 500
