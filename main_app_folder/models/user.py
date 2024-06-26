from main_app_folder.extensions import db

class User(db.Model):
    __tablename__ = 'users'
    UserID = db.Column('UserID', db.Integer, primary_key=True)
    Name = db.Column('Name', db.String(255))
    LastName = db.Column('LastName', db.String(255))
    Email = db.Column('Email', db.String(255), unique=True, nullable=False)
    Password = db.Column('Password', db.String(255), nullable=False)
    Role = db.Column('Role', db.String)
    ProfileImage = db.Column('ProfileImage', db.String(255), nullable=True)
    
    def __repr__(self):
        return f'<User {self.Email}>'
