import datetime

from jwt import decode
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
        decoded = decode(token, key=secret_key, algorithms=["HS256"], options={"verify_signature": False})
        user_id = decoded.get('sub', {}).get('id')
        return user_id
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None
    
def get_clinics(user_id):
    try:
        response = requests.get('http://0.0.0.0:80/api/clinics?user_id={}'.format(user_id))
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


def send_data_to_api(url, data):
    try:
        print(f"Sending data to API: {data}")  # Add this line to print the data
        response = requests.post(url, json=data)
        response.raise_for_status()
        print("success")
        flash('Data sent successfully!', 'success')
    except requests.exceptions.RequestException as e:
        print(f"error: {e}")
        flash('Failed to send data.', 'danger')
