''' Import required modules '''
from data import data, user_with_id, user_with_token
from error import InputError, AccessError

def clear():
    '''
    Resets the internal data of the application to its initial state (no input/output)
    '''
    data['users'] = []
    data['channels'] = []
    data['latest_message_id'] = 0
    return {
    }

def users_all(token):
    '''
    Returns a list of all users and their associated details
    Input: token (str)
    Output: dict where 'user' key maps to a list of dictionaries containing user information
    '''
    # Error check
    if user_with_token(token) is None:
        # Invalid token
        raise AccessError('Invalid token')
    
    return {
        'users': [
            {
                'u_id': user['u_id'],
                'email': user['email'],
                'name_first': user['name_first'],
                'name_last': user['name_last'],
                'handle_str': user['handle'],
            }
            for user in data['users']
        ],
    }

def admin_userpermission_change(token, u_id, permission_id):
    pass

def search(token, query_str):
    '''
    Given a query string, return a collection of messages in all
    of the channels that the user has joined that match the query
    Input: token (str), query_str (str)
    Output: dict where 'messages' maps to a list of dictionaries containing messages
            where query_str is a substring of the message content
    '''
    # Error check
    auth_user = user_with_token(token)
    if auth_user is None:
        # Invalid token
        raise AccessError('Invalid token')

    messages = []
    for channel in data['channels']:
        # Channels the auth_user is a member of
        if auth_user['u_id'] in channel['all_members']:
            for message in channel['messages']:
                # query_str is a substring of message
                if query_str in message['message']:
                    messages.append(message)

    return {
        'messages': messages,
    }
