from flask import Flask
from .extensions import db, cors, csrf
from dotenv import load_dotenv
import os
import urllib

def create_app():
    app = Flask(__name__)
    load_dotenv()

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'a_default_secret_key')
    app.config['WTF_CSRF_ENABLED'] = os.getenv('WTF_CSRF_ENABLED')

    driver = '{ODBC Driver 17 for SQL Server}'
    server = os.getenv('SQL_SERVER')
    database = os.getenv('SQL_DATABASE')
    username = os.getenv('SQL_USER')
    password = os.getenv('SQL_PASSWORD')

    params = urllib.parse.quote_plus(
        f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    )
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={params}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    cors.init_app(app, supports_credentials=True)
    csrf.init_app(app)

    from .routes import home_routes, auth_routes, finance_routes, loans_routes, overview, account, recommendations, calendar, transactions, chatbot
    # Initialize routes or register blueprints
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

    return app