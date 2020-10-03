import re

# Database
data = {
    # Users - array of dictionaries {
    #   id - unique integer, 
    #   email - string, 
    #   password - string, 
    #   name_first - string, 
    #   name_last - string, 
    #   token - string,
    # }
    'users': [],
    # Channels - array of dictionaries {
    #   id - unique integer, 
    #   name - string, 
    #   is_public - boolean,
    #   owner_members - array of u_id (integer corresponding to a user id),
    #   all_members - array of u_id (integer corresponding to a user id),
    #   messages - array of dictionaries {
    #       member_id - unique integer,
    #       u_id - integer corresponding to the sender's user id,
    #       time_created - datetime object,
    #       message - string,
    #   },
    # }
    'channels': [],
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

# Returns the user with specified email address
def user_with_email(email):
    for user in data['users']:
        if user['email'] == email:
            return user
    return None

# Returns the user with specified token
def user_with_token(token):
    for user in data['users']:
        if user['token'] == token and token != '':
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
# Extracts information about a specified channel (by id)
def channel_with_id(id):
    for channel in data['channels']:
        if channel['id'] == id:
            return channel
    return None

