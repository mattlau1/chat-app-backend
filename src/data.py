''' Import required modules '''
import re
import jwt

# Private key for jwt encoding and decoding
PRIVATE_KEY = 'aHR0cHM6Ly95b3V0dS5iZS9kUXc0dzlXZ1hjUQ=='


################
### Database ###
################
data = {
    # Users - array of dictionaries {
    #   u_id - unique integer (stored sequentially starting from index 0),
    #   email - string,
    #   password - string,
    #   name_first - string,
    #   name_last - string,
    #   handle - string,
    #   permission_id - int,
    #   token - string,
    # }
    'users': [],
    # Channels - array of dictionaries {
    #   channel_id - unique integer (stored sequentially starting from index 0),
    #   name - string,
    #   is_public - boolean,
    #   owner_members - array of u_id (integer corresponding to a user id),
    #   all_members - array of u_id (integer corresponding to a user id),
    #   messages - array of dictionaries {
    #       message_id - unique integer,
    #       u_id - integer corresponding to the sender's user id,
    #       time_created - UNIX timestamp (float),
    #       message - string,
    #   },
    # }
    'channels': [],
    # Stores the latest message_id used across all channels
    'latest_message_id': 0,
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
    if 0 <= u_id < len(data['users']):
        return data['users'][u_id]
    return None

def user_with_token(token):
    '''
    Tries to return user (dict) with specified token (str), returning None if not found
    '''
    try:
        # Decode token and pass user id to user_with_id()
        payload = jwt.decode(token.encode('utf-8'), PRIVATE_KEY, algorithms=['HS256'])
        u_id = payload['u_id']
        # Check for valid session (future iterations?)
        if data['users'][u_id]['token'] != '':
            return user_with_id(payload['u_id'])
        return None
    except:
        return None


#####################################
### Helper functions for channels ###
#####################################
def channel_with_id(channel_id):
    '''
    Extracts information about a specified channel (by id)
    Tries to return channel (dict) with specified channel id (int), returning None if not found
    '''
    if 0 <= channel_id < len(data['channels']):
        return data['channels'][channel_id]
    return None

def channel_with_message_id(message_id):
    '''
    Tries to return a tuple of the channel (channel info dict) containing the
    message with specified message_id (int) and the index that the message is stored
    under the channel, both returning None if not found
    '''
    for channel in data['channels']:
        for message_index, message in enumerate(channel['messages']):
            if message['message_id'] == message_id:
                return (channel, message_index)
    return (None, None)

def message_with_id(message_id):
    '''
    Tries to return the message (message info dict) corresponding
    to a given message_id (int), returning None if not found
    '''
    for channel in data['channels']:
        for message in channel['messages']:
            if message['message_id'] == message_id:
                return message
    return None
