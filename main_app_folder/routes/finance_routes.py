from flask import jsonify, redirect, render_template, url_for, session, flash, session
import datetime
from main_app_folder.forms import forms  # Assuming your form is in a forms.py file
# from main_app_folder.models import User  # Assuming you have the User model
from main_app_folder.utils import helpers
from main_app_folder.utils import functions

def init_app(app):
    @app.route('/incomes')
    def incomes():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        conn = helpers.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM outcomes WHERE UserID = ? AND Type = 'Income'", user_id)
        incomes = cursor.fetchall()

        total_incomes = sum(income.Cost for income in incomes)

        # Generate pie charts if there are corresponding records
        incomes_pie_chart_img = functions.generate_pie_chart(incomes) if incomes else None
        
        cursor.close()
        conn.close()

        return render_template('incomes.html', incomes=incomes, incomes_pie_chart_img=incomes_pie_chart_img, total_incomes=total_incomes)

    @app.route('/add_income', methods=['GET', 'POST'])
    def add_income():
        if 'user_id' not in session:
            flash('Please log in to add an income.')
            return redirect(url_for('login'))

        form = forms.IncomeForm()

        if form.validate_on_submit():
            name = form.name.data
            cost = form.cost.data
            day = form.day.data
            user_id = session['user_id']

            # Add income to the database
            query = """INSERT INTO outcomes (UserID, Name, Cost, Day, Type)
                    VALUES (?, ?, ?, ?, 'Income')"""
            with helpers.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (user_id, name, cost, day))
                    conn.commit()

            flash('Income added successfully!')
            return redirect(url_for('incomes'))  # Redirect to the incomes overview page

        return render_template('add_income.html', form=form)

    @app.route('/edit_income/<int:income_id>', methods=['GET', 'POST'])
    def edit_income(income_id):
        if 'user_id' not in session:
            flash('Please log in to edit records.')
            return redirect(url_for('login'))

        form = forms.EditIncomeForm()

        if form.validate_on_submit():
            name = form.name.data
            cost = form.cost.data
            day = form.day.data
            user_id = session['user_id']

            # Update income in the database
            query = """UPDATE outcomes SET Name=?, Cost=?, Day=? WHERE ID=? AND UserID=? AND Type='Income'"""
            with helpers.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (name, cost, day, income_id, user_id))
                    conn.commit()

            flash('Income updated successfully!')
            return redirect(url_for('incomes'))  # Redirect to the incomes overview page

        else:
            # Fetch the current income data
            conn = helpers.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM outcomes WHERE ID=? AND UserID=? AND Type='Income'", (income_id, session['user_id']))
            income = cursor.fetchone()
            cursor.close()
            conn.close()

            if income:
                # Populate form fields with the current income data
                form.name.data = income.Name
                form.cost.data = income.Cost
                form.day.data = income.Day
            else:
                flash('Income not found.')
                return redirect(url_for('incomes'))

        return render_template('edit_income.html', form=form)

    @app.route('/delete_income/<int:income_id>', methods=['POST'])
    def delete_income(income_id):
        if 'user_id' not in session:
            return jsonify({'message': 'Please log in to delete incomes.'}), 401
        
        try:
            user_id = session['user_id']
            # Ensure that the user deleting the income is the owner
            conn = helpers.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM outcomes WHERE ID = ? AND UserID = ?", (income_id, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Income deleted successfully!')
            return redirect(url_for('incomes'))
        except Exception as e:
            return jsonify({'message': 'An error occurred while deleting the income.'}), 500

    @app.route('/saving')
    def savings():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        conn = helpers.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM outcomes WHERE UserID = ? AND Type = 'Saving'", user_id)
        savings = cursor.fetchall()
        
        total_savings = sum(saving.Cost for saving in savings)

        # Generate pie charts if there are corresponding records
        savings_pie_chart_img = functions.generate_pie_chart(savings) if savings else None
        
        cursor.close()
        conn.close()

        return render_template('saving.html', savings=savings, total_savings=total_savings, savings_pie_chart_img=savings_pie_chart_img)

    @app.route('/add_saving', methods=['GET', 'POST'])
    def add_saving():
        if 'user_id' not in session:
            flash('Please log in to add an saving.')
            return redirect(url_for('login'))

        form = forms.SavingForm()

        if form.validate_on_submit():
            name = form.name.data
            cost = form.cost.data
            user_id = session['user_id']

            # Add saving to the database
            query = """INSERT INTO outcomes (UserID, Name, Cost, Type)
                    VALUES (?, ?, ?, 'Saving')"""
            with helpers.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (user_id, name, cost))
                    conn.commit()

            flash('Saving added successfully!')
            return redirect(url_for('savings'))  # Redirect to the savings overview page

        return render_template('add_saving.html', form=form)

    @app.route('/edit_savings/<int:saving_id>', methods=['GET', 'POST'])
    def edit_savings(saving_id):
        if 'user_id' not in session:
            flash('Please log in to edit records.')
            return redirect(url_for('login'))

        form = forms.SavingForm()

        if form.validate_on_submit():
            name = form.name.data
            cost = form.cost.data
            user_id = session['user_id']

            # Update saving in the database
            query = """UPDATE outcomes SET Name=?, Cost=? WHERE ID=? AND UserID=? AND Type='Saving'"""
            with helpers.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (name, cost, saving_id, user_id))
                    conn.commit()

            flash('Saving updated successfully!')
            return redirect(url_for('savings'))  # Redirect to the savings overview page

        else:
            # Fetch the current saving data
            conn = helpers.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM outcomes WHERE ID=? AND UserID=? AND Type='Saving'", (saving_id, session['user_id']))
            saving = cursor.fetchone()
            cursor.close()
            conn.close()

            if saving:
                # Populate form fields with the current saving data
                form.name.data = saving.Name
                form.cost.data = saving.Cost
            else:
                flash('Saving not found.')
                return redirect(url_for('savings'))

        return render_template('edit_savings.html', form=form)

    @app.route('/delete_saving/<int:saving_id>', methods=['POST'])
    def delete_saving(saving_id):
        if 'user_id' not in session:
            return jsonify({'message': 'Please log in to delete savings.'}), 401
        
        try:
            user_id = session['user_id']
            # Ensure that the user deleting the saving is the owner
            conn = helpers.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM outcomes WHERE ID = ? AND UserID = ?", (saving_id, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Saving deleted successfully!')
            return redirect(url_for('savings'))
        except Exception as e:
            return jsonify({'message': 'An error occurred while deleting the saving.'}), 500

    @app.route('/outcomes')
    def outcomes():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        conn = helpers.get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM outcomes WHERE UserID = ?", user_id)
        outcomes = cursor.fetchall()

        # Calculate totals
        total_expenses = sum(outcome.Cost for outcome in outcomes if outcome.Type == 'Expense')
        total_subscriptions = sum(outcome.Cost for outcome in outcomes if outcome.Type == 'Subscription')


        expenses = [outcome for outcome in outcomes if outcome.Type == 'Expense']
        subscriptions = [outcome for outcome in outcomes if outcome.Type == 'Subscription']

        # Generate pie charts if there are corresponding records
        expenses_pie_chart_img = functions.generate_pie_chart(expenses) if expenses else None
        subscriptions_pie_chart_img = functions.generate_pie_chart(subscriptions) if subscriptions else None

        cursor.close()
        conn.close()

        return render_template('outcomes.html', outcomes=outcomes, expenses_pie_chart_img=expenses_pie_chart_img, subscriptions_pie_chart_img=subscriptions_pie_chart_img, total_expenses=total_expenses, total_subscriptions=total_subscriptions)

    @app.route('/add_outcome', methods=['GET', 'POST'])
    def add_outcome():
        if 'user_id' not in session:
            flash('Please log in to add an outcome.')
            return redirect(url_for('login'))

        form = forms.OutcomeForm()

        if form.validate_on_submit():
            name = form.name.data
            cost = form.cost.data
            day = form.day.data
            outcome_type = form.type.data
            user_id = session['user_id']

            # Add outcome to database
            query = """INSERT INTO outcomes (UserID, Name, Cost, Day, Type, Year, Month, Fulfilled)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            with helpers.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (user_id, name, cost, day, outcome_type, datetime.date.today().year, datetime.date.today().month, 0))
                    conn.commit()
            flash('Outcome added successfully!')
            return redirect(url_for('outcomes'))  # Redirect to the outcomes overview page

        return render_template('add_outcome.html', form=form)

    @app.route('/edit_outcome/<int:outcome_id>', methods=['GET', 'POST'])
    def edit_outcome(outcome_id):
        if 'user_id' not in session:
            flash('Please log in to edit records.')
            return redirect(url_for('login'))

        form = forms.EditOutcomeForm()

        if form.validate_on_submit():
            name = form.name.data
            cost = form.cost.data
            day = form.day.data
            outcome_type = form.type.data
            user_id = session['user_id']

            # Update outcome in the database
            query = """UPDATE outcomes SET Name=?, Cost=?, Day=?, Type=? WHERE ID=? AND UserID=?"""
            with helpers.get_db_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (name, cost, day, outcome_type, outcome_id, user_id))
                    conn.commit()

            flash('Outcome updated successfully!')
            return redirect(url_for('outcomes'))  # Redirect to the outcomes overview page

        else:
            # Fetch the current outcome data
            conn = helpers.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM outcomes WHERE ID=? AND UserID=?", (outcome_id, session['user_id']))
            outcome = cursor.fetchone()
            cursor.close()
            conn.close()

            if outcome:
                # Populate form fields with the current outcome data
                form.name.data = outcome.Name
                form.cost.data = outcome.Cost
                form.day.data = outcome.Day
                form.type.data = outcome.Type
            else:
                flash('Outcome not found.')
                return redirect(url_for('outcomes'))

        return render_template('edit_outcome.html', form=form)

    @app.route('/delete_outcome/<int:outcome_id>', methods=['POST'])
    def delete_outcome(outcome_id):
        if 'user_id' not in session:
            return jsonify({'message': 'Please log in to delete outcomes.'}), 401
        
        try:
            user_id = session['user_id']
            # Ensure that the user deleting the outcome is the owner
            conn = helpers.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM outcomes WHERE ID = ? AND UserID = ?", (outcome_id, user_id))
            conn.commit()
            cursor.close()
            conn.close()
            flash('Outcome deleted successfully!')
            return redirect(url_for('outcomes'))
        except Exception as e:
            return jsonify({'message': 'An error occurred while deleting the outcome.'}), 500
