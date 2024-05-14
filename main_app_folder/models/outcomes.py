from main_app_folder import db

class Outcome(db.Model):
    __tablename__ = 'outcomes'
    ID = db.Column('ID', db.Integer, primary_key=True)
    UserID = db.Column('UserID', db.Integer, db.ForeignKey('users.UserID'))
    Name = db.Column('Name', db.String(255))
    Cost = db.Column('Cost', db.Integer)
    Day = db.Column('Day', db.Integer)
    Month = db.Column('Month', db.Integer)
    Year = db.Column('Year', db.Integer)
    Fulfilled = db.Column('Fulfilled', db.Boolean)
    Type = db.Column('Type', db.String(255))

    def __repr__(self):
        return f'<Name={self.Name}, Cost={self.Cost}, Day={self.Day}, Month={self.Month}, Year={self.Year}, Type={self.Type}>'
