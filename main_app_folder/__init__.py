from flask import Flask
from flask_session import Session
from .extensions import db, cors, csrf
from dotenv import load_dotenv
import os
import urllib

def create_app(config=None):
    app = Flask(__name__)

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
    
    # Configure session
    app.config['SESSION_TYPE'] = 'filesystem'
    Session(app)

    # Register Blueprints
    from .routes.home_routes import home_bp
    from .routes.auth_routes import auth_bp
    from .routes.finance_routes import finance_bp
    from .routes.loans_routes import loans_bp
    from .routes.overview import overview_bp
    from .routes.account import account_bp
    from .routes.recommendations import recommendations_bp
    from .routes.calendar import calendar_bp
    from .routes.transactions import transactions_bp
    from .routes.chatbot import chatbot_bp

    app.register_blueprint(home_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(finance_bp)
    app.register_blueprint(loans_bp)
    app.register_blueprint(overview_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(recommendations_bp)
    app.register_blueprint(calendar_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(chatbot_bp)

    return app
