import re
from werkzeug.security import generate_password_hash


def validate_user_input(data):
    errors = {}

    if 'username' not in data or not data['username'].strip():
        errors['username'] = 'Username is required'
    elif len(data['username']) < 3:
        errors['username'] = 'Username must be at least 3 characters'

    if 'email' not in data or not data['email'].strip():
        errors['email'] = 'Email is required'
    elif not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
        errors['email'] = 'Invalid email format'

    if 'password' not in data or not data['password'].strip():
        errors['password'] = 'Password is required'
    elif len(data['password']) < 8:
        errors['password'] = 'Password must be at least 8 characters'

    return errors