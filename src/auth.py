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
    Params: u_id (int)
    Returns: JWT-encoded token (str)
    '''
    return jwt.encode({'u_id': u_id}, PRIVATE_KEY, algorithm='HS256').decode('utf-8')

# Generates a handle for a user
def generate_handle(u_id, name_first, name_last):
    '''
    Generates a unique handle for a given user
    Params: id (int), name_first (str), name_last (str)
    Returns: handle_string (str)
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
    Params: email (str), password (str)
    Returns: u_id (int) and token (str) as a dict
    '''
    user = user_with_email(email)
    encrypted_password = hashlib.sha256(password.encode()).hexdigest()
    # Error check
    if not valid_email(email):
        # Invalid email format
        raise InputError
    elif user is None:
        # Unregistered email
        raise InputError
    elif user['password'] != encrypted_password:
        # Incorrect password
        raise InputError

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
    Params: token (str)
    Returns: is_success (bool) as a dict
    '''
    user = user_with_token(token)
    # Check for valid token
    if user is None:
        raise AccessError

    # Update user token
    user_update_token(user['id'], '')
    assert user_with_email(user['email'])['token'] == ''

    return {
        'is_success': True,
    }


def auth_register(email, password, name_first, name_last):
    '''
    Registers a user
    Params: email (str), password (str), name_first (str), name_last (str)
    Returns: u_id generated (int) and token generated (str) as a dict
    '''
    # Error check
    if not valid_email(email):
        # Invalid email format
        raise InputError
    elif email in user_email_list():
        # Email in use
        raise InputError
    elif len(password) < 6:
        # Password length
        raise InputError
    elif len(name_first) not in range(1, 51):
        # name_first length
        raise InputError
    elif len(name_last) not in range(1, 51):
        # name_last length
        raise InputError

    # Register new user
    u_id = len(data['users']) + 1
    token = generate_token(u_id)
    encrypted_password = hashlib.sha256(password.encode()).hexdigest()

    # Append user information to data
    data['users'].append({
        'id': u_id,
        'email': email,
        'password': encrypted_password,
        'name_first': name_first,
        'name_last': name_last,
        'handle': generate_handle(u_id, name_first, name_last),
        'token': token,
    })

    return {
        'u_id': u_id,
        'token': token,
    }
