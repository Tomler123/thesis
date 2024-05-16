from flask import jsonify, redirect, render_template, request, url_for, session, flash, session
import datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from main_app_folder.forms import forms  # Assuming your form is in a forms.py file
from main_app_folder.utils import helpers
from main_app_folder.utils import functions
from main_app_folder.extensions import db
from main_app_folder.models.user import User
from main_app_folder.models.outcomes import Outcome


def init_app(app):

    @app.route('/incomes')
    def incomes():
        try:
            if 'user_id' not in session:
                return redirect(url_for('login'))

            user_id = session['user_id']
            return handle_get_incomes(user_id)
        except SQLAlchemyError as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/add_income', methods=['GET', 'POST'])
    def add_income():
        try:
            if 'user_id' not in session:
                flash('Please log in to add an income.')
                return redirect(url_for('login'))

            form = forms.IncomeForm()
            if form.validate_on_submit():
                new_income = Outcome(
                    UserID=session['user_id'],
                    Name=form.name.data,
                    Cost=form.cost.data,
                    Day=form.day.data,
                    Type='Income'
                )
                
                return handle_add_income(new_income)
            
            return render_template('add_income.html', form=form)
        
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('Error adding income.')
            return render_template('add_income.html', form=form), 500
        
    @app.route('/edit_income/<int:income_id>', methods=['GET', 'POST'])
    def edit_income(income_id):
        if 'user_id' not in session:
            flash('Please log in to edit records.')
            return redirect(url_for('login'))

        income = Outcome.query.filter_by(ID=income_id, UserID=session['user_id']).first()
        if not income:
            flash('Income not found.')
            return redirect(url_for('incomes'))

        form = forms.EditIncomeForm(obj=income)

        if request.method == 'POST' and form.validate_on_submit():
            return handle_edit_income(income, form)
        
        elif request.method == 'GET':
            form.name.data = income.Name
            form.cost.data = income.Cost
            form.day.data = income.Day

        return render_template('edit_income.html', form=form, income_id=income_id)

    @app.route('/delete_income/<int:income_id>', methods=['POST'])
    def delete_income(income_id):
        try:
            if 'user_id' not in session:
                return jsonify({'message': 'Please log in to delete incomes.'}), 401

            income = Outcome.query.filter_by(ID=income_id, UserID=session['user_id']).first()
            return handle_delete_income(income)
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

    @app.route('/savings')
    def savings():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        return handle_get_savings(user_id)

    @app.route('/add_saving', methods=['GET', 'POST'])
    def add_saving():
        if 'user_id' not in session:
            flash('Please log in to add a saving.')
            return redirect(url_for('login'))

        form = forms.SavingForm()
        if form.validate_on_submit():
            new_saving = Outcome(
                UserID=session['user_id'],
                Name=form.name.data,
                Cost=form.cost.data,
                Type='Saving'
            )
            
            return handle_add_saving(new_saving)
        
        return render_template('add_saving.html', form=form)

    @app.route('/edit_saving/<int:saving_id>', methods=['GET', 'POST'])
    def edit_saving(saving_id):
        if 'user_id' not in session:
            flash('Please log in to edit records.')
            return redirect(url_for('login'))

        saving = Outcome.query.filter_by(ID=saving_id, UserID=session['user_id'], Type='Saving').first()
        if not saving:
            flash('Saving not found.')
            return redirect(url_for('savings'))

        form = forms.EditSavingForm(obj=saving)

        if request.method == 'POST' and form.validate_on_submit():
            return handle_edit_saving(saving, form)
        
        elif request.method == 'GET':
            form.name.data = saving.Name
            form.cost.data = saving.Cost

        return render_template('edit_saving.html', form=form, saving_id=saving_id)

    @app.route('/delete_saving/<int:saving_id>', methods=['POST'])
    def delete_saving(saving_id):
        try:
            if 'user_id' not in session:
                return jsonify({'message': 'Please log in to delete savings.'}), 401

            saving = Outcome.query.filter_by(ID=saving_id, UserID=session['user_id'], Type='Saving').first()
            return handle_delete_saving(saving)
        except SQLAlchemyError as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500


    @app.route('/outcomes')
    def outcomes():
        if 'user_id' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        return handle_get_outcomes(user_id)

    @app.route('/add_outcome', methods=['GET', 'POST'])
    def add_outcome():
        if 'user_id' not in session:
            flash('Please log in to add an outcome.')
            return redirect(url_for('login'))

        form = forms.OutcomeForm()
        if form.validate_on_submit():
            try:
                new_outcome = Outcome(
                    UserID=session['user_id'],
                    Name=form.name.data,
                    Cost=form.cost.data,
                    Day=form.day.data,
                    Month=datetime.date.today().month,
                    Year=datetime.date.today().year,
                    Fulfilled=0,
                    Type=form.type.data
                )
                return handle_add_outcome(new_outcome)
            except Exception as e:
                flash('An error occurred while adding the outcome: ' + str(e))
                db.session.rollback()

        return render_template('add_outcome.html', form=form)

    @app.route('/edit_outcome/<int:outcome_id>', methods=['GET', 'POST'])
    def edit_outcome(outcome_id):
        if 'user_id' not in session:
            flash('Please log in to edit records.')
            return redirect(url_for('login'))

        outcome = Outcome.query.filter_by(ID=outcome_id, UserID=session['user_id']).first()
        if not outcome:
            flash('Outcome not found.')
            return redirect(url_for('outcomes'))

        form = forms.EditOutcomeForm(obj=outcome)  # Initialize form with outcome object if it's a GET request

        if request.method == 'POST' and form.validate_on_submit():
            return handle_edit_outcome(outcome, form)
        
        elif request.method == 'GET':
            form.name.data = outcome.Name
            form.cost.data = outcome.Cost
            form.day.data = outcome.Day
            form.type.data = outcome.Type

        return render_template('edit_outcome.html', form=form, outcome_id=outcome_id)
    
    @app.route('/delete_outcome/<int:outcome_id>', methods=['POST'])
    def delete_outcome(outcome_id):
        if 'user_id' not in session:
            return jsonify({'message': 'Please log in to delete outcomes.'}), 401

        outcome = Outcome.query.filter_by(ID=outcome_id, UserID=session['user_id']).first()
        return handle_delete_outcome(outcome)

def handle_get_incomes(user_id):
    incomes = Outcome.query.filter_by(UserID=user_id, Type='Income').all()
    total_incomes = sum(income.Cost for income in incomes if income)
    incomes_pie_chart_img = functions.generate_pie_chart(incomes) if incomes else None
    return render_template('incomes.html', incomes=incomes, incomes_pie_chart_img=incomes_pie_chart_img, total_incomes=total_incomes)

def handle_add_income(new_income):
    db.session.add(new_income)
    db.session.commit()
    flash('Income added successfully!')
    return redirect(url_for('incomes'))

def handle_edit_income(income, form):
    income.Name = form.name.data
    income.Cost = form.cost.data
    income.Day = form.day.data
    db.session.commit()
    flash('Income updated successfully!')
    return redirect(url_for('incomes'))

def handle_delete_income(income):
    if income:
        db.session.delete(income)
        db.session.commit()
        flash('Income deleted successfully!')
    else:
        flash('Income not found or you do not have permission to delete it.')
    return redirect(url_for('incomes'))

def handle_get_savings(user_id):
    conn = helpers.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM outcomes WHERE UserID = ? AND Type = 'Saving'", (user_id,))
    savings = cursor.fetchall()
    
    total_savings = sum(saving.Cost for saving in savings)

    # Generate pie charts if there are corresponding records
    savings_pie_chart_img = functions.generate_pie_chart(savings) if savings else None
    
    cursor.close()
    conn.close()

    return render_template('saving.html', savings=savings, total_savings=total_savings, savings_pie_chart_img=savings_pie_chart_img)

def handle_add_saving(new_saving):
    db.session.add(new_saving)
    db.session.commit()
    flash('Saving added successfully!')
    return redirect(url_for('savings'))

def handle_edit_saving(saving, form):
    saving.Name = form.name.data
    saving.Cost = form.cost.data
    db.session.commit()
    flash('Saving updated successfully!')
    return redirect(url_for('savings'))

def handle_delete_saving(saving):
    if saving:
        db.session.delete(saving)
        db.session.commit()
        flash('Saving deleted successfully!')
    else:
        flash('Saving not found or you do not have permission to delete it.')
    return redirect(url_for('savings'))

def handle_get_outcomes(user_id):
    outcomes = Outcome.query.filter_by(UserID=user_id).all()
    expenses = [outcome for outcome in outcomes if outcome.Type == 'Expense']
    subscriptions = [outcome for outcome in outcomes if outcome.Type == 'Subscription']
    total_expenses = sum(outcome.Cost for outcome in expenses)
    total_subscriptions = sum(outcome.Cost for outcome in subscriptions)
    expenses_pie_chart_img = functions.generate_pie_chart(expenses) if expenses else None
    subscriptions_pie_chart_img = functions.generate_pie_chart(subscriptions) if subscriptions else None
    return render_template('outcomes.html', outcomes=outcomes, expenses_pie_chart_img=expenses_pie_chart_img, subscriptions_pie_chart_img=subscriptions_pie_chart_img, total_expenses=total_expenses, total_subscriptions=total_subscriptions)

def handle_add_outcome(new_outcome):
    db.session.add(new_outcome)
    db.session.commit()
    flash('Outcome added successfully!')
    return redirect(url_for('outcomes'))

def handle_edit_outcome(outcome, form):
    outcome.Name = form.name.data
    outcome.Cost = form.cost.data
    outcome.Day = form.day.data
    outcome.Type = form.type.data
    db.session.commit()
    flash('Outcome updated successfully!')
    return redirect(url_for('outcomes'))

def handle_delete_outcome(outcome):
    if outcome:
        db.session.delete(outcome)
        db.session.commit()
        flash('Outcome deleted successfully!')
    else:
        flash('Outcome not found or you do not have permission to delete it.')
    return redirect(url_for('outcomes'))