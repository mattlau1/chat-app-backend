from data import data, valid_email, user_with_id, user_with_token, user_email_list, user_handle_list
from error import InputError, AccessError

def user_profile(token, u_id):
    '''
    Returns information about a specified user.
    Input: token (str), u_id (int)
    Output: dict containing user's id, email, first name, last name, and handle
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    target_user = user_with_id(u_id)

    # Error check
    if auth_user is None:
        # Invalid token
        raise AccessError('Invalid token')
    elif target_user is None:
        # Invalid u_id
        raise InputError('Invalid user')

    return {
        'user': {
        	'u_id': target_user['u_id'],
        	'email': target_user['email'],
        	'name_first': target_user['name_first'],
        	'name_last': target_user['name_last'],
        	'handle_str': target_user['handle'],
        },
    }

def user_profile_setname(token, name_first, name_last):
    '''
    Update the authorised user's first and last name
    Input: token (str), name_first (str), name_last (str)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)

    # Error check
    if auth_user is None:
        # Invalid token
        raise AccessError('Invalid token')
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

    # Update name
    data['users'][auth_user['u_id']]['name_first'] = name_first
    data['users'][auth_user['u_id']]['name_last'] = name_last
    
    return {
    }


def user_profile_setemail(token, email):
    '''
    Update the authorised user's email address
    Input: token (str), email (str)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)

    # Error check
    if auth_user is None:
        # Invalid token
        raise AccessError('Invalid token')
    elif not valid_email(email):
        # Invalid email format
        raise InputError('Invalid email')
    elif email in user_email_list():
        # Email in use
        raise InputError('Email already taken')

    # Update email
    data['users'][auth_user['u_id']]['email'] = email

    return {
    }

def user_profile_sethandle(token, handle_str):
    '''
    Update the authorised user's handle (i.e. display name)
    Input: token (str), handle_str (str)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)

    # Error check
    if auth_user is None:
        # Invalid token
        raise AccessError('Invalid token')
    elif len(handle_str) not in range(3, 21):
        # Handle length
        raise InputError('Handle must be between 3 and 20 characters')
    elif handle_str.isspace():
        # Invalid handle
        raise InputError('Invalid handle')
    elif handle_str in user_handle_list():
        # Handle in use
        raise InputError('Handle already taken')

    # Update handle
    data['users'][auth_user['u_id']]['handle'] = handle_str

    return {
    }
