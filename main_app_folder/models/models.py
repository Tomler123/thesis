# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.orm import declarative_base
# from werkzeug.security import generate_password_hash, check_password_hash
# from sqlalchemy.orm import declarative_base 

# db = SQLAlchemy()  # Assuming you have your db object initialized elsewhere

# Base = declarative_base()

# class User(Base):
#     __tablename__ = 'users'  # Specify the table name

#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(50), nullable=False)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(120), nullable=False)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)
