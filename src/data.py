import re
import jwt

# Private key for jwt encoding and decoding
PRIVATE_KEY = 'aHR0cHM6Ly95b3V0dS5iZS9kUXc0dzlXZ1hjUQ=='


################
### Database ###
################
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
    #       message_id - unique integer,
    #       u_id - integer corresponding to the sender's user id,
    #       time_created - datetime object,
    #       message - string,
    #   },
    # }
    'channels': [],
}


################################
### General helper functions ###
################################
def valid_email(email):
    '''
    Checks to see if an email is in a valid email format
    Returns match object for input email (str)
    '''
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex, email)


##################################
### Helper functions for users ###
##################################
def user_email_list():
    '''
    Returns a list containing all the user emails (str)
    '''
    return [user['email'] for user in data['users']]

def user_handle_list():
    '''
    Returns a list containing all the user handles (str)
    '''
    return [user['handle'] for user in data['users'] if user['handle'] != '']

def user_with_email(email):
    '''
    Tries to return user (dict) with specified email address (str), returning None if not found
    '''
    for user in data['users']:
        if user['email'] == email:
            return user
    return None

def user_with_id(u_id):
    '''
    Tries to return user (dict) with specified user id (int), returning None if not found
    '''
    for user in data['users']:
        if user['id'] == u_id:
            return user
    return None

def user_with_token(token):
    '''
    Tries to return user (dict) with specified token (str), returning None if not found
    '''
    try:
        # Decode token and pass user id to user_with_id()
        payload = jwt.decode(token.encode('utf-8'), PRIVATE_KEY, algorithms=['HS256'])
        return user_with_id(payload['u_id'])
    except:
        return None

def user_update_token(u_id, new_token):
    '''
    Updates the token for a given user id (int) with new_token (str)
    '''
    for user in data['users']:
        if user['id'] == u_id:
            user['token'] = new_token


#####################################
### Helper functions for channels ###
#####################################
def channel_with_id(c_id):
    '''
    Extracts information about a specified channel (by id)
    Tries to return channel (dict) with specified channel id (int), returning None if not found
    '''
    for channel in data['channels']:
        if channel['id'] == c_id:
            return channel
    return None
