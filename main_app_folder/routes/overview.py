from flask import jsonify, redirect, render_template, url_for, session, flash, session
# from main_app_folder.models import User  # Assuming you have the User model
from main_app_folder.utils import helpers
from main_app_folder.utils import functions

def init_app(app):
    @app.route('/view_finances')
    def view_finances():
        if 'user_id' not in session:
            flash('Please log in to view your finances.')
            return redirect(url_for('login'))
        
        user_id = session['user_id']

        # Connect to the database
        conn = helpers.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM outcomes WHERE UserID = ? AND Type = 'Expense'", user_id)
        expenses = cursor.fetchall()

        cursor.execute("SELECT DISTINCT Name FROM outcomes WHERE UserID = ? AND Type = 'Expense'", user_id)
        categories = [row.Name for row in cursor.fetchall()]

        amounts = {}
        for category in categories:
            cursor.execute("SELECT SUM(Cost) FROM outcomes WHERE UserID = ? AND Type = 'Expense' AND Name = ?", (user_id, category))
            amounts[category] = cursor.fetchone()[0] or 0

        expenses_graph = functions.create_bar_chart(list(amounts.values()), categories)
        
        cursor.execute("SELECT * FROM outcomes WHERE UserID = ? AND Type = 'Income'", user_id)
        incomes = cursor.fetchall()

        cursor.execute("SELECT DISTINCT Name FROM outcomes WHERE UserID = ? AND Type = 'Income'", user_id)
        categories = [row.Name for row in cursor.fetchall()]

        amounts = {}
        for category in categories:
            cursor.execute("SELECT SUM(Cost) FROM outcomes WHERE UserID = ? AND Type = 'Income' AND Name = ?", (user_id, category))
            amounts[category] = cursor.fetchone()[0] or 0

        incomes_graph = functions.create_bar_chart(list(amounts.values()), categories)

        cursor.execute("SELECT * FROM outcomes WHERE UserID = ? AND Type = 'Saving'", user_id)
        savings = cursor.fetchall()

        cursor.execute("SELECT DISTINCT Name FROM outcomes WHERE UserID = ? AND Type = 'Saving'", user_id)
        categories = [row.Name for row in cursor.fetchall()]

        amounts = {}
        for category in categories:
            cursor.execute("SELECT SUM(Cost) FROM outcomes WHERE UserID = ? AND Type = 'Saving' AND Name = ?", (user_id, category))
            amounts[category] = cursor.fetchone()[0] or 0

        savings_graph = functions.create_bar_chart(list(amounts.values()), categories)

        cursor.execute("SELECT * FROM outcomes WHERE UserID = ? AND Type = 'Subscription'", user_id)
        subscriptions = cursor.fetchall()

        cursor.execute("SELECT DISTINCT Name FROM outcomes WHERE UserID = ? AND Type = 'Subscription'", user_id)
        categories = [row.Name for row in cursor.fetchall()]

        amounts = {}
        for category in categories:
            cursor.execute("SELECT SUM(Cost) FROM outcomes WHERE UserID = ? AND Type = 'Subscription' AND Name = ?", (user_id, category))
            amounts[category] = cursor.fetchone()[0] or 0

        subscriptions_graph = functions.create_bar_chart(list(amounts.values()), categories)

        cursor.close()
        conn.close()
        
        return render_template('view_finances.html', expenses=expenses, expenses_graph=expenses_graph, incomes=incomes, incomes_graph=incomes_graph, savings=savings, savings_graph=savings_graph, subscriptions=subscriptions, subscriptions_graph=subscriptions_graph)
