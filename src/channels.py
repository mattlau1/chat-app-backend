''' Import required modules '''
from data import data, user_with_token
from error import InputError, AccessError

def channels_list(token):
    '''
    Provide a list of all channels (and their associated details) that the auth user is part of
    Input: token (str)
    Output: dict
    '''
    auth_user = user_with_token(token)
    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')

    return {
        'channels': [
            {
                'channel_id': channel['channel_id'],
                'name': channel['name'],
            }
            for channel in data['channels'] if auth_user['u_id'] in channel['all_members']
        ],
    }

def channels_listall(token):
    '''
    Provide a list of all channels (and their associated details)
    Input: token (str)
    Output: dict
    '''
    # Error check
    if user_with_token(token) is None:
        raise AccessError('Invalid token')

    return {
        'channels': [
            {
                'channel_id': channel['channel_id'],
                'name': channel['name'],
            }
            for channel in data['channels']
        ],
    }

def channels_create(token, name, is_public):
    '''
    Creates a new channel with that name that is either a public or private channel
    Input: token (str), name (str), is_public (boolean)
    Output: dict
    '''
    auth_user = user_with_token(token)
    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif len(name) > 20:
        raise InputError('Name longer than 20 characters')
    elif not name:
        raise InputError('Empty name')
    elif name.isspace():
        raise InputError('Whitespace name')

    # Register
    channel_id = len(data['channels'])
    data['channels'].append({
        'channel_id': channel_id,
        'name': name,
        'is_public': is_public,
        'owner_members': [auth_user['u_id'],],
        'all_members': [auth_user['u_id'],],
        'messages': [],
    })

    return {
        'channel_id': channel_id,
    }
