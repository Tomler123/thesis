from flask import Blueprint, redirect, render_template, url_for, session, flash
from main_app_folder.models.user import User
from main_app_folder.models.outcomes import Outcome
from main_app_folder.utils import functions
from collections import defaultdict

overview_bp = Blueprint('overview', __name__)

# financial overview
@overview_bp.route('/view_finances')
def view_finances():
    # check if the user is logged in
    if 'user_id' not in session:
        flash('Please log in to view your finances.')
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])
    if not user:
        flash('User not found.')
        return redirect(url_for('auth.login'))
    
    # these are all types for outcomes
    outcome_types = ['Expense', 'Income', 'Saving', 'Subscription']
    
    outcomes = {outcome_type: [] for outcome_type in outcome_types}
    chart_data = {}

    # for each outcome data is fetched and bar chart created in this loop below
    for outcome_type in outcome_types:
        category_totals = defaultdict(int)
        for outcome in Outcome.query.filter_by(UserID=user.UserID, Type=outcome_type).all():
            category_totals[outcome.Name] += outcome.Cost
            outcomes[outcome_type].append(outcome)
        
        if category_totals:
            chart_data[outcome_type] = functions.create_bar_chart(
                list(category_totals.values()),
                list(category_totals.keys())
            )
        else:
            chart_data[outcome_type] = functions.create_bar_chart(list(),list())

    return render_template(
        'view_finances.html',
        incomes=outcomes['Income'], incomes_graph=chart_data['Income'],
        savings=outcomes['Saving'], savings_graph=chart_data['Saving'],
        expenses=outcomes['Expense'], expenses_graph=chart_data['Expense'],
        subscriptions=outcomes['Subscription'], subscriptions_graph=chart_data['Subscription']
    )
