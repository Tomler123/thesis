from flask import Flask
from .extensions import db, cors, csrf
from dotenv import load_dotenv
import os
import urllib

app = Flask(__name__)

def create_app(config=None):
    # app = Flask(__name__)
    load_dotenv()
    
    if config:
        app.config.update(config)
    else:
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
    
    # home_routes.init_app(app)
    # calendar.init_app(app)
    # loans_routes.init_app(app)
    # home_routes.home
    # calendar.calendar
    # loans_routes.loans
    # auth_routes.init_app(app)
    # account.init_app(app)
    # overview.init_app(app)
    # finance_routes.init_app(app)
    # recommendations.init_app(app)
    # transactions.init_app(app)
    # chatbot.init_app(app)

    return app
