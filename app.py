import os
import requests
import datetime


from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify
from flask_login import login_required, LoginManager
from mysql.connector import Error
from datetime import timedelta
from auth import auth_bp, get_user_by_username
from models import models_bp

from helper_functions import load_form_fields, serialize_data, send_data_to_api, get_user_id_from_token, get_clinics


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['TEMPLATES_AUTO_RELOAD'] = True


# Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(models_bp)

# Secret key for session management
app.config['SECRET_KEY'] = "your_secret_key"


# Login Manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

# Define the user loader function
@login_manager.user_loader
def load_user(username):
    user = get_user_by_username(username)
    return user



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('/doctor/dashboard.html')


@app.route('/mark_arrived/<int:appointment_id>', methods=['POST'])
@login_required
def mark_arrived(appointment_id):
    pass

@app.route('/clinics')
def clinics():
    try:
        response = requests.get('http://0.0.0.0:80/api/clinics')
        response.raise_for_status()
        clinics_data = response.json().get('clinics', [])

        user_id = get_user_id_from_token()
        print(user_id)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching clinics: {e}")
        
        try:
            response = requests.get('http://0.0.0.0:80/api/clinics')
            response.raise_for_status()
            clinics_data = response.json().get('clinics', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching clinics: {e}")
            clinics_data = []

    return render_template('clinics.html', clinics=clinics_data)

@app.route('/clinic_management', methods=['GET', 'POST'])
def clinic_management():
    if request.method == 'POST':

        form_data = load_form_fields(request)
        form_data['created_at'] = datetime.datetime.now()
        form_data['updated_at'] = datetime.datetime.now()
        form_data = serialize_data(form_data)

        print(f"form_data: {form_data}")
        


        send_data_to_api('http://0.0.0.0:80/api/clinics', form_data)

    return render_template('./admin/clinic_management.html')

@app.route('/doctor_management')
def doctor_management():
    return render_template('./admin/doctor_management.html')

@app.route('/patients')
def patients():

    user_id = get_user_id_from_token()
    first_clinic = get_clinics(user_id)
    
    mock_clinic_id = 3


    try:
        response = requests.get('http://0.0.0.0:80/api/patients?clinic_id={}'.format(first_clinic))
        response.raise_for_status()
        patients_data = response.json().get('patients', [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching patients: {e}")
        patients_data = []

    return render_template('patients.html', patients=patients_data)

@app.route('/patient_management', methods=['GET', 'POST'])
def patient_management():
    if request.method == 'POST':

        form_data = load_form_fields(request)
        form_data['created_at'] = datetime.datetime.now()
        form_data['updated_at'] = datetime.datetime.now()
        form_data = serialize_data(form_data)

        print(f"form_data: {form_data}")


        send_data_to_api('http://0.0.0.0:80/api/patients', form_data)


    return render_template('./admin/patient_management.html')

# Debbugin route to show all the session information

@app.route('/session')
def session_view():
    return jsonify(dict(session))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, user_reloader=True)