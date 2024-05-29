from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from main_app_folder.utils import helpers
from main_app_folder.forms import forms
from main_app_folder.models.outcomes import Outcome
from main_app_folder.models.loans import Loan
from main_app_folder.models.user import User
from main_app_folder.extensions import db

# create blueprint
account_bp = Blueprint('account', __name__)

# function to change profile icon
@account_bp.route('/update_icon', methods=['POST'])
def update_icon():
    if 'user_id' in session:
        user_id = session['user_id']
        selected_icon = request.form.get('selected_icon')
        try:
            conn = helpers.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET ProfileImage = ? WHERE UserID = ?", (selected_icon, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Profile image updated successfully.')
        except Exception as e:
            flash('An error occurred while updating the profile image.')
        return redirect(url_for('account.account'))
    else:
        flash('You must be logged in to update the profile image.')
        return redirect(url_for('auth.login'))

# function for profile page to display information
@account_bp.route('/account', methods=['GET','POST'])
def account():
    # check if the user is logged in
    if 'user_id' not in session:
        flash('You must be logged in to view the account page')
        return redirect(url_for('auth.login'))

    user_id = session['user_id']
    form = forms.IconForm()

    if form.validate_on_submit():
        selected_icon = form.selected_icon.data
        return update_icon()

    user = User.query.get(user_id)
    if not user:
        flash('User not found.')
        return redirect(url_for('auth.login'))

    total_income = Outcome.query.with_entities(db.func.sum(Outcome.Cost)).filter_by(UserID=user_id, Type='Income').scalar() or 0
    total_saving = Outcome.query.with_entities(db.func.sum(Outcome.Cost)).filter_by(UserID=user_id, Type='Saving').scalar() or 0
    total_expenses = Outcome.query.with_entities(db.func.sum(Outcome.Cost)).filter(
        Outcome.UserID == user_id,
        db.or_(Outcome.Type == 'Expense', Outcome.Type == 'Subscription')
    ).scalar() or 0

    total_borrowed = Loan.query.with_entities(db.func.sum(Loan.LoanAmount)).filter_by(UserID=user_id, IsBorrower=True).scalar() or 0
    total_lent = Loan.query.with_entities(db.func.sum(Loan.LoanAmount)).filter_by(UserID=user_id, IsBorrower=False).scalar() or 0

    return render_template(
        'account.html',
        user=user,
        total_saving=total_saving,
        total_income=total_income,
        total_expenses=total_expenses,
        total_borrowed=round(total_borrowed, 0),
        total_lent=round(total_lent, 0),
        form=form
    )
