from main_app_folder.extensions import db

class Transaction(db.Model):
    __tablename__ = 'transactions'
    TransactionID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    Amount = db.Column(db.Numeric(18, 0), nullable=False)
    Date = db.Column(db.Date, nullable=False)
    Category = db.Column(db.String(255), nullable=False)
    Description = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<Transaction {self.TransactionID}>'
