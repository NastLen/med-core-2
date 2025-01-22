import datetime
import requests


from flask import flash
import simplejson as json

def load_form_fields(request):
    form_fields = {}
    for field in request.form:
        form_fields[field] = request.form[field]
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
