from data import (
    data, valid_email, user_with_email, user_with_token,
    user_email_list, user_handle_list, user_update_token,
)
from error import InputError, AccessError

# Generates a token for a registered user
def generate_token(id):
    # import user_with_id and maybe datetime for future iterations
    return str(id)

# Generates a handle for a user
def generate_handle(id, name_first, name_last):
    # First 20 characters of concatenation of name_first and name_last
    handle_string = (name_first.lower() + name_last.lower())[:20]
    # Ensure unique
    while handle_string in user_handle_list():
        handle_string = (str(id) + handle_string)[:20]
    return handle_string


def auth_login(email, password):
    user = user_with_email(email)
    # Error check
    if not valid_email(email):
        # Invalid email format
        raise InputError
    elif user is None:
        # Unregistered email
        raise InputError
    elif user['password'] != password:
        # Incorrect password
        raise InputError
    
    # Update token
    token = generate_token(user['id'])
    updated = user_update_token(user['id'], token)
    assert updated['update_success'] == True
    assert user_with_email(email)['token'] == token

    return {
        'u_id': user['id'],
        'token': token,
    }


def auth_logout(token):
    user = user_with_token(token)
    # Check for valid token
    if user is None:
        raise AccessError
    
    # Update user token
    updated = user_update_token(user['id'], '')
    assert updated['update_success'] == True
    assert user_with_email(user['email'])['token'] == ''
    
    return {
        'is_success': True,
    }


def auth_register(email, password, name_first, name_last):
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
    id = len(data['users']) + 1
    token = generate_token(id)
    # Append user information to data
    data['users'].append({
        'id': id,
        'email': email,
        'password': password,
        'name_first': name_first,
        'name_last': name_last,
        'handle': generate_handle(id, name_first, name_last),
        'token': token,
    })
    
    return {
        'u_id': id,
        'token': token,
    }
