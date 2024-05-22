from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators, SelectField, FloatField, IntegerField, DateField, DecimalField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, NumberRange, InputRequired


class SignUpForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=30)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=30)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=30),
        Regexp(r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[,./\'\[\]!@#$%^&*(){}<>?:"])[A-Za-z\d,./\'\[\]!@#$%^&*(){}<>?:"]+', message='Password must contain at least one uppercase letter, one number, and one symbol.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, max=30)
    ])
    
    submit = SubmitField('Log In')

class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, max=30),
        Regexp(r'(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[,./\'\[\]!@#$%^&*(){}<>?:"])[A-Za-z\d,./\'\[\]!@#$%^&*(){}<>?:"]+', message='Password must contain at least one uppercase letter, one number, and one symbol.')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Reset Password')

class IconForm(FlaskForm):
    selected_icon = StringField('Selected Icon', validators=[DataRequired()])
    submit = SubmitField('Submit')

class IncomeForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    cost = FloatField('Cost', validators=[InputRequired(), NumberRange(min=0)])
    day = IntegerField('Day', validators=[InputRequired(), NumberRange(min=1, max=31)])

class SavingForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    cost = FloatField('Cost', validators=[InputRequired(), NumberRange(min=0)])

class EditSavingForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    cost = FloatField('Cost', validators=[InputRequired(), NumberRange(min=0)])

class EditIncomeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    cost = FloatField('Cost', validators=[DataRequired()])
    day = IntegerField('Day', validators=[DataRequired(), NumberRange(min=1, max=31)])

class OutcomeForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()])
    cost = FloatField('Cost', validators=[InputRequired(), NumberRange(min=0)])
    day = IntegerField('Day', validators=[InputRequired(), NumberRange(min=1, max=31)])
    type = SelectField('Type', choices=[('Expense', 'Expense'), ('Subscription', 'Subscription')], validators=[InputRequired()])

class EditOutcomeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    cost = FloatField('Cost', validators=[DataRequired()])
    day = IntegerField('Day', validators=[DataRequired(), NumberRange(min=1, max=31)])
    type = SelectField('Type', choices=[('Expense', 'Expense'), ('Subscription', 'Subscription')], validators=[DataRequired()])

class AddLoanForm(FlaskForm):
    lender_name = StringField('Lender/Borrower Name', validators=[InputRequired()])
    loan_amount = DecimalField('Loan Amount', validators=[InputRequired(), NumberRange(min=0)])
    interest_rate = DecimalField('Interest Rate (%)', validators=[InputRequired(), NumberRange(min=0)])
    monthly_payment = DecimalField('Monthly Payment', validators=[InputRequired(), NumberRange(min=0)])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[InputRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[InputRequired()])
    remaining_balance = DecimalField('Remaining Balance', validators=[InputRequired(), NumberRange(min=0)])
    is_borrower = SelectField('Are you the borrower?', choices=[('1', 'Yes'), ('0', 'No')], validators=[InputRequired()])
    notes = TextAreaField('Notes')

class EditLoanForm(FlaskForm):
    lender_name = StringField('Lender Name', validators=[DataRequired(), Length(max=100)])
    loan_amount = FloatField('Loan Amount', validators=[DataRequired(), NumberRange(min=0)])
    interest_rate = FloatField('Interest Rate', validators=[DataRequired(), NumberRange(min=0)])
    monthly_payment = FloatField('Monthly Payment', validators=[DataRequired(), NumberRange(min=0)])
    start_date = DateField('Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    due_date = DateField('Due Date', validators=[DataRequired()], format='%Y-%m-%d')
    remaining_balance = FloatField('Remaining Balance', validators=[DataRequired(), NumberRange(min=0)])
    is_borrower = SelectField('Are you borrower', choices=[('1', 'Yes'), ('0', 'No')], coerce=int)
    notes = TextAreaField('Notes')
    submit = SubmitField('Update')

class RecommendationsForm(FlaskForm):
    savings_goal = IntegerField('Enter the percentage of your income that you want to save', default=0, validators=[NumberRange(min=0, max=100, message="Value must be between 0 and 100.")])
    submit = SubmitField('Get Recommendations')

class ContactUsForm(FlaskForm):
    message = StringField('Message', validators=[DataRequired()])
    submit = SubmitField('Submit')

class TransactionForm(FlaskForm):
    amount = DecimalField('Amount', validators=[DataRequired(), NumberRange(min=0)])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    category = StringField('Category', validators=[Length(min=0, max=30)])
    description = StringField('Description', validators=[Length(min=0, max=30)])
    submit = SubmitField('Submit')

class StockPredictionForm(FlaskForm):
    stock_name = StringField('Stock Symbol', validators=[DataRequired()])
    submit = SubmitField('Predict')