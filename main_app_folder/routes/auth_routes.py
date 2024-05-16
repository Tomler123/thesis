from flask import redirect, request, render_template, url_for, session, flash, session
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
from main_app_folder.forms import forms
from main_app_folder.utils import helpers 
import secrets  
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import URLSafeTimedSerializer as Serializer

pending_users = {}

def init_app(app):
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'walletbuddyai@gmail.com'
    app.config['MAIL_PASSWORD'] = 'tmgq owra tjts hkfx'
    app.config['MAIL_DEFAULT_SENDER'] = 'walletbuddyai@gmail.com'

    mail = Mail(app)

    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
    # Update with your email address
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        mail = Mail(app)
        
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

            # Check if email already exists
            cursor.execute("SELECT * FROM users WHERE Email = ?", email)
            if cursor.fetchone():
                flash('Email already registered. Please login or use a different email.', 'error')
                return redirect(url_for('signup'))

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

            verification_link = url_for('verify_email', token=verification_token, _external=True)
            
            msg = Message('Verify Your Email', recipients=[email])
            msg.body = f'Click the following link to verify your email: {verification_link}'
            mail.send(msg)

            flash('You have successfully signed up!', 'success')
            return render_template('verify_email.html')
        if request.method == 'POST' and not form.validate():
            print("Signup form errors:", form.errors)
        return render_template('signup.html', form=form)
    
    # Define the verify_email route
    @app.route('/verify_email/<token>')
    def verify_email(token):
        for user_email, user_info in pending_users.items():
            if user_info['verification_token'] == token:
                # Connect to the database
                conn = helpers.get_db_connection()
                cursor = conn.cursor()

                # If email does not exist, proceed with registration
                cursor.execute("""
                    INSERT INTO users (Name, LastName, Email, Password, Role, ProfileImage)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, user_info['name'], user_info['last_name'], user_info['email'], 
                user_info['password'], user_info['role'], user_info['profile_image'])

                # Fetch the user's ID
                cursor.execute("SELECT UserID FROM users WHERE Email = ?", user_info['email'])
                user_id = cursor.fetchone()[0]

                conn.commit()
                cursor.close()
                conn.close()

                session['user_id'] = user_id

                flash('Your email has been verified. You can now log in.', 'success')
                del pending_users[user_email]  # Remove user from pending_users
                return redirect(url_for('account'))

        flash('Invalid verification token. Please try again or sign up.', 'error')
        return redirect(url_for('signup'))

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = forms.LoginForm()

        if request.method == 'POST' or form.validate_on_submit():
            email = request.form.get('email')  # Use the .get method to avoid KeyError
            password = request.form.get('password')

            # Connect to the database
            conn = helpers.get_db_connection()
            cursor = conn.cursor()

            # Find user by email
            cursor.execute("SELECT UserID, Password FROM users WHERE Email = ?", email)
            user = cursor.fetchone()

            # Close cursor and connection
            cursor.close()
            conn.close()

            # If user exists and password matches
            if user and check_password_hash(user.Password, password):
                session['user_id'] = user.UserID  # Store the user's ID in the session
                return redirect(url_for('account'))  # Redirect to the user's account page
            else:
                flash('Invalid email or password')


        return render_template('login.html', form=form)

    @app.route('/forgot_password', methods=['GET', 'POST'])
    def forgot_password():
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USE_SSL'] = False
        mail = Mail(app)

        form = forms.ForgotPasswordForm()

        if form.validate_on_submit():
            email = form.email.data
            session['reset_email'] = form.email.data
            # Generate a token with a 1-hour expiration time
            serializer = Serializer(app.config['SECRET_KEY'])
            token = serializer.dumps(email)

            # checking if the user is registered
            conn = helpers.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT Email from users WHERE Email = ?", email)
            user = cursor.fetchone()
            
            if user is None:
                flash('No account with that email address exists.', 'error')
                return render_template('forgot_password.html', form=form)
            
            # Send email with password reset link
            reset_link = url_for('reset_password', token=token, _external=True)
            msg = Message('Password Reset Request', recipients=[email])
            msg.body = f"Click the following link to reset your password: {reset_link}"
            mail.send(msg)

            flash('An email with instructions to reset your password has been sent to your email address.')
            return redirect(url_for('forgot_password_confirm'))

        return render_template('forgot_password.html', form=form)

    @app.route('/forgot_password_confirm')
    def forgot_password_confirm():
        return render_template('forgot_password_confirm.html')

    @app.route('/reset_password', methods=['GET','POST'])
    def reset_password():
        form = forms.ResetPasswordForm()

        if form.validate_on_submit():
            # Get the new password from the form
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
            return redirect(url_for('login'))  # Redirect to the login page after resetting the password

        return render_template('reset_password.html', form=form)

    @app.route('/contact', methods=['GET', 'POST'])
    def contact():
        app.config['MAIL_PORT'] = 465
        app.config['MAIL_USE_TLS'] = False
        app.config['MAIL_USE_SSL'] = True
        mail = Mail(app)
        if 'user_id' not in session:
            flash('Please log in to access recommendations.')
            return redirect(url_for('login'))
        
        form = forms.ContactUsForm()
        if form.validate_on_submit():
            user_id = session['user_id']    
            # Connect to the database
            conn = helpers.get_db_connection()
            cursor = conn.cursor()

            # Calculating total monthly debt
            cursor.execute("SELECT Email FROM users WHERE UserID = ?", user_id)
            email = cursor.fetchone()[0]
            
            message = form.message.data
            msg = Message("Contact Form Submission",
                        sender=app.config['MAIL_USERNAME'],
                        recipients=[app.config['MAIL_USERNAME']])
            msg.body = f"Message from {email}:\n{message}"
            try:
                mail.send(msg)
                flash('Your message has been sent successfully!', 'success')
            except Exception as e:
                flash(f'Error sending email: {str(e)}', 'error')
            return redirect(url_for('contact'))
        return render_template('contact_us.html', form=form)