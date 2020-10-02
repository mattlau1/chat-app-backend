from error import InputError, AccessError
from data import data, user_with_token

# initialise dictionary to store detail of the channel
scaffold = {}

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
    channel_length = len(name)
    max_channel_length = 20

    if (channel_length > max_channel_length):
        # Long channel names
        raise InputError
    if (not name):
        # Empty name
        raise InputError
    if (name.isspace()):
        # Whitespace name
        raise InputError

    # make a dictionary and append it
    d = scaffold.copy()
    d['id'] = 1
    d['name'] = name
    data['channels'].append(d)

    #if there is already a channel, change id
    if (len(data['channels']) > 1):
        d['id'] = len(data['channels'])
