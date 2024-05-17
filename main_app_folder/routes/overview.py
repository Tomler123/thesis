from flask import Blueprint, jsonify, redirect, render_template, url_for, session, flash
from main_app_folder.models.user import User
from main_app_folder.models.outcomes import Outcome
from main_app_folder.utils import functions

overview_bp = Blueprint('overview', __name__)

@overview_bp.route('/view_finances')
def view_finances():
    if 'user_id' not in session:
        flash('Please log in to view your finances.')
        return redirect(url_for('auth.login'))
    
    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.')
        return redirect(url_for('auth.login'))
    
    expenses = Outcome.query.filter_by(UserID=user.UserID, Type='Expense').all()
    categories = set(expense.Name for expense in expenses)
    
    expenses_data = {category: sum(exp.Cost for exp in expenses if exp.Name == category) for category in categories}
    expenses_graph = functions.create_bar_chart(list(expenses_data.values()), list(categories))
    incomes = Outcome.query.filter_by(UserID=user.UserID, Type='Income').all()
    income_categories = set(income.Name for income in incomes)
    
    incomes_data = {category: sum(inc.Cost for inc in incomes if inc.Name == category) for category in income_categories}
    incomes_graph = functions.create_bar_chart(list(incomes_data.values()), list(income_categories))
    savings = Outcome.query.filter_by(UserID=user.UserID, Type='Saving').all()
    saving_categories = set(saving.Name for saving in savings)
    
    savings_data = {category: sum(sav.Cost for sav in savings if sav.Name == category) for category in saving_categories}
    savings_graph = functions.create_bar_chart(list(savings_data.values()), list(saving_categories))
    subscriptions = Outcome.query.filter_by(UserID=user.UserID, Type='Subscription').all()
    subscription_categories = set(subscription.Name for subscription in subscriptions)
    
    subscriptions_data = {category: sum(sub.Cost for sub in subscriptions if sub.Name == category) for category in subscription_categories}
    subscriptions_graph = functions.create_bar_chart(list(subscriptions_data.values()), list(subscription_categories))
    return render_template('view_finances.html', 
                           expenses=expenses, expenses_graph=expenses_graph, 
                           incomes=incomes, incomes_graph=incomes_graph, 
                           savings=savings, savings_graph=savings_graph, 
                           subscriptions=subscriptions, subscriptions_graph=subscriptions_graph)
