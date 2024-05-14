from main_app_folder import db

class Loan(db.Model):
    __tablename__ = 'loans'
    LoanID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    LenderName = db.Column(db.String(255), nullable=False)
    LoanAmount = db.Column(db.Numeric(18, 2), nullable=False)
    MonthlyPayment = db.Column(db.Numeric(18, 2), nullable=False)
    InterestRate = db.Column(db.Numeric(5, 2), nullable=False)
    StartDate = db.Column(db.Date, nullable=False)
    DueDate = db.Column(db.Date, nullable=False)
    RemainingBalance = db.Column(db.Numeric(18, 2), nullable=False)
    IsBorrower = db.Column(db.Boolean, nullable=False)
    Notes = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Loan {self.LoanID}>'
