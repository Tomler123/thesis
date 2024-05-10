


from flask import flash, redirect, render_template, request, session, url_for

from main_app_folder.utils import helpers
from main_app_folder.forms import forms


def init_app(app):
    @app.route('/update_icon', methods=['POST'])
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

            return redirect(url_for('account'))  # Redirect to the account page after updating
        else:
            flash('You must be logged in to update the profile image.')
            return redirect(url_for('login'))

    @app.route('/account', methods=['GET','POST'])
    def account():
        if 'user_id' in session:
            user_id = session['user_id']
            
            form = forms.IconForm()

            # Connect to the database
            conn = helpers.get_db_connection()
            cursor = conn.cursor()

            if form.validate_on_submit():  # Check if the form is submitted and validated
                selected_icon = form.selected_icon.data
                return update_icon()

            # Fetch user details
            cursor.execute("SELECT * FROM users WHERE UserID = ?", user_id)
            user_details = cursor.fetchone()

            # Check if user details were found
            if user_details:
                # Income
                cursor.execute("""
                SELECT SUM(Cost) AS total_income FROM outcomes 
                WHERE UserID = ? AND Type = 'Income'
                """, (user_id,))
                result = cursor.fetchone()
                total_income = result.total_income if result.total_income else 0

                # Saving
                cursor.execute("""
                SELECT SUM(Cost) AS total_saving FROM outcomes 
                WHERE UserID = ? AND Type = 'Saving'
                """, (user_id,))
                result = cursor.fetchone()
                total_saving = result.total_saving if result.total_saving else 0

                # Expenses
                cursor.execute("""
                SELECT SUM(Cost) AS total_expenses FROM outcomes 
                WHERE UserID = ? AND (Type = 'Expense' OR Type = 'Subscription')
                """, (user_id,))
                result = cursor.fetchone()
                total_expenses = result.total_expenses if result.total_expenses else 0

                # Loan
                cursor.execute("""
                SELECT SUM(LoanAmount) AS total_borrowed 
                FROM loans 
                WHERE UserID = ? AND IsBorrower = 1
                """, (user_id,))
                total_borrowed = cursor.fetchone()[0] or 0

                cursor.execute("""
                SELECT SUM(LoanAmount) AS total_lent 
                FROM loans 
                WHERE UserID = ? AND IsBorrower = 0
                """, (user_id,))
                total_lent = cursor.fetchone()[0] or 0
                # Close the database connection
                cursor.close()
                conn.close()

                # Pass the user details to the template
                return render_template('account.html', user=user_details, total_saving=total_saving, total_income=total_income, total_expenses=total_expenses, total_borrowed=round(total_borrowed, 0), total_lent=round(total_lent, 0), form=form)
            else:
                # Close the database connection
                cursor.close()
                conn.close()

                flash('User not found.')
                return redirect(url_for('login'))
        else:
            flash('You must be logged in to view the account page')
            return redirect(url_for('login'))

    @app.route('/logout')
    def logout():
        session.pop('user_id', None)  # Remove the user_id from the session
        return redirect(url_for('home'))