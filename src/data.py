import re

# Database
data = {
    # Users - array of {id, email, password, name_first, name_last, token}
    'users': [],
    # Channels - array of {id, name, }
    'channels': [],
    # Messages
    'messages': [],
}


""" General helper functions """
# Checks to see if an email is in a valid email format
def valid_email(email):
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex, email)


""" Helper functions for users """
# Extracts all the emails for the users
def user_email_list():
    return [user['email'] for user in data['users']]

# Retrieves all the active tokens
def active_tokens():
    return [user['token'] for user in data['users'] if user['token'] != '']

# Returns the user with specified email address
def user_with_email(email):
    for user in data['users']:
        if user['email'] == email:
            return user
    return None

# Returns the user with specified token
def user_with_token(token):
    for user in data['users']:
        if user['token'] == token:
            return user
    return None

# Returns the user with specified id
def user_with_id(id):
    for user in data['users']:
        if user['id'] == id:
            return user
    return None

# Returns a list of user handles
def user_handle_list():
    return [user['handle'] for user in data['users'] if user['handle'] != '']

# Updates the token for a specified user
def user_update_token(id, new_token):
    for user in data['users']:
        if user['id'] == id:
            user['token'] = new_token
            return {'update_success': True}
    return {'update_success': False}


""" Helper functions for channels """



""" Helper functions for messages """

