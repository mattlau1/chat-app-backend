from data import data, user_with_token

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
    authorised_user = user_with_token(token)
    assert authorised_user is not None
    # Error check
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
