from flask import Blueprint
from flask_login import UserMixin
from mysql.connector import Error
from werkzeug.security import check_password_hash
import logging

models_bp = Blueprint('models', __name__)

class User(UserMixin):
    def __init__(self, id, username, is_admin, is_doctor, created_at):
        self.id = id
        self.username = username
        self.is_admin = is_admin
        self.is_doctor = is_doctor
        self.created_at = created_at

    def get_id(self):
        return self.username  # Return username

def construct_user(user_data):
    """Construct a User object from a dictionary of user data."""
    return User(
        id=user_data['id'],
        username=user_data['username'],
        is_admin=user_data['is_admin'],
        is_doctor=user_data['is_doctor'],
        created_at=user_data['created_at']
    )


    
