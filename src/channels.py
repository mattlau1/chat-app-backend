from error import InputError, AccessError

def channels_list(token):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
        ],
    }

def channels_listall(token):
    return {
        'channels': [
        	{
        		'channel_id': 1,
        		'name': 'My Channel',
        	}
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

    return {
        'channel_id': 1,
    }
