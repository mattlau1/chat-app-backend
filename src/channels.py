from error import InputError, AccessError
from data import data, user_with_token

# initialise dictionary to store detail of the channel

def channels_list(token):
    authorised_user = user_with_token(token)
    # Error check
    if authorised_user is None:
        raise AccessError
    
    return {
        'channels': [
        	{
        		'channel_id': channel['id'],
        		'name': channel['name'],
        	}
            for channel in data['channels'] if authorised_user['id'] in channel['all_members']
        ],
    }

def channels_listall(token):
    # Error check
    if user_with_token(token) is None:
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
    authorised_user = user_with_token(token)
    # Error check
    if len(name) > 20:
        raise InputError
    elif (not name):
        # Empty name
        raise InputError
    elif (name.isspace()):
        # Whitespace name
        raise InputError
    elif authorised_user is None:
        raise AccessError


    # Register
    channel_id = len(data['channels']) + 1
    data['channels'].append({
        'id': channel_id,
        'name': name,
        'is_public': is_public,
        'owner_members': [authorised_user['id'],],
        'all_members': [authorised_user['id'],],
        'messages': [],
    })
    
    return {
        'channel_id': channel_id,
    }
