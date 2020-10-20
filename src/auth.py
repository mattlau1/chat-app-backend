''' Import required modules '''
import hashlib
import jwt
from data import (
    PRIVATE_KEY, data, valid_email, user_with_email, user_with_token,
    user_email_list, user_handle_list, user_update_token,
)
from error import InputError, AccessError

# Generates a token for a registered user
def generate_token(u_id):
    '''
    Generates a JSON Web Token (JWT) encoded token for a given user id
    Input: u_id (int)
    Output: JWT-encoded token (str)
    '''
    return jwt.encode({'u_id': u_id}, PRIVATE_KEY, algorithm='HS256').decode('utf-8')

# Generates a handle for a user
def generate_handle(u_id, name_first, name_last):
    '''
    Generates a unique handle for a given user
    Input: id (int), name_first (str), name_last (str)
    Output: handle_string (str)
    '''
    # First 20 characters of concatenation of name_first and name_last
    handle_string = (name_first.lower() + name_last.lower())[:20]
    # Ensure unique
    while handle_string in user_handle_list():
        handle_string = (str(u_id) + handle_string)[:20]
    return handle_string


def auth_login(email, password):
    '''
    Logs a user in
    Input: email (str), password (str)
    Output: u_id (int) and token (str) as a dict
    '''
    user = user_with_email(email)
    encrypted_password = hashlib.sha256(password.encode()).hexdigest()
    # Error check
    if not valid_email(email):
        # Invalid email format
        raise InputError('Invalid email format')
    elif user is None:
        # Unregistered email
        raise InputError('Unregistered email')
    elif user['password'] != encrypted_password:
        # Incorrect password
        raise InputError('Incorrect password')

    # Update token
    token = generate_token(user['id'])
    user_update_token(user['id'], token)
    assert user_with_email(email)['token'] == token

    return {
        'u_id': user['id'],
        'token': token,
    }


def auth_logout(token):
    '''
    Logs a user out
    Input: token (str)
    Output: is_success (bool) as a dict
    '''
    user = user_with_token(token)
    # Check for valid token
    if user is None:
        raise AccessError('Invalid token')

    # Update user token
    user_update_token(user['id'], '')
    assert user_with_email(user['email'])['token'] == ''

    return {
        'is_success': True,
    }


def auth_register(email, password, name_first, name_last):
    '''
    Registers a user
    Input: email (str), password (str), name_first (str), name_last (str)
    Output: u_id generated (int) and token generated (str) as a dict
    '''
    # Error check
    if not valid_email(email):
        # Invalid email format
        raise InputError('Invalid email')
    elif email in user_email_list():
        # Email in use
        raise InputError('Email already taken')
    elif len(password) < 6:
        # Password length
        raise InputError('Password too short')
    elif len(name_first) not in range(1, 51):
        # name_first length
        raise InputError('First name should be between 1 and 50 characters inclusive')
    elif name_first.isspace():
        # name_first invalid
        raise InputError('First name cannot be empty')
    elif len(name_last) not in range(1, 51):
        # name_last length
        raise InputError('Last name should be between 1 and 50 characters inclusive')
    elif name_last.isspace():
        # name_last invalid
        raise InputError('Last name cannot be empty')

    # Register new user
    u_id = len(data['users']) + 1
    token = generate_token(u_id)
    encrypted_password = hashlib.sha256(password.encode()).hexdigest()
    permission_id = 1 if len(data['users']) == 0 else 2

    # Append user information to data
    data['users'].append({
        'id': u_id,
        'email': email,
        'password': encrypted_password,
        'name_first': name_first,
        'name_last': name_last,
        'handle': generate_handle(u_id, name_first, name_last),
        'permission_id': permission_id,
        'token': token,
    })

    return {
        'u_id': u_id,
        'token': token,
    }
