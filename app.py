from flask import Flask, flash, render_template, request, redirect, session, url_for, g
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from sqlite3 import dbapi2 as sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from config import MAIL_USERNAME, MAIL_PASSWORD, SECRET_KEY
import hashlib
import time
from flask import jsonify

from weaviate import Client


app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = MAIL_USERNAME
app.config['MAIL_PASSWORD'] = MAIL_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = MAIL_USERNAME
app.config['MAIL_DEBUG'] = True

mail = Mail(app)

serializer = URLSafeTimedSerializer(app.secret_key)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('users.db')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def generate_verification_token(email):
    timestamp = str(time.time())
    email_hash = hashlib.sha256(email.encode('utf-8')).hexdigest()
    return email_hash + timestamp


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/signin', methods=['POST'])
def signin():
    email = request.form['email']
    password = request.form['password']
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    
    if user is None:
        return jsonify({'error': 'Email not found'})
    
    if not check_password_hash(user[2], password):
        return jsonify({'error': 'Incorrect password'})
    
    session['user_id'] = user[0]
    session['email'] = user[1]
    return jsonify({'success': 'Logged in successfully'})


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM approved_emails WHERE email=?", (email,))
        result = c.fetchone()
        if result:
            # Generate a hash key
            hash_key = hashlib.sha256(email.encode()).hexdigest()

            # Add the hash key to the database
            c.execute("UPDATE approved_emails SET hash_key=? WHERE email=?", (hash_key, email))
            conn.commit()

            # Send the authorization email with the hash key
            authorization_link = url_for('authorize_email', email=email, hash_key=hash_key, _external=True)
            send_authorization_email(email, authorization_link, hash_key)

            flash('Authorization email sent to ' + email, 'success')
            session['email'] = email
            return redirect('/dashboard')
        else:
            flash('Email address not authorized', 'error')

        conn.close()

    return render_template('signup.html')


@app.route('/authorize-email/<email>')
def authorize_email(email):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()

    # Check if email is already on approved list
    c.execute("SELECT * FROM approved_users WHERE email = ?", (email,))
    approved_user = c.fetchone()

    if approved_user:
        flash('Email already authorized')
    else:
        # Add email to approved list
        c.execute("INSERT INTO approved_users (email) VALUES (?)", (email,))
        conn.commit()
        flash('Email authorized')

    return redirect(url_for('signin'))

def send_authorization_email(email, authorization_link, hash_key):
    msg = Message('Authorize Your Email Address', sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
    msg.body = f'Please click the following link to authorize your email address: {authorization_link}\n\nYour hash key is: {hash_key}'
    mail.send(msg)


@app.route('/confirm-email/<token>')
def confirm_email(token):
    try:
        email = serializer.loads(token, salt='email-confirmation', max_age=3600)
    except:
        return render_template('token_expired.html')

    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET confirmed=True WHERE email = ?", (email,))
    return render_template('email_confirmed.html')


def send_confirmation_email(user_email, confirmation_link):
    msg = Message('Confirm Your Email', sender=MAIL_USERNAME, recipients=[user_email])
    msg.body = f'Hello! Please confirm your email through the following link:\n{confirmation_link}'
    mail.send(msg)


@app.route('/token-expired', methods=['GET'])
def token_expired():
    return render_template('token_expired.html')


@app.route('/email-confirmed', methods=['GET'])
def email_confirmed():
    return render_template('email_confirmed.html')


@app.route('/verification-sent')
def verification_sent():
    return render_template('verification_sent.html')


@app.route('/test-email')
def test_email():
    msg = Message('Test Email', sender=MAIL_USERNAME, recipients=['matt.ian.schwartz@gmail.com'])
    msg.body = 'This is a test email from Flask-Mail'
    mail.send(msg)
    return 'Test email sent!'

@app.route('/dashboard')
def dashboard():
    # Your dashboard logic here
    client = Client("http://localhost:8080")
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
