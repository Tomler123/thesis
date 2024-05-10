from flask import Flask
from flask_sqlalchemy import SQLAlchemy  
import os
from flask_cors import CORS
from itsdangerous import Serializer
from main_app_folder.utils import helpers  # Assuming get_db_connection is here
from flask_wtf.csrf import CSRFProtect
import matplotlib
matplotlib.use('Agg')  # Set the backend before importing pyplot
from dotenv import load_dotenv
from main_app_folder.routes import home_routes, auth_routes, finance_routes, loans_routes, overview, account, recommendations, calendar, transactions, chatbot
import urllib

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a_default_secret_key')
app.config['WTF_CSRF_ENABLED'] = os.getenv('WTF_CSRF_ENABLED')
serializer = Serializer(app.config['SECRET_KEY'])
driver= '{ODBC Driver 17 for SQL Server}'
server = os.getenv('SQL_SERVER')
database = os.getenv('SQL_DATABASE')
username = os.getenv('SQL_USER')
password = os.getenv('SQL_PASSWORD')

conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

params = urllib.parse.quote_plus(
    f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
)
# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect={params}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
CORS(app)

# Home page
home_routes.init_app(app)

# Login Signup Mail handling
auth_routes.init_app(app)

# Account
account.init_app(app)

# Finances
overview.init_app(app)

# Incomes, Outcomes, Savings (CRUD)
finance_routes.init_app(app)

# Loans
loans_routes.init_app(app)

# Recommendations
recommendations.init_app(app)

# Calendar
calendar.init_app(app)

# Transactions
transactions.init_app(app)

# Chatterbot
chatbot.init_app(app)
