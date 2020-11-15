''' Import required modules '''
from data import data, Channel, user_with_token
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
                'channel_id': channel.get_channel_id(),
                'name': channel.get_name(),
            }
            for channel in data['channels'] if auth_user in channel.get_all_members()
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
                'channel_id': channel.get_channel_id(),
                'name': channel.get_name(),
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
    new_channel = Channel(auth_user, name, is_public)
    data['channels'].append(new_channel)

    return {
        'channel_id': new_channel.get_channel_id(),
    }
