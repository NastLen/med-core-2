import datetime

import jwt
from flask import flash, current_app, request
import simplejson as json
import requests

def get_user_id_from_token():
    secret_key = current_app.config['SECRET_KEY']
    print(f"secret_key  {secret_key}")  
    token = request.cookies.get('token')
    print(f"token  inside the helper {token}")
    if not token:
        return None

    try:
        decoded = jwt.decode(token, key=secret_key, algorithms=["HS256"], options={"verify_signature": False})
        user_id = decoded.get('sub', {}).get('id')
        return user_id
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None
    
def get_clinics(user_id):
    try:
        response = requests.get('http://127.0.0.1:80/api/clinics?user_id={}'.format(user_id))
        response.raise_for_status()
        clinics_data = response.json().get('clinics', [])
        print(clinics_data)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching clinics: {e}")
        clinics_data = []
    if clinics_data:
        return clinics_data[0]['id']
    else:
        return None

def get_doctors(clinic_id):
    try:
        response = requests.get(f'http://127.0.0.1:80/api/doctors?clinic_id={clinic_id}')
        response.raise_for_status()
        professionals_data = response.json().get('professionals', [])
        print("********** PROFESSIONALS DATA **********")
        print(professionals_data)
        print("**********************************")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching professionals: {e}")
        professionals_data = []
    
    if professionals_data:
        return professionals_data[0]['id']
    else:
        return None


def load_form_fields(request):
    form_fields = {}
    for field in request.form:
        form_fields[field] = request.form[field]
        print(f"field: {field}, value: {request.form[field]}")
    return form_fields

def serialize_data(data):
    """Serialize data to JSON-compatible format, handling datetime objects."""
    def json_serial(obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.isoformat()
        raise TypeError("Type not serializable")
    
    return {k: (json_serial(v) if isinstance(v, (datetime.datetime, datetime.date)) else v) for k, v in data.items()}


def send_data_to_api(url, data, method='post', **kwargs):
    try:
        if method.lower() == 'post':
            response = requests.post(url, json=data, **kwargs)
        elif method.lower() == 'put':
            response = requests.put(url, json=data, **kwargs)
        else:
            raise ValueError("Unsupported method: {}".format(method))
        
        response.raise_for_status()
        print("success")
        flash('Data sent successfully!', 'success')
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")
        flash('Failed to send data.', 'danger')

def patient_exists(patient_id):
    try:
        response = requests.get(f'http://127.0.0.1:80/api/patient_by_id/{patient_id}')
        response.raise_for_status()
        patient_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching patient: {e}")
        patient_data = {}
    return bool(patient_data)

def search_care_link(doctor_id, clinic_id, patient_id):
    print("=====================================================================================================")
    print(f"doctor_id: {doctor_id}, clinic_id: {clinic_id}, patient_id: {patient_id}")
    print("=====================================================================================================")
    try:
        response = requests.get(
            'http://127.0.0.1:80/api/care_link',
            params={
                'doctor_id': doctor_id,
                'clinic_id': clinic_id,
                'patient_id': patient_id
            }
        )
        print(f"Request URL: {response.url}")
        response.raise_for_status()
        care_link_data = response.json()
        return care_link_data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching care link: {e}")
        flash('Failed to fetch care link.', 'danger')
        return None
    

def retrieve_patient_data(patient_id):
    try:
        response = requests.get(f'http://127.0.0.1:80/api/patient_by_id/{patient_id}')
        response.raise_for_status()
        patient_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching patient: {e}")
        patient_data = {}
    return patient_data