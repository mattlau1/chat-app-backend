from error import InputError, AccessError
from data import (
    valid_email, user_email_list, user_handle_list, user_with_id, user_with_token
)
def user_profile(token, u_id):
    # invalid token
    if user_with_token(token) is None :
        raise AccessError('Invalid token')
    # invalid id
    if user_with_id(u_id) is None:
        raise AccessError('Invalid ID')

    return {
        'user': {
        	'u_id': 1,
        	'email': 'cs1531@cse.unsw.edu.au',
        	'name_first': 'Hayden',
        	'name_last': 'Jacobs',
        	'handle_str': 'hjacobs',
        },
    }

def user_profile_setname(token, name_first, name_last):
    # invalid token
    if user_with_token(token) is None :
        raise AccessError('Invalid token')
    # invalid name length
    if len(name_first) not in range(1, 51):
        raise InputError('First name should be between 1 and 50 characters inclusive')
    if len(name_last) not in range(1, 51):
        raise InputError('Last name should be between 1 and 50 characters inclusive')
    
    return {
    }

def user_profile_setemail(token, email):
    if not valid_email(email):
        # Invalid email format
        raise InputError('Invalid email format')
    elif email in user_email_list():
        # Email in use
        raise InputError('Email already taken')

    return {
    }

def user_profile_sethandle(token, handle_str):
    handle_len = len(handle_str)
    if handle_len <= 3 or handle_len >= 20:
        # Invalid handle length (too short or too long)
        raise InputError('handle_str must be between 3 and 20 characters')
    elif handle_str in user_handle_list():
        # Handle in use
        raise InputError('handle is already used by another user')

    return {
    }