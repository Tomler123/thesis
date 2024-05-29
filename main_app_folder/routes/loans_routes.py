from flask import Blueprint, jsonify, redirect, render_template, request, url_for, session, flash
from main_app_folder.forms import forms
from main_app_folder.models.user import User
from main_app_folder.models.loans import Loan
from main_app_folder.extensions import db
from main_app_folder.utils import functions
import warnings

warnings.filterwarnings("ignore")

# creating blueprint
loans_bp = Blueprint('loans', __name__)

# function to get loans
@loans_bp.route('/loans')
def loans():
    # check if the user is logged in
    if 'user_id' not in session:
        flash('Please log in to view your loans.')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.')
        return redirect(url_for('auth.login'))

    # getting all loans and creating pie charts
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

# function to add loans
@loans_bp.route('/add_loan', methods=['GET', 'POST'])
def add_loan():
    # check if the user is logged in
    if 'user_id' not in session:
        flash('Please log in to add a loan.')
        return redirect(url_for('auth.login'))
    
    form = forms.AddLoanForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                new_loan = Loan(
                    UserID=session['user_id'],
                    LenderName=form.lender_name.data,
                    LoanAmount=form.loan_amount.data,
                    InterestRate=form.interest_rate.data,
                    MonthlyPayment=form.monthly_payment.data,
                    StartDate=form.start_date.data,
                    DueDate=form.due_date.data,
                    RemainingBalance=form.remaining_balance.data,
                    IsBorrower=bool(int(form.is_borrower.data)),
                    Notes=form.notes.data
                )

                if new_loan.LoanAmount < 0 or not new_loan.LenderName:
                    flash('Invalid loan data. Please check the details and try again.')
                    return render_template('add_loan.html', form=form)
                
                db.session.add(new_loan)
                db.session.commit()
                flash('Loan added successfully!')
                return redirect(url_for('loans.loans'))

            except Exception as e:
                flash(f"An error occurred: {str(e)}")
        else:
            flash(f"Form validation failed: {form.errors}")

    return render_template('add_loan.html', form=form)

# function to edit loans
@loans_bp.route('/edit_loan/<int:loan_id>', methods=['GET', 'POST'])
def edit_loan(loan_id):
    # check if the user is logged in
    if 'user_id' not in session:
        flash('Please log in to edit records.')
        return redirect(url_for('auth.login'))
    
    loan = Loan.query.filter_by(LoanID=loan_id, UserID=session['user_id']).first()
    if not loan:
        flash('Loan not found.')
        return redirect(url_for('loans.loans'))
    
    form = forms.EditLoanForm(obj=loan)
    
    if request.method == 'POST':
        if form.validate_on_submit():
            try:
                loan.LenderName = form.lender_name.data
                loan.LoanAmount = form.loan_amount.data
                loan.InterestRate = form.interest_rate.data
                loan.MonthlyPayment = form.monthly_payment.data
                loan.StartDate = form.start_date.data
                loan.DueDate = form.due_date.data
                loan.RemainingBalance = form.remaining_balance.data
                loan.IsBorrower = bool(int(form.is_borrower.data))
                loan.Notes = form.notes.data
                db.session.commit()
                flash('Loan updated successfully!')
                return redirect(url_for('loans.loans'))
            except Exception as e:
                flash('An error occurred while updating the loan. Please try again.')
        else:
            flash(f"Form validation failed: {form.errors}")
    else:
        # fillinf the form with values
        form.lender_name.data = loan.LenderName
        form.loan_amount.data = loan.LoanAmount
        form.interest_rate.data = loan.InterestRate
        form.monthly_payment.data = loan.MonthlyPayment
        form.start_date.data = loan.StartDate
        form.due_date.data = loan.DueDate
        form.remaining_balance.data = loan.RemainingBalance
        form.is_borrower.data = loan.IsBorrower
        form.notes.data = loan.Notes
    
    return render_template('edit_loan.html', form=form)

# function to delete loans
@loans_bp.route('/delete_loan/<int:loan_id>', methods=['POST'])
def delete_loan(loan_id):
    # check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'message': 'Please log in to delete loans.'}), 401

    loan = Loan.query.filter_by(LoanID=loan_id, UserID=session['user_id']).first()
    if not loan:
        flash('Loan not found or you do not have permission to delete it.')
        return redirect(url_for('loans.loans'))
    
    try:
        db.session.delete(loan)
        db.session.commit()
        flash('Loan deleted successfully!')
    except Exception as e:
        return jsonify({'message': 'An error occurred while deleting the loan.'}), 500
    
    return redirect(url_for('loans.loans'))
