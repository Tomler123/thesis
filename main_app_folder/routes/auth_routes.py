from flask import Blueprint, current_app, redirect, request, render_template, url_for, session, flash
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer
from main_app_folder.forms import forms
from main_app_folder.utils import helpers
import secrets

auth_bp = Blueprint('auth', __name__)

pending_users = {}

def configure_mail(app, port, use_tls, use_ssl):
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = port
    app.config['MAIL_USE_TLS'] = use_tls
    app.config['MAIL_USE_SSL'] = use_ssl
    app.config['MAIL_USERNAME'] = 'walletbuddyai@gmail.com'
    app.config['MAIL_PASSWORD'] = 'tmgq owra tjts hkfx'
    app.config['MAIL_DEFAULT_SENDER'] = 'walletbuddyai@gmail.com'
    return Mail(app)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    mail = configure_mail(current_app, 587, True, False)
    form = forms.SignUpForm()
    
    if form.validate_on_submit() or request.method == 'POST':
        name = form.name.data
        last_name = form.last_name.data
        email = form.email.data
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        role = 'user'
        profile_image = 'icon1.png'
        verification_token = secrets.token_urlsafe(32)
        
        conn = helpers.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE Email = ?", email)
        if cursor.fetchone():
            flash('Email already registered. Please login or use a different email.', 'error')
            return redirect(url_for('auth.signup'))
        pending_users[email] = {
            'name': name,
            'last_name': last_name,
            'email': email,
            'password': hashed_password,
            'role': role,
            'profile_image': profile_image,
            'verification_token': verification_token
        }
        
        conn.commit()
        cursor.close()
        conn.close()
        verification_link = url_for('auth.verify_email', token=verification_token, _external=True)
        
        msg = Message('Verify Your Email', recipients=[email])
        msg.body = f'Click the following link to verify your email: {verification_link}'
        mail.send(msg)
        flash('You have successfully signed up!', 'success')
        return render_template('verify_email.html')
    if request.method == 'POST' and not form.validate():
        print("Signup form errors:", form.errors)
    return render_template('signup.html', form=form)

@auth_bp.route('/verify_email/<token>')
def verify_email(token):
    for user_email, user_info in pending_users.items():
        if user_info['verification_token'] == token:
            conn = helpers.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (Name, LastName, Email, Password, Role, ProfileImage)
                VALUES (?, ?, ?, ?, ?, ?)
            """, user_info['name'], user_info['last_name'], user_info['email'], 
            user_info['password'], user_info['role'], user_info['profile_image'])
            cursor.execute("SELECT UserID FROM users WHERE Email = ?", user_info['email'])
            user_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            session['user_id'] = user_id
            flash('Your email has been verified. You can now log in.', 'success')
            del pending_users[user_email]
            return redirect(url_for('account.account'))
    flash('Invalid verification token. Please try again or sign up.', 'error')
    return redirect(url_for('auth.signup'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.LoginForm()
    if request.method == 'POST' or form.validate_on_submit():
        email = request.form.get('email')
        password = request.form.get('password')
        conn = helpers.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID, Password FROM users WHERE Email = ?", email)
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user and check_password_hash(user.Password, password):
            session['user_id'] = user.UserID
            return redirect(url_for('account.account'))
        else:
            flash('Invalid email or password')
    return render_template('login.html', form=form)

@auth_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    mail = configure_mail(current_app, 587, True, False)
    form = forms.ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        session['reset_email'] = form.email.data
        serializer = Serializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(email)
        conn = helpers.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Email from users WHERE Email = ?", email)
        user = cursor.fetchone()
        if user is None:
            flash('No account with that email address exists.', 'error')
            return render_template('forgot_password.html', form=form)
        reset_link = url_for('auth.reset_password', token=token, _external=True)
        msg = Message('Password Reset Request', recipients=[email])
        msg.body = f"Click the following link to reset your password: {reset_link}"
        mail.send(msg)
        flash('An email with instructions to reset your password has been sent to your email address.')
        return redirect(url_for('auth.forgot_password_confirm'))
    return render_template('forgot_password.html', form=form)

@auth_bp.route('/forgot_password_confirm')
def forgot_password_confirm():
    return render_template('forgot_password_confirm.html')

@auth_bp.route('/reset_password', methods=['GET','POST'])
def reset_password():
    form = forms.ResetPasswordForm()
    if form.validate_on_submit():
        new_password = form.password.data
        reset_email = session.get('reset_email')
        conn = helpers.get_db_connection()
        cursor = conn.cursor()
        hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        cursor.execute("UPDATE users SET Password = ? WHERE Email = ?", hashed_password, reset_email)
        conn.commit()
        cursor.close()
        conn.close()
        flash('Your password has been reset successfully. You can now log in with your new password.')
        session.pop('reset_email', None)
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form)

@auth_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    mail = configure_mail(current_app, 465, False, True)
    if 'user_id' not in session:
        flash('Please log in to access recommendations.')
        return redirect(url_for('auth.login'))
    form = forms.ContactUsForm()
    if form.validate_on_submit():
        user_id = session['user_id']
        conn = helpers.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Email FROM users WHERE UserID = ?", user_id)
        email = cursor.fetchone()[0]
        message = form.message.data
        msg = Message("Contact Form Submission",
                    sender=current_app.config['MAIL_USERNAME'],
                    recipients=[current_app.config['MAIL_USERNAME']])
        msg.body = f"Message from {email}:\n{message}"
        try:
            mail.send(msg)
            flash('Your message has been sent successfully!', 'success')
        except Exception as e:
            flash(f'Error sending email: {str(e)}', 'error')
        return redirect(url_for('auth.contact'))
    return render_template('contact_us.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('home.home'))
