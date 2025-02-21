import os
import requests
import datetime


from flask import Flask, render_template, redirect, url_for, session, request, flash, jsonify
from flask_cors import CORS
from flask_login import login_required, LoginManager
from mysql.connector import Error
from datetime import timedelta
from auth import auth_bp, get_user_by_username
from models import models_bp
import requests

from helper_functions import (
    load_form_fields, 
    serialize_data, 
    send_data_to_api, 
    get_user_id_from_token, 
    get_clinics, 
    get_doctors, 
    patient_exists, 
    search_care_link,
    retrieve_patient_data
)


app = Flask(__name__)
CORS(app)
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

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Get data from the contact form
        name = request.form.get('name')
        email = request.form.get('email')
        message_content = request.form.get('message')

        # Send the POST request to the /auth/contact API
        response = requests.post(
            'http://127.0.0.1:80/auth/contact', 
            json={  # Pass the form data as JSON
                'name': name,
                'email': email,
                'message': message_content
            }
        )
        
        # Check the response from the API
        if response.status_code == 200:
            return redirect(url_for('about'))
        else:
            flash('There was an issue sending your message. Please try again later.', 'danger')

          # Redirect back to the contact form

    return render_template('contact.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('/doctor/dashboard.html')


@app.route('/mark_arrived/<int:appointment_id>', methods=['POST'])
@login_required
def mark_arrived(appointment_id):
    pass
@app.route('/frontdesk')
def frontdesk():
    return render_template('frontdesk.html')

@app.route('/clinics')
def clinics():
    user_id = get_user_id_from_token()
    try:
        response = requests.get('http://0.0.0.0:80/api/clinics?user_id={}'.format(user_id))
        response.raise_for_status()
        clinics_data = response.json().get('clinics', [])

        
      
    except requests.exceptions.RequestException as e:
        print(f"Error fetching clinics: {e}")
        
        try:
            response = requests.get('http://0.0.0.0:80/api/clinics?user_id={}'.format(user_id))
            response.raise_for_status()
            clinics_data = response.json().get('clinics', [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching clinics: {e}")
            clinics_data = []

    return render_template('clinics.html', clinics=clinics_data)

@app.route('/clinic_management', methods=['GET', 'POST'])
def clinic_management():
    user_id = get_user_id_from_token()
    if request.method == 'POST':

        form_data = load_form_fields(request)
        form_data['created_at'] = datetime.datetime.now()
        form_data['updated_at'] = datetime.datetime.now()
        form_data = serialize_data(form_data)

        print(f"form_data: {form_data}")
        


        send_data_to_api('http://0.0.0.0:80/api/clinics', form_data)

    return render_template('./admin/clinic_management.html', user_id=user_id)

@app.route('/doctor_management')
def doctor_management():
    return render_template('./admin/doctor_management.html')

@app.route('/medical_record')
def medical_record():
    care_link_id = request.args.get('care_link_id')
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')

    patient = retrieve_patient_data(care_link_id)

    if request.method == 'POST':
        form_data = load_form_fields(request)
        form_data['created_at'] = datetime.datetime.now()
        form_data['updated_at'] = datetime.datetime.now()
        form_data = serialize_data(form_data)
        send_data_to_api('http://127.0.0.1:80/api/medical-records', form_data)
    
    care_link_id = request.args.get('care_link_id')

    



    return render_template('medical_record.html', care_link_id=care_link_id, first_name=first_name, last_name=last_name, patient=patient)

@app.route('/patients')
def patients():
    user_id = get_user_id_from_token()
    first_clinic = get_clinics(user_id)
    first_doctor = get_doctors(first_clinic)

    try:
        response = requests.get('http://0.0.0.0:80/api/patients?clinic_id={}'.format(first_clinic))
        response.raise_for_status()
        patients_data = response.json().get('patients', [])
        # Associate care links for each patient
        for patient in patients_data:
            patient_id = patient['id']
            doctor_id = first_doctor
            care_link_id = search_care_link(doctor_id, first_clinic, patient_id)
            patient['care_link_id'] = care_link_id
            birth_date = patient.get('date_of_birth')
            if birth_date:
                birth_date = datetime.datetime.strptime(birth_date, '%Y-%m-%d')
                today = datetime.datetime.today()
                age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
                patient['age'] = age
                print("********** PATIENT AGE **********")
                print(patient['age'])


    except requests.exceptions.RequestException as e:
        print(f"Error fetching patients: {e}")
        patients_data = []


    return render_template('patients.html', patients=patients_data)


@app.route('/patient_management', methods=['GET', 'POST'])
def patient_management():
    if request.method == 'POST':


        form_data = request.form.to_dict()
        form_data['created_at'] = datetime.datetime.now()
        form_data['updated_at'] = datetime.datetime.now()
        form_data = serialize_data(form_data)

        user_id = get_user_id_from_token()
        first_clinic = get_clinics(user_id)
        first_doctor = get_doctors(first_clinic)
        patient_id = form_data.get('id')

        if patient_exists(patient_id):
            send_data_to_api(f'http://0.0.0.0:80/api/patient_by_id/{patient_id}', form_data, method='PUT')
        else:
            form_data['clinic_id'] = first_clinic
            form_data['doctor_id'] = first_doctor
            send_data_to_api('http://0.0.0.0:80/api/patients', form_data)

        return redirect(url_for('patients'))

    if request.method == 'GET':
        patient_id = request.args.get('patient_id')
        user_id = get_user_id_from_token()
        first_clinic = get_clinics(user_id)
        first_doctor = get_doctors(first_clinic)
        care_link_id = search_care_link(patient_id, first_clinic, first_doctor)

        if patient_id:
            try:
                response = requests.get(f'http://0.0.0.0:80/api/patient_by_id/{patient_id}')
                response.raise_for_status()
                patient_data = response.json().get('patient', {})
                patient_data['care_link_id'] = care_link_id

            except requests.exceptions.RequestException as e:
                print(f"Error fetching patient: {e}")
                patient_data = {}
        else:
            patient_data = {}

        return render_template('./admin/patient_management.html', patient=patient_data)

    return render_template('./admin/patient_management.html')

# Debbugin route to show all the session information

@app.route('/session')
def session_view():
    return jsonify(dict(session))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, user_reloader=True)