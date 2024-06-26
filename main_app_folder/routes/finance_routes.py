from flask import Blueprint, jsonify, redirect, render_template, request, url_for, session, flash
import datetime
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from main_app_folder.forms import forms
from main_app_folder.utils import functions
from main_app_folder.extensions import db
from main_app_folder.models.outcomes import Outcome

# creating blueprint
finance_bp = Blueprint('finance', __name__)

# function to get income data
@finance_bp.route('/incomes')
def incomes():
    try:
        # check if the user is logged in
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        
        user_id = session['user_id']
        incomes = Outcome.query.filter_by(UserID=user_id, Type='Income').all()
        total_incomes = sum(income.Cost for income in incomes if income)
        incomes_pie_chart_img = functions.generate_pie_chart(incomes) if incomes else None
        
        return render_template('incomes.html', incomes=incomes, incomes_pie_chart_img=incomes_pie_chart_img, total_incomes=total_incomes)
    
    except SQLAlchemyError as e:
        return jsonify({'error': str(e)}), 500

# function to add income
@finance_bp.route('/add_income', methods=['GET', 'POST'])
def add_income():
    try:
        # check if the user is logged in
        if 'user_id' not in session:
            flash('Please log in to add an income.')
            return redirect(url_for('auth.login'))

        form = forms.IncomeForm()

        if form.validate_on_submit():
            new_income = Outcome(
                UserID=session['user_id'],
                Name=form.name.data,
                Cost=form.cost.data,
                Day=form.day.data,
                Type='Income'
            )
            db.session.add(new_income)
            db.session.commit()
            flash('Income added successfully!')
            return redirect(url_for('finance.incomes'))

        return render_template('add_income.html', form=form)

    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error adding income.')
        return render_template('add_income.html', form=form), 500

# function to edit income
@finance_bp.route('/edit_income/<int:income_id>', methods=['GET', 'POST'])
def edit_income(income_id):
    try:
        # check if the user is logged in
        if 'user_id' not in session:
            flash('Please log in to edit records.')
            return redirect(url_for('auth.login'))

        income = Outcome.query.filter_by(ID=income_id, UserID=session['user_id']).first()
        if not income:
            flash('Income not found.')
            return redirect(url_for('finance.incomes'))

        form = forms.EditIncomeForm(obj=income)

        if request.method == 'POST' and form.validate_on_submit():
            income.Name = form.name.data
            income.Cost = form.cost.data
            income.Day = form.day.data
            db.session.commit()
            flash('Income updated successfully!')
            return redirect(url_for('finance.incomes'))

        elif request.method == 'GET':
            form.name.data = income.Name
            form.cost.data = income.Cost
            form.day.data = income.Day

        return render_template('edit_income.html', form=form, income_id=income_id)

    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Error updating income.')
        return render_template('edit_income.html', form=form, income_id=income_id), 500

# function to delete incomes
@finance_bp.route('/delete_income/<int:income_id>', methods=['POST'])
def delete_income(income_id):
    try:
        # check if the user is logged in
        if 'user_id' not in session:
            return jsonify({'message': 'Please log in to delete incomes.'}), 401

        income = Outcome.query.filter_by(ID=income_id, UserID=session['user_id']).first()

        if income:
            db.session.delete(income)
            db.session.commit()
            flash('Income deleted successfully!')
        else:
            flash('Income not found or you do not have permission to delete it.')

        return redirect(url_for('finance.incomes'))

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# function to get savings
@finance_bp.route('/savings')
def savings():
    # check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user_id = session['user_id']
    
    savings = Outcome.query.filter_by(UserID=user_id, Type='Saving').all()
    total_savings = sum(saving.Cost for saving in savings)
    savings_pie_chart_img = functions.generate_pie_chart(savings) if savings else None

    return render_template('saving.html', savings=savings, total_savings=total_savings, savings_pie_chart_img=savings_pie_chart_img)

# function to add savings
@finance_bp.route('/add_saving', methods=['GET', 'POST'])
def add_saving():
    # check if the user is logged in
    if 'user_id' not in session:
        flash('Please log in to add a saving.')
        return redirect(url_for('auth.login'))

    form = forms.SavingForm()
    if form.validate_on_submit():
        new_saving = Outcome(
            UserID=session['user_id'],
            Name=form.name.data,
            Cost=form.cost.data,
            Type='Saving'
        )
        
        db.session.add(new_saving)
        db.session.commit()
        flash('Saving added successfully!')
        return redirect(url_for('finance.savings'))
    
    return render_template('add_saving.html', form=form)

# function to edit savings
@finance_bp.route('/edit_savings/<int:saving_id>', methods=['GET', 'POST'])
def edit_savings(saving_id):
    # check if the user is logged in
    if 'user_id' not in session:
        flash('Please log in to edit records.')
        return redirect(url_for('auth.login'))

    saving = Outcome.query.filter_by(ID=saving_id, UserID=session['user_id'], Type='Saving').first()
    if not saving:
        flash('Saving not found.')
        return redirect(url_for('finance.savings'))

    form = forms.EditSavingForm(obj=saving)
    if request.method == 'POST' and form.validate_on_submit():
        saving.Name = form.name.data
        saving.Cost = form.cost.data
        db.session.commit()
        flash('Saving updated successfully!')
        return redirect(url_for('finance.savings'))
    
    elif request.method == 'GET':
        form.name.data = saving.Name
        form.cost.data = saving.Cost

    return render_template('edit_savings.html', form=form, saving_id=saving_id)

# function for deleting savings
@finance_bp.route('/delete_saving/<int:saving_id>', methods=['POST'])
def delete_saving(saving_id):
    try:
        # check if the user is logged in
        if 'user_id' not in session:
            return jsonify({'message': 'Please log in to delete savings.'}), 401

        saving = Outcome.query.filter_by(ID=saving_id, UserID=session['user_id'], Type='Saving').first()
        if saving:
            db.session.delete(saving)
            db.session.commit()
            flash('Saving deleted successfully!')
        else:
            flash('Saving not found or you do not have permission to delete it.')

        return redirect(url_for('finance.savings'))
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# function to get outcomes
@finance_bp.route('/outcomes')
def outcomes():
    # check if the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    
    outcomes = Outcome.query.filter_by(UserID=user_id).all()
    expenses = [outcome for outcome in outcomes if outcome.Type == 'Expense']
    subscriptions = [outcome for outcome in outcomes if outcome.Type == 'Subscription']
    total_expenses = sum(outcome.Cost for outcome in expenses)
    total_subscriptions = sum(outcome.Cost for outcome in subscriptions)
    
    expenses_pie_chart_img = functions.generate_pie_chart(expenses) if expenses else None
    subscriptions_pie_chart_img = functions.generate_pie_chart(subscriptions) if subscriptions else None
    
    return render_template(
        'outcomes.html', 
        outcomes=outcomes, 
        expenses_pie_chart_img=expenses_pie_chart_img, 
        subscriptions_pie_chart_img=subscriptions_pie_chart_img, 
        total_expenses=total_expenses, 
        total_subscriptions=total_subscriptions
    )

# function to add new outcome to the database
@finance_bp.route('/add_outcome', methods=['GET', 'POST'])
def add_outcome():
    # check if the user is logged in
    if 'user_id' not in session:
        flash('Please log in to add an outcome.')
        return redirect(url_for('auth.login'))
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
            db.session.add(new_outcome)
            db.session.commit()
            flash('Outcome added successfully!')
            return redirect(url_for('finance.outcomes'))
        except Exception as e:
            flash('An error occurred while adding the outcome: ' + str(e))
            db.session.rollback()
    return render_template('add_outcome.html', form=form)

# function to edit outcome
@finance_bp.route('/edit_outcome/<int:outcome_id>', methods=['GET', 'POST'])
def edit_outcome(outcome_id):
    # check if the user is logged in
    if 'user_id' not in session:
        flash('Please log in to edit records.')
        return redirect(url_for('auth.login'))
    
    outcome = Outcome.query.filter_by(ID=outcome_id, UserID=session['user_id']).first()
    if not outcome:
        flash('Outcome not found.')
        return redirect(url_for('finance.outcomes'))
    
    form = forms.EditOutcomeForm(obj=outcome)
    if request.method == 'POST' and form.validate_on_submit():
        outcome.Name = form.name.data
        outcome.Cost = form.cost.data
        outcome.Day = form.day.data
        outcome.Type = form.type.data
        db.session.commit()
        flash('Outcome updated successfully!')
        return redirect(url_for('finance.outcomes'))
    
    elif request.method == 'GET':
        form.name.data = outcome.Name
        form.cost.data = outcome.Cost
        form.day.data = outcome.Day
        form.type.data = outcome.Type
    
    return render_template('edit_outcome.html', form=form, outcome_id=outcome_id)

# function to delete outcome
@finance_bp.route('/delete_outcome/<int:outcome_id>', methods=['POST'])
def delete_outcome(outcome_id):
    # check if the user is logged in
    if 'user_id' not in session:
        return jsonify({'message': 'Please log in to delete outcomes.'}), 401
    
    outcome = Outcome.query.filter_by(ID=outcome_id, UserID=session['user_id']).first()
    if outcome:
        db.session.delete(outcome)
        db.session.commit()
        flash('Outcome deleted successfully!')
    else:
        flash('Outcome not found or you do not have permission to delete it.')
    
    return redirect(url_for('finance.outcomes'))