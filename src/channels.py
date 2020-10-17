from data import data, user_with_token
from error import InputError, AccessError

def channels_list(token):
    auth_user = user_with_token(token)
    # Error check
    if auth_user is None:
        # Invalid token
        raise AccessError
    
    return {
        'channels': [
        	{
        		'channel_id': channel['id'],
        		'name': channel['name'],
        	}
            for channel in data['channels'] if auth_user['id'] in channel['all_members']
        ],
    }

def channels_listall(token):
    # Error check
    if user_with_token(token) is None:
        # Invalid token
        raise AccessError

    return {
        'channels': [
        	{
        		'channel_id': channel['id'],
        		'name': channel['name'],
        	}
            for channel in data['channels']
        ],
    }

def channels_create(token, name, is_public):
    auth_user = user_with_token(token)
    # Error check
    if len(name) > 20:
        # Name longer than 20 characters
        raise InputError
    elif not name:
        # Empty name
        raise InputError
    elif name.isspace():
        # Whitespace name
        raise InputError
    elif auth_user is None:
        # Invalid token
        raise AccessError

    # Register
    channel_id = len(data['channels']) + 1
    data['channels'].append({
        'id': channel_id,
        'name': name,
        'is_public': is_public,
        'owner_members': [auth_user['id'],],
        'all_members': [auth_user['id'],],
        'messages': [],
    })
    
    return {
        'channel_id': channel_id,
    }
