from flask import Blueprint, render_template, request, redirect, url_for, flash, logging
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from db import engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from models import construct_user

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Authenticate the user and construct a User object if valid
        user = authenticate_user(username, password)
        if user:
            # Log the user in
            login_user(user, remember=True)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Hash the password
        password_hash = generate_password_hash(password)

        # Check if the username already exists
        existing_user = get_user_by_username(username)
        if existing_user:
            flash('Username already taken!', 'danger')
            return redirect(url_for('auth.register'))

        try:
            save_user_in_db(username, password_hash)  # This is now atomic
            flash('User registered successfully!', 'success')
            return redirect(url_for('auth.login'))
        except RuntimeError as e:
            flash(f'Error registering user: {e}', 'danger')
            return redirect(url_for('auth.register'))

    return render_template('auth/register.html')


def save_user_in_db(username, password_hash):
    """Insert a new user into the database using vanilla SQL and transaction handling."""
    try:
        with engine.begin() as conn:  # engine.begin() handles transaction management
            query = text("""
                INSERT INTO users (username, password_hash, is_admin, is_doctor, created_at)
                VALUES (:username, :password_hash, :is_admin, :is_doctor, NOW())
            """)
            conn.execute(query, {
                'username': username,
                'password_hash': password_hash,
                'is_admin': False,
                'is_doctor': False
            })
    except SQLAlchemyError as e:
        logging.error(f"Transaction failed: {e}")
        raise RuntimeError(f"Transaction failed: {e}")



def authenticate_user(username, password):
    """Authenticate a user based on username and password."""
    try:
        with engine.connect() as conn:  # Use engine.connect() to get a connection
            query = text("SELECT * FROM users WHERE username = :username")
            result = conn.execute(query, {'username': username})
            user_data = result.fetchone()  # Fetch one result
            
            if user_data and check_password_hash(user_data['password_hash'], password):
                return construct_user(user_data)
    except SQLAlchemyError as e:  # Catch SQLAlchemy-specific exceptions
        logging.error(f"Error during user authentication: {e}")
        raise  # Re-raise the exception after logging it

def get_user_by_username(username):
    """Get a user by their username."""
    try:
        with engine.connect() as conn:  # Use engine.connect() to get a connection
            query = text("SELECT * FROM users WHERE username = :username")
            result = conn.execute(query, {'username': username})
            user_data = result.fetchone()  # Fetch one result
            
            if user_data:
                return construct_user(user_data)
    except SQLAlchemyError as e:  # Catch SQLAlchemy-specific exceptions
        logging.error(f"Error getting user by username: {e}")
        raise  # Re-raise the exception after logging it

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
