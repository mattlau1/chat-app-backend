from data import (
    data, valid_email, user_with_email, user_with_token,
    user_email_list, user_handle_list, active_tokens, user_update_token,
)
from error import InputError, AccessError

# Generates a token for a registered user
def generate_token(id):
    # import user_with_id for future iterations
    return str(id)

# Generates a handle for a user
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
    assert user is not None
    token = ''
    if user['password'] == password:
        token = generate_token(user['id'])
    else:
        raise InputError
    
    # Update token
    updated = user_update_token(user['id'], token)
    assert updated['update_success'] == True
    assert user_with_email(email)['token'] == token

    return {
        'u_id': user['id'],
        'token': token,
    }


def auth_logout(token):
    # Check for valid token
    if token not in active_tokens():
        raise AccessError
    
    # Update user token
    user = user_with_token(token)
    assert user is not None
    updated = user_update_token(user['id'], '')
    assert updated['update_success'] == True
    assert user_with_email(user['email'])['token'] == ''
    
    return {
        'is_success': True,
    }


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
    token = generate_token(id)
    user_info = {
        'id': id,
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last,
        'handle': generate_handle(id, name_first, name_last),
        'token': token,
    }
    data['users'].append(user_info)
    
    return {
        'u_id': id,
        'token': token,
    }
