from flask import Blueprint, render_template, request, redirect, url_for, flash, logging
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from db import engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text
from models import construct_user
import requests

auth_bp = Blueprint('auth', __name__)

import requests
from flask import request, render_template, jsonify

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Ensure the request contains JSON data
        if not request.is_json:
            return jsonify({'message': 'Bad request: Missing or invalid JSON data'}), 400

        # Extract username and password from JSON
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'message': 'Bad request: Username and password are required'}), 400

        # Forward the request to the login service
        try:
            response = requests.post(
                "http://127.0.0.1:80/auth/login",
                json={'username': username, 'password': password},
                verify=False
            )
        except requests.RequestException as e:
            return jsonify({'message': f'Error communicating with login service: {str(e)}'}), 500

        # Handle response from login service
        if response.status_code == 200:
            try:
                return jsonify(response.json()), 200
            except ValueError:
                return jsonify({'message': 'Invalid response from login service'}), 500
        elif response.status_code == 401:
            return jsonify({'message': 'Invalid username or password'}), 401
        else:
            return jsonify({'message': 'Unexpected error from login service'}), response.status_code

    # Handle GET request (render login form)
    return render_template('auth/login.html')



import requests  # To make the HTTP request to /auth/verify-2fa

@auth_bp.route('/2fa', methods=['GET', 'POST'])
def two_fa():
    if request.method == 'POST':
        auth_code = request.json.get('authCode')  # Get the 2FA code entered by the user
        temporary_token = request.headers.get('Authorization')  # Get the temporary token from headers

        if not temporary_token:
            return jsonify({"message": "No temporary token found. Please log in first."}), 400
        
        # Prepare the payload to forward to /auth/verify-2fa
        payload = {'verification_code': auth_code}
        
        # Forward the request to the /auth/verify-2fa endpoint
        response = requests.post(
            'http://127.0.0.1:80/auth/verify-2fa', 
            json=payload,
            headers={'Authorization': temporary_token}  # Include the temporary token in the header
        )

        # Check the response from the /auth/verify-2fa endpoint
        if response.status_code == 200:
            data = response.json()
            return jsonify(data), 200
        else:
            data = response.json()
            return jsonify(data), response.status_code
    
    return render_template('auth/2fa.html')



@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        # Get data from the JSON body of the request
        data = request.get_json()  # Expecting JSON data
        email = data.get('email')  # Extract email from the JSON data

        print(email)  # This will now print the email

        try:
            # Send the POST request to the /auth/forgot-password API
            response = requests.post(
                'http://127.0.0.1:80/auth/forgot-password',
                json={'email': email},
                verify = False# Pass the email as JSON
            )
            if response.status_code == 200:
                try:
                    return jsonify(response.json()), 200
                except ValueError:
                    return jsonify({'message': 'Invalid response from login service'}), 500
            else:
                return jsonify({'message': 'Unexpected error from login service'}), response.status_code
        except requests.exceptions.RequestException as e:
            # Handle any errors related to the request itself
            return jsonify({'message': str(e)}), 500

    return render_template('auth/forgot-password.html')

@auth_bp.route('/2fa-forgot-password', methods=['GET', "POST"])
def two_fa_forgot_password():
    if request.method == 'POST':
        auth_code = request.json.get('authCode')  # Get the 2FA code entered by the user
        temporary_token = request.headers.get('Authorization')  # Get the temporary token from headers

        print(f"Received auth_code: {auth_code}")  # Debugging line
        print(f"Received temporary_token: {temporary_token}")  # Debugging line

        if not temporary_token:
            return jsonify({"message": "No temporary token found. Please log in first."}), 400
        
        # Prepare the payload to forward to /auth/verify-2fa
        payload = {'verification_code': auth_code}
        print(f"Payload: {payload}")  # Debugging line
        
        # Forward the request to the /auth/verify-2fa endpoint
        response = requests.post(
            'http://127.0.0.1:80/api/verify-password-reset', 
            json=payload,
            headers={'Authorization': temporary_token}  # Include the temporary token in the header
        )
        print(f"Response from /verify-password-reset: {response.status_code}, {response.text}")  # Debugging line

        if response.status_code == 200:
            data = response.json()
            return jsonify(data), 200

        else:
            data = response.json()
            return jsonify(data), response.status_code
    
    return render_template('auth/2fa-forgot-password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        print("POSTOU")
        # Correctly retrieve the password using the correct key
        new_password = request.json.get('new_password')
        print(new_password)

        # Retrieve the JWT token from the client-side local storage
        token = request.headers.get('Authorization')  # Assuming the token is stored in the headers
        print(token)

        if not token:
            flash('Authorization token missing. Please log in again. back', 'error')
            return redirect(url_for('auth.login'))

        # Ensure payload is a dictionary
        payload = {"new_password": new_password}

        # Send the POST request to the /auth/update-password API
        response = requests.post(
            'http://127.0.0.1:80/auth/update-password',
            json=payload,
            headers={'Authorization': token}  # Include the token in the header
        )
        print(f"Response from /update-password-reset: {response.status_code}")

        # Check the response from the API
        if response.status_code == 200:
            flash('Password updated successfully. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Failed to update password. Please try again.', 'error')

    return render_template('auth/reset-password.html')



@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        # Get form data
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        name = request.form.get('name')
        phone = request.form.get('phone')
        is_doctor = request.form.get('is_doctor')

        # Send the POST request to the /auth/register API
        response = requests.post(
            'http://127.0.0.1:80/auth/register',
            json={  # Pass the form data as JSON
                'username': username,
                'password': password,
                'email': email,
                'name': name,
                'phone': phone,
                'is_doctor': is_doctor
            }
        )

        # Check the response from the API
        if response.status_code == 201:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('There was an issue with registration. Please try again.', 'danger')


    # Render the registration page for GET requests
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
