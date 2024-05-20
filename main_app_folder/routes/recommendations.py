from flask import Blueprint, redirect, render_template, request, url_for, session, flash
from main_app_folder.forms import forms
from main_app_folder.utils import helpers

recommendations_bp = Blueprint('recommendations', __name__)

@recommendations_bp.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    if 'user_id' not in session:
        flash('Please log in to access recommendations.')
        return redirect(url_for('auth.login'))
    
    form = forms.RecommendationsForm()
    
    if form.validate_on_submit():
        user_id = session['user_id']
        
        # Connect to the database
        conn = helpers.get_db_connection()
        cursor = conn.cursor()
        
        # Calculating total monthly debt
        cursor.execute("SELECT SUM(MonthlyPayment) FROM loans WHERE UserID = ? AND IsBorrower = 1", (user_id,))
        total_monthly_debt_data = cursor.fetchone()[0]
        total_monthly_debt = float(total_monthly_debt_data) if total_monthly_debt_data is not None else 0
        
        cursor.execute("SELECT SUM(MonthlyPayment) FROM loans WHERE UserID = ? AND IsBorrower = 0", (user_id,))
        total_expected_loan_data = cursor.fetchone()[0]
        total_expected_loan = float(total_expected_loan_data) if total_expected_loan_data is not None else 0
        
        cursor.execute("""
            SELECT LenderName, MonthlyPayment, LoanAmount
            FROM loans
            WHERE UserID = ? AND IsBorrower = 0
        """, (user_id,))
        loan_data = cursor.fetchall()
        lent_loans = []
        total_lent_loan_amount = 0
        
        for name, monthly, total in loan_data:
            monthly = round(monthly, 2)
            total = round(total, 2)
            lent_loans.append({'name': name, 'monthly': monthly, 'total': total})
            total_lent_loan_amount += total
        
        cursor.execute("""
            SELECT LenderName, MonthlyPayment, LoanAmount
            FROM loans
            WHERE UserID = ? AND IsBorrower = 1
        """, (user_id,))
        loan_data = cursor.fetchall()
        borrowed_loans = []
        total_borrowed_loan_amount = 0
        
        for name, monthly, total in loan_data:
            monthly = round(monthly, 2)
            total = round(total, 2)
            borrowed_loans.append({'name': name, 'monthly': monthly, 'total': total})
            total_borrowed_loan_amount += total
        
        cursor.execute("""
            SELECT Name, Cost
            FROM outcomes 
            WHERE UserID = ? AND Type = 'Subscription'
        """, (user_id,))
        subscription_data = cursor.fetchall()
        subscriptions = {name: round(cost, 2) for name, cost in subscription_data}
        subscriptions_total = sum(subscriptions.values())
        
        cursor.execute("""
            SELECT Name, Cost
            FROM outcomes 
            WHERE UserID = ? AND Type = 'Expense'
        """, (user_id,))
        expense_data = cursor.fetchall()
        fixed_expenses = {name: round(cost, 2) for name, cost in expense_data}
        fixed_total = sum(fixed_expenses.values())
        
        savings_goal_percentage = float(request.form.get('savings_goal'))
        cursor.execute("""
        SELECT SUM(Cost) AS total_income FROM outcomes 
        WHERE UserID = ? AND Type = 'Income'
        """, (user_id,))
        result = cursor.fetchone()
        total_income = result[0] if result[0] else 0
        
        if total_income <= 0:
            cursor.close()
            conn.close()
            return render_template('recommendations.html', form=form, error="You have not entered income details. Please fill in all the necessary data. You can find link through 'Navigation Menu'=>'Finances'=>'Edit Income'")
        elif (fixed_total + subscriptions_total) > total_income:
            cursor.close()
            conn.close()
            return render_template('recommendations.html', form=form, error=f"Total income ({total_income}) is less than total fixed expenses ({fixed_total + subscriptions_total})")
        elif total_income * (1 - (savings_goal_percentage / 100)) - (fixed_total + subscriptions_total) < 0:
            cursor.close()
            conn.close()
            return render_template('recommendations.html', form=form, error=f"Can't save {savings_goal_percentage}%, because of high amount of total fixed expenses ({fixed_total + subscriptions_total}) compared to total income ({total_income})")
        else:
            savings_amount = total_income * (savings_goal_percentage / 100)
            available_amount = total_income - fixed_total - subscriptions_total - savings_amount
            daily_spending_limit = round(available_amount / 30, 2)
            category_names = request.form.getlist('category_name[]')
            priorities = request.form.getlist('priority[]')
            
            if not category_names:
                recommendations = {
                    'groceries': round(daily_spending_limit * 0.15, 2),
                    'healthcare': round(daily_spending_limit * 0.05, 2),
                    'transportation': round(daily_spending_limit * 0.1, 2),
                    'personal': round(daily_spending_limit * 0.05, 2),
                    'pets': round(daily_spending_limit * 0.03, 2),
                    'entertainment': round(daily_spending_limit * 0.05, 2),
                }
            else:
                priority_dict = {name: float(priority) for name, priority in zip(category_names, priorities)}
                total_priority = sum(priority_dict.values())
                available_funds = total_income * (1 - (savings_goal_percentage / 100)) - fixed_total - subscriptions_total
                recommendations = {name: round(available_funds * (priority / total_priority) / 30, 2) for name, priority in priority_dict.items()}
            
            cursor.execute("""
                SELECT Name, Fulfilled
                FROM outcomes 
                WHERE UserID = ? AND Type = 'Subscription'
            """, (user_id,))
            subscription_fulfillment_data = cursor.fetchall()
            
            cursor.execute("""
                SELECT Name, Fulfilled
                FROM outcomes 
                WHERE UserID = ? AND Type = 'Expense'
            """, (user_id,))
            expense_fulfillment_data = cursor.fetchall()
            fulfilled_status = {}
            
            for name, fulfilled in expense_fulfillment_data:
                fulfilled_status[name] = 'Fulfilled' if fulfilled == 1 else 'Unfulfilled'
            
            for name, fulfilled in subscription_fulfillment_data:
                fulfilled_status[name] = 'Fulfilled' if fulfilled == 1 else 'Unfulfilled'
            
            return render_template('recommendations.html', form=form, fixed_expenses=fixed_expenses, subscriptions=subscriptions,
                                   recommendations=recommendations, fixed=fixed_total, subscriptions_total=subscriptions_total,
                                   daily=daily_spending_limit, monthly=savings_amount, total_expected_loan=total_expected_loan,
                                   fulfilled_status=fulfilled_status, total_monthly_debt=total_monthly_debt,
                                   total_borrowed_loan_amount=total_borrowed_loan_amount, total_lent_loan_amount=total_lent_loan_amount,
                                   lent_loans=lent_loans, borrowed_loans=borrowed_loans)
    return render_template('recommendations.html', form=form)
