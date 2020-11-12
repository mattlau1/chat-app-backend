''' Import required modules '''
from data import (data, User, valid_email, jwt_encode_payload, jwt_decode_string,
                  user_with_email, user_with_token, user_email_list)
from error import InputError, AccessError

def auth_login(email, password):
    '''
    Logs a user in
    Input: email (str), password (str)
    Output: u_id (int) and token (str) as a dict
    '''
    user = user_with_email(email)
    # Error check
    if not valid_email(email):
        # Invalid email format
        raise InputError('Invalid email format')
    elif user is None:
        # Unregistered email
        raise InputError('Unregistered email')
    elif not user.verify_password(password):
        # Incorrect password
        raise InputError('Incorrect password')

    # Update token
    user.token = user.generate_token()

    return {
        'u_id': user.u_id,
        'token': user.token,
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

    # Invalidate user token - session stuff in future iterations?
    user.token = ''

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
    new_user = User(email, password, name_first, name_last)
    data['users'].append(new_user)

    return {
        'u_id': new_user.u_id,
        'token': new_user.token,
    }


def generate_reset_code(email):
    '''
    Generates a reset code for a User given their email address
    Input: email (string)
    Output: reset_code (string)
    '''
    user = user_with_email(email)

    # Error checks
    if not valid_email(email):
        raise InputError('Invalid email')
    if user is None:
        raise InputError('Unregistered email')

    # Generate, store and return random reset code
    reset_code = jwt_encode_payload({'email': email})
    if reset_code not in data['valid_reset_codes']:
        data['valid_reset_codes'].append(reset_code)

    return reset_code


def password_reset(reset_code, new_password):
    '''
    Updates the password of a User to new_password, given a reset_code
    Input: reset_code (string), new_password (string)
    Output: empty dict
    '''
    # Error check
    if len(new_password) < 6:
        # Password length
        raise InputError('Password too short')

    # Decode reset_code
    try:
        payload = jwt_decode_string(reset_code)
        user = user_with_email(payload['email'])
        # Check reset_code is still valid
        if reset_code not in data['valid_reset_codes']:
            raise InputError('Invalid reset code')
        user.update_password(new_password)
        # Invalidate current reset_code
        data['valid_reset_codes'].remove(reset_code)
    except:
        raise InputError('Invalid reset code')

    return {
    }
