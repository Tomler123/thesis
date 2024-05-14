from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
cors = CORS()
csrf = CSRFProtect()