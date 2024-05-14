from flask import jsonify, redirect, render_template, request, url_for, session, flash
import datetime
from main_app_folder.forms import forms  # Adjust this import if necessary
from main_app_folder.models.user import User
from main_app_folder.models.loans import Loan
from main_app_folder.utils import helpers
from main_app_folder import db

from main_app_folder.utils import functions

def init_app(app):
    @app.route('/loans')
    def loans():
        if 'user_id' not in session:
            flash('Please log in to view your loans.')
            return redirect(url_for('login'))

        user = User.query.get(session['user_id'])
        if not user:
            flash('User not found.')
            return redirect(url_for('login'))

        borrowed_loans = Loan.query.filter_by(UserID=user.UserID, IsBorrower=True).all()
        borrowed_loans_pie_chart_img = functions.loans_pie_chart(borrowed_loans) if borrowed_loans else None
        total_borrowed_loans = sum(loan.LoanAmount for loan in borrowed_loans)

        lent_loans = Loan.query.filter_by(UserID=user.UserID, IsBorrower=False).all()
        lent_loans_pie_chart_img = functions.loans_pie_chart(lent_loans) if lent_loans else None
        total_lent_loans = sum(loan.LoanAmount for loan in lent_loans)

        return render_template('loans.html', 
                               borrowed_loans=borrowed_loans, lent_loans=lent_loans, 
                               lent_loans_pie_chart_img=lent_loans_pie_chart_img, 
                               borrowed_loans_pie_chart_img=borrowed_loans_pie_chart_img, 
                               total_borrowed_loans=total_borrowed_loans, 
                               total_lent_loans=total_lent_loans)
    
    @app.route('/add_loan', methods=['GET', 'POST'])
    def add_loan():
        if 'user_id' not in session:
            flash('Please log in to add a loan.')
            return redirect(url_for('login'))

        form = forms.AddLoanForm()
        if form.validate_on_submit():
            try:
                lender_name = form.lender_name.data
                loan_amount = form.loan_amount.data
                interest_rate = form.interest_rate.data
                monthly_payment = form.monthly_payment.data
                start_date = form.start_date.data
                due_date = form.due_date.data
                remaining_balance = form.remaining_balance.data
                is_borrower = bool(int(form.is_borrower.data))  # Ensure correct boolean casting
                notes = form.notes.data
                user_id = session['user_id']

                # Log the form data
                print("Validating and submitting form data:")
                print(f"Lender Name: {lender_name}, Loan Amount: {loan_amount}, Interest Rate: {interest_rate}, Monthly Payment: {monthly_payment}")
                print(f"Start Date: {start_date}, Due Date: {due_date}, Remaining Balance: {remaining_balance}, Is Borrower: {is_borrower}, Notes: {notes}")

                # Assuming conn is your database connection
                query = """INSERT INTO loans (UserID, LenderName, LoanAmount, InterestRate, MonthlyPayment, StartDate, DueDate, RemainingBalance, IsBorrower, Notes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                with helpers.get_db_connection() as conn:
                    with conn.cursor() as cursor:
                        cursor.execute(query, (user_id, lender_name, loan_amount, interest_rate, monthly_payment, start_date, due_date, remaining_balance, is_borrower, notes))
                        conn.commit()

                flash('Loan added successfully!')
                return redirect(url_for('loans'))  # Redirect to the loans overview page
            except Exception as e:
                flash(f"An error occurred: {str(e)}")
                print(f"An error occurred: {str(e)}")  # Log the error for debugging

        else:
            print("Form errors:", form.errors)  # Log form errors

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
