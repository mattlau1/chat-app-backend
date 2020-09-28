from data import data, valid_email, user_email_list, user_handle_list, user_with_email, user_update_token
from error import InputError, AccessError

def generate_handle(id, name_first, name_last):
    # First 20 characters of concatenation of name_first and name_last
    handle_string = (name_first.lower() + name_last.lower())[:20]
    while handle_string in user_handle_list():
        handle_string = (str(id) + handle_string)[:20]
    return handle_string


def auth_login(email, password):
    # Error check
    # Invalid email format
    if not valid_email(email):
        raise InputError
    # Unregistered email
    elif email not in user_email_list():
        raise InputError
    
    # Login attempt
    user = user_with_email(email)
    token = ''
    if user['password'] == password:
        token = str(user['id'])
    else:
        raise InputError
    
    # Update token
    updated = user_update_token(user['id'], token)
    assert updated['update_success'] == True

    return {
        'u_id': user['id'],
        'token': token,
    }

def auth_logout(token):
    for user in data['users']:
        if user['token'] == token:
            # Invalidate token
            user['token'] = ''
            return {'is_success': True}
    return {'is_success': False}

def auth_register(email, password, name_first, name_last):
    # Error check
    # Invalid email format
    if not valid_email(email):
        raise InputError
    # Email in use
    elif email in user_email_list():
        raise InputError
    # Password length
    elif len(password) < 6:
        raise InputError
    # name_first length
    elif len(name_first) not in range(1, 51):
        raise InputError
    # name_last length
    elif len(name_last) not in range(1, 51):
        raise InputError

    # Register new user
    id = len(data['users']) + 1
    user_info = {
        'id': id,
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last,
        'handle': generate_handle(id, name_first, name_last),
        'token': str(id),
    }
    data['users'].append(user_info)
    
    return {
        'u_id': id,
        'token': str(id),
    }
