from flask import Flask, jsonify, redirect, request, render_template, url_for, session, flash, session
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask_sqlalchemy import SQLAlchemy
import io
from io import BytesIO
import base64
import pyodbc
import urllib
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField, validators, SelectField, FloatField, IntegerField, DateField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, NumberRange, InputRequired
import math
import algo
from flask_wtf.csrf import CSRFProtect
import json
import datetime

# server = 'TOMLER'  # If a local instance, typically 'localhost\\SQLEXPRESS'
# database = 'thesis'  # Your database name

# For Windows Authentication
# conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};TRUSTED_CONNECTION=yes'

# Tomleras database route
# C:\Program Files (x86)\Microsoft SQL Server Management Studio 19

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Configure Database URI: 
server = 'walletbuddyai.database.windows.net'
database = 'walletbuddyai'
username = 'toma_sulava_sulaberidze'
password = 'Tomler123,./'
driver= '{ODBC Driver 17 for SQL Server}'

conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=walletbuddyai.database.windows.net;"
    "DATABASE=walletbuddyai;"
    "UID=toma_sulava_sulaberidze;"
    "PWD=Tomler123,./;"
)

app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect={params}"
csrf = CSRFProtect(app)
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

################################################################

################################################################
# ??????????????????????

@app.route('/financial-position')
def financial_position():    
    return render_template('financial-position.html')

################################################################
# ??????????????????????
# Define form class
class StockPredictionForm(FlaskForm):
    stock_name = StringField('Stock Name', validators=[DataRequired()])
    submit = SubmitField('Get Graph')

@app.route('/stock_crypto_prediction', methods=['GET', 'POST'])
def stock_crypto_prediction():
    # Create an instance of the form class
    form = StockPredictionForm()

    if form.validate_on_submit():
        # Get the stock name from the form
        stock_name = form.stock_name.data
        
        # Call the main function from algo.py with stock_name
        # It should save the images in the static/images/ directory
        algo.main(stock_name)

        # Construct paths to the images
        loss_plot_path = 'images/loss_plot.png'
        predictions_plot_path = 'images/predictions_plot.png'
        extended_predictions_plot_path = 'images/extended_predictions_plot.png'
        
        # Render the template with the paths to the generated images
        return render_template('stock_crypto_prediction.html',
                               stock_name=stock_name,
                               loss_plot_path=loss_plot_path,
                               predictions_plot_path=predictions_plot_path,
                               extended_predictions_plot_path=extended_predictions_plot_path,
                               form=form)
    
    # If it's a GET request or the form is not valid, render the form
    return render_template('stock_crypto_prediction.html', form=form)

################################################################
# Login Signup
class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=30),
        Regexp(r'(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]', message='Password must contain at least one uppercase letter, one number, and one symbol.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Sign Up')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    
    if form.validate_on_submit():
        name = form.name.data
        last_name = form.last_name.data
        email = form.email.data
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        role = 'user'
        profile_image = 'none'
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute("SELECT * FROM users WHERE Email = ?", email)
        if cursor.fetchone():
            flash('Email already registered. Please login or use a different email.', 'error')
            return redirect(url_for('signup'))

        # If email does not exist, proceed with registration
        cursor.execute("""
            INSERT INTO users (Name, LastName, Email, Password, Role, ProfileImage)
            VALUES (?, ?, ?, ?, ?, ?)
        """, name, last_name, email, hashed_password, role, profile_image)

        # Fetch the new user's ID
        cursor.execute("SELECT UserID FROM users WHERE Email = ?", email)
        user_id = cursor.fetchone()[0]

        # Insert initial income record with zeros
        cursor.execute("""
            INSERT INTO incomes (UserID, Salary, Bonuses, Investment, PassiveIncome, Other)
            VALUES (?, 0, 0, 0, 0, 0)
            """, user_id)

        cursor.execute("""
            INSERT INTO fixed_expenses (UserID, Rent, TransportPass, Education, Insurance, Other)
            VALUES (?, 0, 0, 0, 0, 0)
            """, user_id)        

        cursor.execute("""
            INSERT INTO savings (UserID, Emergency, Retirement, Education, GoalSpecific, Health, Investment, Other)
            VALUES (?, 0, 0, 0, 0, 0, 0, 0)
            """, user_id)
        
        conn.commit()
        cursor.close()
        conn.close()

        flash('You have successfully signed up!', 'success')
        return redirect(url_for('account'))

    return render_template('signup.html', form=form)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=30)
    ])
    
    submit = SubmitField('Log In')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'POST':
        email = request.form.get('email')  # Use the .get method to avoid KeyError
        password = request.form.get('password')

        # Connect to the database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Find user by email
        cursor.execute("SELECT UserID, Password FROM users WHERE Email = ?", email)
        user = cursor.fetchone()

        # Close cursor and connection
        cursor.close()
        conn.close()

        # If user exists and password matches
        if user and check_password_hash(user.Password, password):
            session['user_id'] = user.UserID  # Store the user's ID in the session
            return redirect(url_for('account'))  # Redirect to the user's account page
        else:
            flash('Invalid email or password')


    return render_template('login.html', form=form)

# #########################################################################
# ACCOUNT AND LOGOUT MUST BE COMPLETED
class IconForm(FlaskForm):
    selected_icon = StringField('Selected Icon', validators=[DataRequired()])
    submit = SubmitField('Submit')

@app.route('/update_icon', methods=['POST'])
def update_icon():
    if 'user_id' in session:
        user_id = session['user_id']
        selected_icon = request.form.get('selected_icon')

        try:
            conn = pyodbc.connect(conn_str)
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
        
        form = IconForm()

        # Connect to the database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        if form.validate_on_submit():  # Check if the form is submitted and validated
            selected_icon = form.selected_icon.data
            return update_icon()

        # Fetch user details
        cursor.execute("SELECT * FROM users WHERE UserID = ?", user_id)
        user_details = cursor.fetchone()

        # Check if user details were found
        if user_details:
            cursor.execute(f"SELECT * FROM incomes WHERE UserID = {user_id}")
            columns = [column[0] for column in cursor.description if column[0] != 'UserID']
            # Construct the SUM query string
            sum_columns = ' + '.join(columns)
            query = f"SELECT SUM({sum_columns}) AS total_income FROM incomes WHERE UserID = ?"
            # Execute the query
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            total_income = result.total_income if isinstance(result.total_income, int) else 0

            # Same for other tables
            # Saving
            cursor.execute(f"SELECT * FROM savings WHERE UserID = {user_id}")
            columns = [column[0] for column in cursor.description if column[0] != 'UserID']
            sum_columns = ' + '.join(columns)
            query = f"SELECT SUM({sum_columns}) AS total_saving FROM savings WHERE UserID = ?"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            total_saving = result.total_saving if isinstance(result.total_saving, int) else 0

            # Expenses
            # cursor.execute(f"SELECT * FROM fixed_expenses WHERE UserID = {user_id}")
            # columns = [column[0] for column in cursor.description if column[0] != 'UserID']
            # sum_columns = ' + '.join(columns)
            # query = f"SELECT SUM({sum_columns}) AS total_expenses FROM fixed_expenses WHERE UserID = ?"
            # cursor.execute(query, (user_id,))
            # result = cursor.fetchone()
            # total_expenses = result.total_expenses if isinstance(result.total_expenses, int) else 0

            cursor.execute("""
            SELECT SUM(Cost) AS total_expenses FROM outcomes 
            WHERE UserID = ? AND Type = 'Expense'
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

################################################################
# Finances

@app.route('/saving', methods=['GET','POST'])
def saving():
    if 'user_id' not in session:
        flash('Please log in to record your saving.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Assuming you have an authenticated user and user_id is stored in session
            user_id = session['user_id']
            emergency = request.form['emergency']
            retirement = request.form['retirement']
            education = request.form['education']
            goal = request.form['goal']
            health = request.form['health']
            investment = request.form['investment']
            other = request.form['other']
            
            # Connect to the database
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            # Insert the saving data
            cursor.execute("""
                INSERT INTO savings
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, emergency, retirement, education, goal, health, investment, other))  # Add other saving fields as needed

            # Commit the transaction and close the connection
            conn.commit()
            cursor.close()
            conn.close()

            flash('saving recorded successfully!')
        except pyodbc.Error as e:
            flash('An error occurred while recording saving.')
            print("Error in SQL:", e)
        
        return redirect(url_for('saving'))

    return render_template('saving.html')

def create_bar_chart(data, categories):
    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)
    axis.bar(categories, data)
    axis.set_xticklabels(categories, rotation=22)  # Rotate x-axis labels to prevent overlap
    buf = io.BytesIO()
    FigureCanvas(fig).print_png(buf)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@app.route('/view_finances')
def view_finances():
    if 'user_id' not in session:
        flash('Please log in to view your finances.')
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    # Connect to the database
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Fetch the income data
    cursor.execute("SELECT * FROM incomes WHERE UserID = ?", user_id)
    incomes = cursor.fetchall()
    
    # Fetch the savings data
    cursor.execute("SELECT * FROM savings WHERE UserID = ?", user_id)
    savings = cursor.fetchall()

    # Fetch the income data
    cursor.execute("SELECT * FROM incomes WHERE UserID = ?", user_id)
    income_data = cursor.fetchone()

    if income_data:
        categories = ['Salary', 'Bonuses', 'Investment', 'PassiveIncome', 'Others']
        amounts = [income_data.Salary, income_data.Bonuses, income_data.Investment, income_data.PassiveIncome, income_data.Other]
        income_graph = create_bar_chart(amounts, categories)
    
    cursor.execute("SELECT * FROM savings WHERE UserID = ?", user_id)
    saving_data = cursor.fetchone()

    if saving_data:
        categories = ['Emergency', 'Retirement', 'Education', 'GoalSpecific', 'Health', 'Investment', 'Others']
        amounts = [saving_data.Emergency, saving_data.Retirement, saving_data.Education, saving_data.GoalSpecific, saving_data.Health, saving_data.Investment, saving_data.Other]
        saving_graph = create_bar_chart(amounts, categories)
    
    cursor.close()
    conn.close()
    
    return render_template('view_finances.html', incomes=incomes, savings=savings, income_graph=income_graph, saving_graph=saving_graph, )

################################################################
# Create pie chart for saved data
def income_pie_chart(income_data):
    # Replacing NaN with 0
    for key, value in income_data.items():
        if math.isnan(value):
            income_data[key] = 0
    
    # Check if all values are zero
    if all(value == 0 for value in income_data.values()):
        # Handle this case by creating a placeholder chart or message
        # For example, return a specific image or a message indicating no data
        pass
    else:
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        # Assuming 'income_data' is a dictionary with your data
        axis.pie(
            [income_data['Salary'], income_data['Bonuses'], income_data['Investment'], income_data['PassiveIncome'], income_data['Other']],
            autopct='%1.1f%%'
        )
        return fig

@app.route('/incomes')
def incomes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM outcomes WHERE UserID = ? AND Type = 'Income'", user_id)
    incomes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('incomes.html', incomes=incomes)

@app.route('/add_income', methods=['GET', 'POST'])
def add_income():
    if 'user_id' not in session:
        flash('Please log in to add an income.')
        return redirect(url_for('login'))

    form = OutcomeForm()

    if form.validate_on_submit():
        name = form.name.data
        cost = form.cost.data
        day = form.day.data
        income_type = form.type.data
        user_id = session['user_id']

        # Add income to the database
        query = """INSERT INTO outcomes (UserID, Name, Cost, Day, Type)
                   VALUES (?, ?, ?, ?, ?)"""
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id, name, cost, day, income_type))
                conn.commit()

        flash('Income added successfully!')
        return redirect(url_for('incomes'))  # Redirect to the incomes overview page

    return render_template('add_income.html', form=form)
class EditIncomeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    cost = FloatField('Cost', validators=[DataRequired()])
    day = IntegerField('Day', validators=[DataRequired(), NumberRange(min=1, max=31)])

@app.route('/edit_income/<int:income_id>', methods=['GET', 'POST'])
def edit_income(income_id):
    if 'user_id' not in session:
        flash('Please log in to edit records.')
        return redirect(url_for('login'))

    form = EditIncomeForm()

    if form.validate_on_submit():
        name = form.name.data
        cost = form.cost.data
        day = form.day.data
        user_id = session['user_id']

        # Update income in the database
        query = """UPDATE outcomes SET Name=?, Cost=?, Day=? WHERE ID=? AND UserID=? AND Type='Income'"""
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (name, cost, day, income_id, user_id))
                conn.commit()

        flash('Income updated successfully!')
        return redirect(url_for('incomes'))  # Redirect to the incomes overview page

    else:
        # Fetch the current income data
        conn = pyodbc.connect(conn_str)
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
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM incomes WHERE ID = ? AND UserID = ?", (income_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Income deleted successfully!')
        return redirect(url_for('incomes'))
    except Exception as e:
        return jsonify({'message': 'An error occurred while deleting the income.'}), 500

def saving_pie_chart(saving_data):
    for key, value in saving_data.items():
        if math.isnan(value):
            saving_data[key] = 0    
    if all(value == 0 for value in saving_data.values()):
        pass
    else:
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        axis.pie(
            [saving_data['Emergency'], saving_data['Retirement'], saving_data['Education'], saving_data['GoalSpecific'], saving_data['Health'], saving_data['Investment'], saving_data['Other']],
            autopct='%1.1f%%'
        )
        return fig

class EditSavingForm(FlaskForm):
    emergency = DecimalField('Emergency', validators=[DataRequired()])
    retirement = DecimalField('Retirement', validators=[DataRequired()])
    education = DecimalField('Education', validators=[DataRequired()])
    goal_specific = DecimalField('Goal Specific', validators=[DataRequired()])
    health = DecimalField('Health', validators=[DataRequired()])
    investment = DecimalField('Investment', validators=[DataRequired()])
    other = DecimalField('Other', validators=[DataRequired()])
    submit = SubmitField('Update')

@app.route('/edit_saving', methods=['GET', 'POST'])
def edit_saving():
    if 'user_id' not in session:
        flash('Please log in to edit records.')
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    form = EditSavingForm()

    if request.method == 'POST' or form.validate_on_submit():
        emergency = form.emergency.data
        retirement = form.retirement.data
        education = form.education.data
        goal_specific = form.goal_specific.data
        health = form.health.data
        investment = form.investment.data
        other = form.other.data

        cursor.execute("""
            UPDATE savings SET
            Emergency = ?,
            Retirement = ?,
            Education = ?,
            GoalSpecific = ?,
            Health = ?,
            Investment = ?,
            Other = ?
            WHERE UserID = ?
        """, (emergency, retirement, education, goal_specific, health, investment, other, user_id))

        conn.commit()
        flash('Savings updated successfully!')
        return redirect(url_for('view_finances'))
    else:
        cursor.execute("SELECT * FROM savings WHERE UserID = ?", user_id)
        saving_data = cursor.fetchone()
        
        if saving_data:
            form.emergency.data = saving_data[1]
            form.retirement.data = saving_data[2]
            form.education.data = saving_data[3]
            form.goal_specific.data = saving_data[4]
            form.health.data = saving_data[5]
            form.investment.data = saving_data[6]
            form.other.data = saving_data[7]

            total_sum = sum([
                form.emergency.data,
                form.retirement.data,
                form.education.data,
                form.goal_specific.data,
                form.health.data,
                form.investment.data,
                form.other.data
            ])
            
            saving_dict = {
                'Emergency' : form.emergency.data,
                'Retirement' : form.retirement.data,
                'Education' : form.education.data,
                'GoalSpecific' : form.goal_specific.data,
                'Health' : form.health.data,
                'Investment' : form.investment.data,
                'Other' : form.other.data
            }

            pie_chart = saving_pie_chart(saving_dict)
            png_output = BytesIO()
            FigureCanvas(pie_chart).print_png(png_output)
            png_output.seek(0)
            chart_url = base64.b64encode(png_output.getvalue()).decode('ascii')

            return render_template('edit_saving.html', form=form, chart_url=chart_url, total_sum=total_sum)
        else:
            flash('No saving data found.')
            return redirect(url_for('account'))

@app.route('/outcomes')
def outcomes():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM outcomes WHERE UserID = ?", user_id)
    outcomes = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('outcomes.html', outcomes=outcomes)

class OutcomeForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    cost = FloatField('Cost', validators=[InputRequired(), NumberRange(min=0)])
    day = IntegerField('Day', validators=[InputRequired(), NumberRange(min=1, max=31)])
    type = SelectField('Type', choices=[('Expense', 'Expense'), ('Subscription', 'Subscription')], validators=[InputRequired()])

@app.route('/add_outcome', methods=['GET', 'POST'])
def add_outcome():
    if 'user_id' not in session:
        flash('Please log in to add an outcome.')
        return redirect(url_for('login'))

    form = OutcomeForm()

    if form.validate_on_submit():
        name = form.name.data
        cost = form.cost.data
        day = form.day.data
        outcome_type = form.type.data
        user_id = session['user_id']

        # Add outcome to database
        query = """INSERT INTO outcomes (UserID, Name, Cost, Day, Type, Year, Month, Fulfilled)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id, name, cost, day, outcome_type, datetime.date.today().year, datetime.date.today().month, 0))
                conn.commit()
        flash('Outcome added successfully!')
        return redirect(url_for('outcomes'))  # Redirect to the outcomes overview page

    return render_template('add_outcome.html', form=form)

class EditOutcomeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    cost = FloatField('Cost', validators=[DataRequired()])
    day = IntegerField('Day', validators=[DataRequired(), NumberRange(min=1, max=31)])
    type = SelectField('Type', choices=[('Expense', 'Expense'), ('Subscription', 'Subscription')], validators=[DataRequired()])

@app.route('/edit_outcome/<int:outcome_id>', methods=['GET', 'POST'])
def edit_outcome(outcome_id):
    if 'user_id' not in session:
        flash('Please log in to edit records.')
        return redirect(url_for('login'))

    form = EditOutcomeForm()

    if form.validate_on_submit():
        name = form.name.data
        cost = form.cost.data
        day = form.day.data
        outcome_type = form.type.data
        user_id = session['user_id']

        # Update outcome in the database
        query = """UPDATE outcomes SET Name=?, Cost=?, Day=?, Type=? WHERE ID=? AND UserID=?"""
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (name, cost, day, outcome_type, outcome_id, user_id))
                conn.commit()

        flash('Outcome updated successfully!')
        return redirect(url_for('outcomes'))  # Redirect to the outcomes overview page

    else:
        # Fetch the current outcome data
        conn = pyodbc.connect(conn_str)
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
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM outcomes WHERE ID = ? AND UserID = ?", (outcome_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Outcome deleted successfully!')
        return redirect(url_for('outcomes'))
    except Exception as e:
        return jsonify({'message': 'An error occurred while deleting the outcome.'}), 500

################################################################
# Loans
@app.route('/loans')
def loans():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM loans WHERE UserID = ? AND IsBorrower = 1", user_id)
    borrowed_loans = cursor.fetchall()

    cursor.execute("SELECT * FROM loans WHERE UserID = ? AND IsBorrower = 0", user_id)
    lent_loans = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('loans.html', borrowed_loans=borrowed_loans, lent_loans=lent_loans)

class AddLoanForm(FlaskForm):
    lender_name = StringField('Lender/Borrower Name', validators=[InputRequired()])
    loan_amount = DecimalField('Loan Amount', validators=[InputRequired(), NumberRange(min=0)])
    interest_rate = DecimalField('Interest Rate (%)', validators=[InputRequired(), NumberRange(min=0)])
    monthly_payment = DecimalField('Monthly Payment', validators=[InputRequired(), NumberRange(min=0)])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[InputRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[InputRequired()])
    remaining_balance = DecimalField('Remaining Balance', validators=[InputRequired(), NumberRange(min=0)])
    is_borrower = SelectField('Are you the borrower?', choices=[('1', 'Yes'), ('0', 'No')], validators=[InputRequired()])
    notes = TextAreaField('Notes')

@app.route('/add_loan', methods=['GET', 'POST'])
def add_loan():
    if 'user_id' not in session:
        flash('Please log in to add a loan.')
        return redirect(url_for('login'))

    form = AddLoanForm()
    if form.validate_on_submit():
        # Form data is valid, proceed to add the loan
        lender_name = form.lender_name.data
        loan_amount = form.loan_amount.data
        interest_rate = form.interest_rate.data
        monthly_payment = form.monthly_payment.data
        start_date = form.start_date.data
        due_date = form.due_date.data
        remaining_balance = form.remaining_balance.data
        is_borrower = form.is_borrower.data
        notes = form.notes.data
        user_id = session['user_id']

        # Add loan to database
        # Assuming conn is your database connection
        query = """INSERT INTO loans (UserID, LenderName, LoanAmount, InterestRate, MonthlyPayment, StartDate, DueDate, RemainingBalance,IsBorrower, Notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id, lender_name, loan_amount, interest_rate, monthly_payment, start_date, due_date, remaining_balance, is_borrower, notes))
                conn.commit()

        flash('Loan added successfully!')
        return redirect(url_for('loans'))  # Redirect to the loans overview page

    return render_template('add_loan.html', form=form)

class EditLoanForm(FlaskForm):
    lender_name = StringField('Lender Name', validators=[DataRequired(), Length(max=100)])
    loan_amount = FloatField('Loan Amount', validators=[DataRequired(), NumberRange(min=0)])
    interest_rate = FloatField('Interest Rate', validators=[DataRequired(), NumberRange(min=0)])
    monthly_payment = FloatField('Monthly Payment', validators=[DataRequired(), NumberRange(min=0)])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    due_date = DateField('Due Date', validators=[DataRequired()], format='%Y-%m-%d')
    remaining_balance = FloatField('Remaining Balance', validators=[DataRequired(), NumberRange(min=0)])
    is_borrower = SelectField('Are you borrower', choices=[('1', 'Yes'), ('0', 'No')], coerce=int)
    notes = StringField('Other', validators=[DataRequired(), Length(max=255)])
    submit = SubmitField('Update')

@app.route('/edit_loan/<int:loan_id>', methods=['GET', 'POST'])
def edit_loan(loan_id):
    # Check if user is logged in
    if 'user_id' not in session:
        flash('Please log in to edit records.')
        return redirect(url_for('login'))

    # Connect to your database
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    form = EditLoanForm()

    if request.method == 'POST' and form.validate_on_submit():
        lender_name = form.lender_name.data
        loan_amount = form.loan_amount.data
        interest_rate = form.interest_rate.data
        monthly_payment = form.monthly_payment.data
        start_date = form.start_date.data
        due_date = form.due_date.data
        remaining_balance = form.remaining_balance.data
        is_borrower = form.is_borrower.data
        notes = form.notes.data

        # Update the loan details in the database
        update_query = """UPDATE loans SET LenderName=?, LoanAmount=?, InterestRate=?, MonthlyPayment=?,StartDate=?, DueDate=?, RemainingBalance=?, IsBorrower=?, Notes=? WHERE LoanID=?"""
        cursor.execute(update_query, (lender_name, loan_amount, interest_rate, monthly_payment, start_date, due_date, remaining_balance, is_borrower, notes, loan_id))
        conn.commit()

        # Redirect to a confirmation page or back to the loan list
        return redirect(url_for('loans'))

    else:
        # For a GET request, fetch the loan's current details to prefill the form
        cursor.execute("SELECT * FROM loans WHERE LoanID=?", (loan_id,))
        loan = cursor.fetchone()

        form.lender_name.data = loan.LenderName
        form.loan_amount.data = loan.LoanAmount
        form.interest_rate.data = loan.InterestRate
        form.monthly_payment.data = loan.MonthlyPayment
        form.start_date.data = loan.StartDate
        form.due_date.data = loan.DueDate
        form.remaining_balance.data = loan.RemainingBalance
        form.is_borrower.data = loan.IsBorrower
        form.notes.data = loan.Notes

        # Render the edit page template with the loan details
        return render_template('edit_loan.html', form=form)

@app.route('/delete_loan/<int:loan_id>', methods=['POST'])
def delete_loan(loan_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Please log in to delete loans.'}), 401
    
    try:
        user_id = session['user_id']
        # Ensure that the user deleting the loan is the owner
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM loans WHERE LoanID = ? AND UserID = ?", (loan_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Loan deleted successfully!')
        return redirect(url_for('loans'))
    except Exception as e:
        return jsonify({'message': 'An error occurred while deleting the loan.'}), 500

################################################################
# Subscriptions
@app.route('/subscriptions')
def subscriptions():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM subscriptions WHERE UserID = ?", user_id)
    subscriptions = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('subscriptions.html', subscriptions=subscriptions)

class SubscriptionForm(FlaskForm):
    name = StringField('Service Name', validators=[InputRequired()])
    cost = DecimalField('Cost (Monthly)', validators=[InputRequired(), NumberRange(min=0)])
    date = DecimalField('Date (Day of month)', validators=[InputRequired(), NumberRange(min=1, max=31)])

@app.route('/add_subscription', methods=['GET', 'POST'])
def add_subscription():
    if 'user_id' not in session:
        flash('Please log in to add a subscription.')
        return redirect(url_for('login'))

    form = SubscriptionForm()

    if form.validate_on_submit():
        name = form.name.data
        cost = form.cost.data
        date = form.date.data
        user_id = session['user_id']

        current_year = datetime.date.today().year
        current_month = datetime.date.today().month
        print(current_year)
        print(current_month)
        
        # Add subscription to database
        query = """INSERT INTO subscriptions (UserID, Name, Cost, Date)
                   VALUES (?, ?, ?, ?)"""
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id, name, cost, date))
                conn.commit()
                
                # Insert a row into fulfilled_subscriptions
                subscription_id = cursor.execute("SELECT @@IDENTITY").fetchval()
                insert_fulfilled_query = """INSERT INTO fulfilled_subscriptions (SubscriptionID, Fulfilled, Year, Month)
                                            VALUES (?, ?, ?, ?)"""
                cursor.execute(insert_fulfilled_query, (subscription_id, 0, current_year, current_month))
                conn.commit()

        flash('Subscription added successfully!')
        return redirect(url_for('subscriptions'))  # Redirect to the subscriptions overview page

    return render_template('add_subscription.html', form=form)

class EditSubscriptionForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    cost = DecimalField('Cost', validators=[DataRequired()])
    submit = SubmitField('Update')

@app.route('/edit_subscription/<int:subscription_id>', methods=['GET', 'POST'])
def edit_subscription(subscription_id):
    if not session.get('user_id'):
        flash('Please log in to edit records.')
        return redirect(url_for('login'))

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    form = EditSubscriptionForm()

    try:
        if request.method == 'POST' and form.validate_on_submit():
            name = form.name.data
            cost = form.cost.data
            
            update_query = """UPDATE subscriptions SET Name=?, Cost=? WHERE SubscriptionID=?"""
            cursor.execute(update_query, (name, cost, subscription_id))
            conn.commit()
            flash('Subscription updated successfully!')
            return redirect(url_for('subscriptions'))
        else:
            cursor.execute("SELECT * FROM subscriptions WHERE SubscriptionID=?", (subscription_id,))
            subscription = cursor.fetchone()
            if subscription:
                form.name.data = subscription.Name
                form.cost.data = subscription.Cost
                return render_template('edit_subscription.html', form=form)
            else:
                flash('Subscription not found.')
                return redirect(url_for('subscriptions'))
    except Exception as e:
        flash(f'An error occurred: {e}')
    finally:
        cursor.close()
        conn.close()

    return render_template('edit_subscription.html', form=form)

@app.route('/delete_subscription/<int:subscription_id>', methods=['POST'])
def delete_subscription(subscription_id):
    if 'user_id' not in session:
        return jsonify({'message': 'Please log in to delete subscriptions.'}), 401
    
    try:
        user_id = session['user_id']
        # Ensure that the user deleting the subscription is the owner
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM subscriptions WHERE SubscriptionID = ? AND UserID = ?", (subscription_id, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Subscription deleted successfully!')
        return redirect(url_for('subscriptions'))
    except Exception as e:
        return jsonify({'message': 'An error occurred while deleting the subscription.'}), 500

class RecommendationsForm(FlaskForm):
    savings_goal = IntegerField('Savings Goal', validators=[NumberRange(min=0, max=100, message="Value must be between 0 and 100.")])
    submit = SubmitField('Get Recommendations')

@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    if 'user_id' not in session:
        flash('Please log in to access recommendations.')
        return redirect(url_for('login'))
    form = RecommendationsForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        user_id = session['user_id']    
        # Connect to the database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Calculating total monthly debt
        cursor.execute("SELECT sum(MonthlyPayment) FROM loans WHERE UserID = ? and IsBorrower = 1", user_id)
        total_monthly_debt_data = cursor.fetchone()[0]
        if total_monthly_debt_data is not None:
            total_monthly_debt = float(total_monthly_debt_data)
        else:
            total_monthly_debt = 0
        
        cursor.execute("SELECT sum(MonthlyPayment) FROM loans WHERE UserID = ? and IsBorrower = 0", user_id)
        total_expected_loan_data = cursor.fetchone()[0]
        if total_expected_loan_data is not None:
            total_expected_loan = float(total_expected_loan_data)
        else:
            total_expected_loan = 0
        
        cursor.execute("SELECT sum(Cost) FROM subscriptions WHERE UserID = ?", user_id)
        total_subscription_data = cursor.fetchone()[0]
        if total_subscription_data is not None:
            total_subscriptions = float(total_subscription_data)
        else:
            total_subscriptions = 0
        
        # Calculating total fixed expenses
        cursor.execute("SELECT * FROM fixed_expenses WHERE UserID = ?", user_id)
        expenses_data = cursor.fetchone()
        fixed_expenses = {
            "Rent" : round(expenses_data.Rent,2),
            "Transport" : round(expenses_data.TransportPass,2),
            "Education" : round(expenses_data.Education,2), # OTHER, CHANGE TO EDUCATION LATER IN TABLE
            "Insurance" : round(expenses_data.Insurance,2),
            "Debt" : round(total_monthly_debt,2), # PROCESS LOAN TABLE
            "Subscriptions" : round(total_subscriptions,2),
        }

        fixed_total = sum([b for (a,b) in fixed_expenses.items()])
        savings_goal_percentage = float(request.form.get('savings_goal'))
        print(fixed_total)
        # Calculating total income
        
        cursor.execute(f"SELECT * FROM incomes WHERE UserID = {user_id}")
        columns = [column[0] for column in cursor.description if column[0] != 'UserID']
        sum_columns = ' + '.join(columns)
        query = f"SELECT SUM({sum_columns}) AS total_income FROM incomes WHERE UserID = ?"
        # Execute the query
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        total_income = result.total_income if isinstance(result.total_income, int) else 0

        if total_income <= 0:
            cursor.close()
            conn.close()
            return render_template('recommendations.html', form=form, error = "You have not entered income details. Please fill in all the necessary data. You can find link through 'Navigation Menu'=>'Finances'=>'Edit Income'")
        elif fixed_total > total_income:
            cursor.close()
            conn.close()
            return render_template('recommendations.html',form=form, error = f"Total income ({total_income}) is less than total fixed expenses ({fixed_total})")
        elif total_income*(1-(savings_goal_percentage/100)) - fixed_total < 0:
            cursor.close()
            conn.close()
            return render_template('recommendations.html',form=form, error = f"Can't save {savings_goal_percentage}%, because of high amount of total fixed expenses ({fixed_total}) compared to total income ({total_income})")
        else:
            savings_amount = total_income*(1-(savings_goal_percentage/100)) - fixed_total
            daily_spending_limit = round(savings_amount/30,2)

            
            # Calculate recommendations for spending
            recommendations = {
                'groceries': round(daily_spending_limit * 0.15, 2), 
                'healthcare': round(daily_spending_limit * 0.05, 2), 
                'transportation': round(daily_spending_limit * 0.1, 2), 
                'personal': round(daily_spending_limit * 0.05, 2), 
                'pets': round(daily_spending_limit * 0.03, 2), 
                'entertainment': round(daily_spending_limit * 0.05, 2), 
            }
            fulfilled_status = {}
            cursor.execute("SELECT * FROM expenses WHERE UserID = ?", user_id)
            f_data = cursor.fetchone()
            if f_data:
                # Assuming the table structure matches the dictionary keys
                for category, fulfilled in zip(fixed_expenses.keys(), f_data[1:]):
                    if fulfilled == 1:
                        fulfilled_status[category] = 'Fulfilled'
                    else:
                        fulfilled_status[category] = 'Unfulfilled'
            else:
                # Default to 'Unfulfilled' if no data found
                fulfilled_status = {category: 'Unfulfilled' for category in fixed_expenses.keys()}
            cursor.close()
            conn.close()
            return render_template('recommendations.html', form=form, fixed_expenses=fixed_expenses,
                                   recommendations=recommendations, fixed=fixed_total,
                                   daily=daily_spending_limit, monthly=savings_amount,
                                   total_expected_loan=total_expected_loan, fulfilled_status=fulfilled_status)
    else:
        # GET request, just render the form
        return render_template('recommendations.html', form=form)

################################################################

################################################################

@app.route('/contact')
def contact():
    return render_template('contact_us.html')

################################################################
# Calendar
# @app.route('/calendar')
# def calendar():
#     # Assuming you have the user_id from the session
#     user_id = session.get('user_id')
#     if not user_id:
#         return redirect(url_for('login'))
    
#     # Connect to the database
#     conn = pyodbc.connect(conn_str)
#     cursor = conn.cursor()
    
#     # Fetch both subscription and expense dates
#     cursor.execute("""
#         SELECT Date AS date FROM subscriptions WHERE UserID=?
#         UNION
#         SELECT DueDate AS date FROM expenses WHERE UserID=?
#     """, (user_id, user_id))
    
#     # Fetch all dates from the cursor
#     all_dates = [row.date for row in cursor.fetchall()]
    
#     # Close the connection
#     cursor.close()
#     conn.close()

#     # Render the calendar template and pass the dates
#     return render_template('calendar.html', all_dates=json.dumps(all_dates))

@app.route('/calendar')
def calendar():
    # Assuming you have the user_id from the session
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    # Connect to the database
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()
    
    # Fetch both subscription and expense dates
    cursor.execute("""
        SELECT Day AS date FROM outcomes WHERE UserID=?
    """, (user_id))
    
    # Fetch all dates from the cursor
    all_dates = [row.date for row in cursor.fetchall()]
    
    # Close the connection
    cursor.close()
    conn.close()

    # Render the calendar template and pass the dates
    return render_template('calendar.html', all_dates=json.dumps(all_dates))

@app.route('/get_subscriptions', methods=['POST'])
def get_subscriptions():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    day_clicked = request.json.get('day')
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT ID, Name, Cost, Fulfilled
        FROM outcomes
        WHERE UserID = ? AND Day = ? AND Month = MONTH(GETDATE()) AND Year = YEAR(GETDATE())
    """, (user_id, day_clicked))

    subscriptions = [
        {"id": row.ID, "name": row.Name, "amount": row.Cost, "fulfilled": bool(row.Fulfilled)}
        for row in cursor.fetchall()
    ]

    cursor.close()
    conn.close()

    return jsonify(subscriptions)

@app.route('/update_subscription_status', methods=['POST'])
def update_subscription_status():
    data = request.get_json()
    sub_id = data['sub_id']
    status = data['status']

    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE outcomes
            SET Fulfilled = ?
            WHERE ID = ? AND Year = YEAR(GETDATE()) AND Month = MONTH(GETDATE())
            """, (status, sub_id))

        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({'success': True, 'message': 'Status updated'})

@app.route('/get_subscription_status_by_day', methods=['POST'])
def get_subscription_status_by_day():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT Day, 
               CAST(CASE WHEN COUNT(Fulfilled) = SUM(CAST(Fulfilled AS INT)) THEN 1 ELSE 0 END AS BIT) AS AllFulfilled
        FROM outcomes
        WHERE UserID = ? AND Month = MONTH(GETDATE()) AND Year = YEAR(GETDATE())
        GROUP BY Day
    """, (user_id,))

    day_fulfillment_status = {str(row.Day): row.AllFulfilled for row in cursor.fetchall()}
    
    cursor.close()
    conn.close()

    return jsonify(day_fulfillment_status)
# @app.route('/get_finances', methods=['POST'])
# def get_finances():
#     user_id = session.get('user_id')
#     if not user_id:
#         return redirect(url_for('login'))

#     day_clicked = request.json.get('day')
#     conn = pyodbc.connect(conn_str)
#     cursor = conn.cursor()

#     # Query for outcomes
#     cursor.execute("""
#         SELECT ID, Name, Cost AS amount, 'Outcome' AS type, 1 AS fulfilled
#         FROM outcomes
#         WHERE UserID = ? AND Day = ?
#     """, (user_id, day_clicked))
#     outcomes = [
#         {"id": row.ID, "name": row.Name, "amount": row.amount, "type": row.type, "fulfilled": bool(row.fulfilled)}
#         for row in cursor.fetchall()
#     ]

#     cursor.close()
#     conn.close()

#     return jsonify(outcomes)


# @app.route('/update_finance_status', methods=['POST'])
# def update_finance_status():
#     data = request.get_json()
#     finance_id = data.get('finance_id')
#     status = data.get('status')

#     try:
#         conn = pyodbc.connect(conn_str)
#         cursor = conn.cursor()

#         # Update outcome fulfillment status
#         cursor.execute("""
#             UPDATE outcomes
#             SET Fulfilled = ?
#             WHERE ID = ? AND UserID = ?
#             """, (status, finance_id, session['user_id']))

#         conn.commit()
#         return jsonify({'success': True, 'message': 'Outcome status updated'})
#     except Exception as e:
#         conn.rollback()
#         return jsonify({'success': False, 'message': str(e)}), 500
#     finally:
#         cursor.close()
#         conn.close()

# @app.route('/get_finance_status_by_day', methods=['POST'])
# def get_finance_status_by_day():
#     user_id = session.get('user_id')
#     if not user_id:
#         return redirect(url_for('login'))

#     conn = pyodbc.connect(conn_str)
#     cursor = conn.cursor()

#     query = """
#     SELECT Day, MAX(CAST(Fulfilled AS INT)) AS AllFulfilled
#     FROM outcomes
#     WHERE UserID = ?
#     GROUP BY Day
#     """
#     cursor.execute(query, (user_id,))

#     # Fetch rows and convert the result into a dictionary
#     status_by_day = {str(row.Day): bool(row.AllFulfilled) for row in cursor.fetchall()}

#     cursor.close()
#     conn.close()

#     return jsonify(status_by_day)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
