from flask import Flask, jsonify, redirect, request, render_template, url_for, session, flash, session
import matplotlib.pyplot as plt
from flask_sqlalchemy import SQLAlchemy
import io
import base64
import pyodbc
from werkzeug.security import check_password_hash, generate_password_hash
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp


app = Flask(__name__)
app.secret_key = 'tomler123'  # Needed for session management

server = 'TOMLER'  # If a local instance, typically 'localhost\\SQLEXPRESS'
database = 'thesis'  # Your database name
# username = 'your_username'  # Your SQL Server username, if using SQL Server authentication
# password = 'your_password'  # Your SQL Server password, if using SQL Server authentication

# For Windows Authentication
conn_str = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};TRUSTED_CONNECTION=yes'

# Example of creating a connection
conn = pyodbc.connect(conn_str)

# Tomleras database route
# C:\Program Files (x86)\Microsoft SQL Server Management Studio 19

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about_us.html')

################################################################
# SAMPLE TO DEMONSTRATE GRAPH
@app.route('/money_management_features', methods=['GET', 'POST'])
def money_management_features():
    image_base64 = None
    if request.method == 'POST':
        # Get the stock name from the form
        stock_name = request.form['stock_name']

        # Perform your calculation here
        # This is where you'd include your actual data fetching and graph generation logic
        plt.figure()
        plt.plot([1, 2, 3], [4, 5, 6]) # Replace with actual data
        plt.title(f'Stock Data for {stock_name}')

        # Save it to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Encode the image in base64 and remove the bytestring header
        image_base64 = base64.b64encode(buf.read()).decode('utf-8')
        buf.close()

    # Render the same page with the form and possibly the graph
    return render_template('money_management_features.html', image_base64=image_base64)

################################################################
# ??????????????????????
@app.route('/financial-position')
def financial_position():    
    return render_template('financial-position.html')

################################################################
# ??????????????????????
@app.route('/stock-crypto-prediction')
def stock_crypto_prediction():
    return render_template('stock_and_crypto_prediction.html')

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

        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO users (Name, LastName, Email, Password)
            VALUES (?, ?, ?, ?)
        """, name, last_name, email, hashed_password)

        conn.commit()
        cursor.close()
        conn.close()

        flash('You have successfully signed up!', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
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


    return render_template('login.html')


# #########################################################################
# ACCOUNT AND LOGOUT MUST BE COMPLETED

@app.route('/account')
def account():
    if 'user_id' in session:
        user_id = session['user_id']
        
        # Connect to the database
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        # Fetch user details
        cursor.execute("SELECT * FROM users WHERE UserID = ?", user_id)
        user_details = cursor.fetchone()

        # Check if user details were found
        if user_details:
            cursor.execute(f"SELECT * FROM income WHERE UserID = {user_id}")
            columns = [column[0] for column in cursor.description if column[0] != 'UserID']
            # Construct the SUM query string
            sum_columns = ' + '.join(columns)
            query = f"SELECT SUM({sum_columns}) AS total_income FROM income WHERE UserID = ?"
            # Execute the query
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            total_income = result.total_income if isinstance(result.total_income, int) else 0

            # Same for other tables
            # Saving
            cursor.execute(f"SELECT * FROM saving WHERE UserID = {user_id}")
            columns = [column[0] for column in cursor.description if column[0] != 'UserID']
            sum_columns = ' + '.join(columns)
            query = f"SELECT SUM({sum_columns}) AS total_saving FROM saving WHERE UserID = ?"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            total_saving = result.total_saving if isinstance(result.total_saving, int) else 0

            # Expenses
            cursor.execute(f"SELECT * FROM expenses WHERE UserID = {user_id}")
            columns = [column[0] for column in cursor.description if column[0] != 'UserID']
            sum_columns = ' + '.join(columns)
            query = f"SELECT SUM({sum_columns}) AS total_expenses FROM expenses WHERE UserID = ?"
            cursor.execute(query, (user_id,))
            result = cursor.fetchone()
            total_expenses = result.total_expenses if isinstance(result.total_expenses, int) else 0

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
            return render_template('account.html', user=user_details, total_saving=total_saving, total_income=total_income, total_expenses=total_expenses, total_borrowed=total_borrowed, total_lent=total_lent)
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

@app.route('/income', methods=['GET','POST'])
def income():
    if 'user_id' not in session:
        flash('Please log in to record your income.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Assuming you have an authenticated user and user_id is stored in session
            user_id = session['user_id']
            salary = request.form['salary']
            bonuses = request.form['bonuses']
            passive = request.form['passive']
            business = request.form['business']
            investment = request.form['investment']
            other = request.form['other']
            
            # Connect to the database
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            # Insert the income data
            cursor.execute("""
                INSERT INTO income
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, salary, bonuses, passive, business, investment, other))  # Add other income fields as needed

            # Commit the transaction and close the connection
            conn.commit()
            cursor.close()
            conn.close()

            flash('Income recorded successfully!')
        except pyodbc.Error as e:
            flash('An error occurred while recording income.')
            print("Error in SQL:", e)
        
        return redirect(url_for('income'))

    return render_template('income.html')

@app.route('/expenses', methods=['GET','POST'])
def expenses():
    if 'user_id' not in session:
        flash('Please log in to record your expenses.')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        try:
            # Assuming you have an authenticated user and user_id is stored in session
            user_id = session['user_id']
            fixed = request.form['fixed']
            variable = request.form['variable']
            discretionary = request.form['discretionary']
            annual = request.form['annual']
            rent = request.form['rent']
            utilities = request.form['utilities']
            insurance = request.form['insurance']
            groceries = request.form['groceries']
            transport = request.form['transport']
            health = request.form['health']
            subscriptions = request.form['subscriptions']            
            other = request.form['other']
            
            # Connect to the database
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            # Insert the expenses data
            cursor.execute("""
                INSERT INTO expenses
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, fixed, variable, discretionary, annual, rent, utilities, insurance, groceries, transport, health, subscriptions, other))  # Add other expenses fields as needed

            # Commit the transaction and close the connection
            conn.commit()
            cursor.close()
            conn.close()

            flash('Expenses recorded successfully!')
        except pyodbc.Error as e:
            flash('An error occurred while recording expenses.')
            print("Error in SQL:", e)
        
        return redirect(url_for('expenses'))

    return render_template('expenses.html')

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
            other = request.form['other']
            
            # Connect to the database
            conn = pyodbc.connect(conn_str)
            cursor = conn.cursor()
            
            # Insert the saving data
            cursor.execute("""
                INSERT INTO saving
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, emergency, retirement, education, goal, health, other))  # Add other saving fields as needed

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
    cursor.execute("SELECT * FROM income WHERE UserID = ?", user_id)
    incomes = cursor.fetchall()
    
    # Fetch the savings data
    cursor.execute("SELECT * FROM saving WHERE UserID = ?", user_id)
    savings = cursor.fetchall()
    
    # Fetch the expenses data
    cursor.execute("SELECT * FROM expenses WHERE UserID = ?", user_id)
    expenses = cursor.fetchall()

    # Close the database connection
    cursor.close()
    conn.close()
    
    return render_template('view_finances.html', incomes=incomes, savings=savings, expenses=expenses)
################################################################
# Edit income outcome
@app.route('/edit_income', methods=['GET', 'POST'])
def edit_income():
    if 'user_id' not in session:
        flash('Please log in to edit records.')
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    if request.method == 'POST':
        salary = request.form.get('salary')
        bonuses = request.form.get('bonuses')
        passive_income = request.form.get('passive_income')
        business_income = request.form.get('business_income')
        investment_income = request.form.get('investment_income')
        other = request.form.get('other')

        cursor.execute("""
            UPDATE income SET
            SalaryWages = ?,
            BonusesCommisions = ?,
            PassiveIncome = ?,
            BusinessIncome = ?,
            InvestmentIncome = ?,
            Other = ?
            WHERE UserID = ?
        """, (salary, bonuses, passive_income, business_income, investment_income, other, user_id))

        conn.commit()
        flash('Income updated successfully!')
        return redirect(url_for('view_finances'))
    else:
        cursor.execute("SELECT * FROM income WHERE UserID = ?", user_id)
        income = cursor.fetchone()
        return render_template('edit_income.html', income=income)

@app.route('/edit_saving', methods=['GET', 'POST'])
def edit_saving():
    if 'user_id' not in session:
        flash('Please log in to edit records.')
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    if request.method == 'POST':
        emergency = request.form.get('emergency')
        retirement = request.form.get('retirement')
        education = request.form.get('education')
        goalSpecific = request.form.get('goalSpecific')
        health = request.form.get('health')
        other = request.form.get('other')

        cursor.execute("""
            UPDATE saving SET
            Emergency = ?,
            retirement = ?,
            Education = ?,
            GoalSpecific = ?,
            Health = ?,
            Other = ?
            WHERE UserID = ?
        """, (emergency, retirement, education, goalSpecific, health, other, user_id))

        conn.commit()
        flash('saving updated successfully!')
        return redirect(url_for('view_finances'))
    else:
        cursor.execute("SELECT * FROM saving WHERE UserID = ?", user_id)
        saving = cursor.fetchone()
        return render_template('edit_saving.html', saving=saving)

@app.route('/edit_expenses', methods=['GET', 'POST'])
def edit_expenses():
    if 'user_id' not in session:
        flash('Please log in to edit records.')
        return redirect(url_for('login'))
    
    user_id = session['user_id']

    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    if request.method == 'POST':
        fixed = request.form.get('fixed')
        variable = request.form.get('variable')
        discretionary = request.form.get('discretionary')
        annualPeriodic = request.form.get('annualPeriodic')
        rentMortrage = request.form.get('rentMortrage')
        utilities = request.form.get('utilities')
        insurance = request.form.get('insurance')
        groceries = request.form.get('groceries')
        transport = request.form.get('transport')
        healthCare = request.form.get('healthCare')
        subscriptions = request.form.get('subscriptions')
        other = request.form.get('other')

        cursor.execute("""
            UPDATE expenses SET
            Fixed = ?,
            Variable = ?,
            Discretionary = ?,
            AnnualPeriodic = ?,
            RentMortrage = ?,
            Utilities = ?,
            Insurance = ?,
            Groceries = ?,
            Transport = ?,
            HealthCare = ?,
            Subscriptions = ?,
            Other = ?
            WHERE UserID = ?
        """, (fixed, variable, discretionary, annualPeriodic, rentMortrage, utilities, insurance, groceries, transport, healthCare, subscriptions, other, user_id))

        conn.commit()
        flash('Expenses updated successfully!')
        return redirect(url_for('view_finances'))
    else:
        cursor.execute("SELECT * FROM expenses WHERE UserID = ?", user_id)
        expenses = cursor.fetchone()
        return render_template('edit_expenses.html', expenses=expenses)

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

@app.route('/add_loan', methods=['GET', 'POST'])
def add_loan():
    if 'user_id' not in session:
        flash('Please log in to add a loan.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        lender_name = request.form['lender_name']
        loan_amount = request.form['loan_amount']
        interest_rate = request.form['interest_rate']
        monthly_payment = request.form['monthly_payment']
        start_date = request.form['start_date']
        due_date = request.form['due_date']
        loan_term = request.form['loan_term']
        remaining_balance = request.form['remaining_balance']
        is_borrower = bool(request.form['is_borrower'])
        notes = request.form['notes']
        user_id = session['user_id']

        # Add loan to database
        # Assuming conn is your database connection
        query = """INSERT INTO loans (UserID, LenderName, LoanAmount, InterestRate, MonthlyPayment, StartDate, DueDate, LoanTerm, RemainingBalance,IsBorrower, Notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        with pyodbc.connect(conn_str) as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, (user_id, lender_name, loan_amount, interest_rate, monthly_payment, start_date, due_date, loan_term, remaining_balance, is_borrower, notes))
                conn.commit()

        flash('Loan added successfully!')
        return redirect(url_for('loans'))  # Redirect to the loans overview page

    return render_template('add_loan.html')

@app.route('/edit_loan/<int:loan_id>', methods=['GET', 'POST'])
def edit_loan(loan_id):
    # Check if user is logged in
    if not session.get('user_id'):
        return redirect(url_for('login'))

    # Connect to your database
    conn = pyodbc.connect(conn_str)
    cursor = conn.cursor()

    if request.method == 'POST':
        # Retrieve form data
        lender_name = request.form['lender_name']
        loan_amount = request.form['loan_amount']
        interest_rate = request.form['interest_rate']
        monthly_payment = request.form['monthly_payment']
        start_date = request.form['start_date']
        due_date = request.form['due_date']
        loan_term = request.form['loan_term']
        remaining_balance = request.form['remaining_balance']
        is_borrower = request.form['is_borrower']
        notes = request.form['notes']
        
        # Update the loan details in the database
        update_query = """UPDATE loans SET LenderName=?, LoanAmount=?, InterestRate=?, MonthlyPayment=?,StartDate=?, DueDate=?, LoanTerm=?, RemainingBalance=?, IsBorrower=?, Notes=? WHERE LoanID=?"""
        cursor.execute(update_query, (lender_name, loan_amount, interest_rate, monthly_payment, start_date, due_date, loan_term, remaining_balance, is_borrower, notes, loan_id))
        conn.commit()

        # Redirect to a confirmation page or back to the loan list
        return redirect(url_for('loans'))

    else:
        # For a GET request, fetch the loan's current details to prefill the form
        cursor.execute("SELECT * FROM loans WHERE LoanID=?", (loan_id,))
        loan = cursor.fetchone()

        # Close database connection
        cursor.close()
        conn.close()

        # Render the edit page template with the loan details
        return render_template('edit_loan.html', loan=loan)

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

@app.route('/contact')
def contact():
    return render_template('contact_us.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
