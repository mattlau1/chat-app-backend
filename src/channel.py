from data import user_with_token, user_with_id, channel_with_id

def channel_invite(token, channel_id, u_id):
    channel = channel_with_id(channel_id)
    authorised_user = user_with_token(token)
    invited_user = user_with_id(u_id)
    if channel is None:
        raise Exception('InputError')
    elif invited_user is None:
        raise Exception('InputError')
    elif authorised_user not in channel['all_members']:
        raise Exception('AccessError')
    
    channel['all_members'].append(invited_user)

    return {
    }

def channel_details(token, channel_id):
    channel = channel_with_id(channel_id)
    authorised_user = user_with_token(token)
    if channel is None:
        raise Exception('InputError')
    elif authorised_user not in channel['all_members']:
        raise Exception('AccessError')

    return {
        'name': 'Hayden',
        'owner_members': [
            {
                'u_id': 1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            }
            for owner in channel['owner_members']
        ],
        'all_members': [
            {
                'u_id': 1,
                'name_first': 'Hayden',
                'name_last': 'Jacobs',
            }
            for member in channel['all_members']
        ],
    }

def channel_messages(token, channel_id, start):
    channel = channel_with_id(channel_id)
    authorised_user = user_with_token(token)
    if channel is None:
        raise Exception('InputError')
    elif start > len(channel['messages']):
        raise Exception('InputError')
    elif authorised_user not in channel['all_members']:
        raise Exception('AccessError')
    return {
        'messages': [
            {
                'message_id': 1,
                'u_id': 1,
                'message': 'Hello world',
                'time_created': 1582426789,
            }
        ],
        'start': 0,
        'end': 50,
        # Must account for 'end' being -1
    }

def channel_leave(token, channel_id):
    channel = channel_with_id(channel_id)
    authorised_user = user_with_token(token)
    if channel is None:
        raise Exception('InputError')
    elif authorised_user is None:
        raise Exception('AccessError')

    if authorised_user in channel['owner_members']:
        channel['owner_members'].remove(authorised_user)
    if authorised_user in channel['all_members']:
        channel['all_members'].remove(authorised_user)
    
    return {
    }

def channel_join(token, channel_id):
    channel = channel_with_id(channel_id)
    authorised_user = user_with_token(token)
    if channel is None:
        raise Exception('InputError')
    elif authorised_user is None:
        raise Exception('AccessError')

    if authorised_user in channel['owner_members']:
        channel['owner_members'].append(authorised_user)
    if authorised_user in channel['all_members']:
        channel['all_members'].append(authorised_user)
    
    return {
    }

def channel_addowner(token, channel_id, u_id):
    channel = channel_with_id(channel_id)
    authorised_user = user_with_token(token)    
    new_owner = user_with_id(u_id)
    if channel is None:
        raise Exception('InputError')
    elif new_owner in channel['owner_members']:
        raise Exception('InputError')
    elif authorised_user not in channel['owner_mmebers']:
        raise Exception('AccessError')

    channel['owner_members'].append(new_owner)

    return {
    }

def channel_removeowner(token, channel_id, u_id):
    channel = channel_with_id(channel_id)
    authorised_user = user_with_token(token)
    old_owner = user_with_id(u_id)
    if channel is None:
        raise Exception('InputError')
    elif old_owner not in channel['owner_members']:
        raise Exception('InputError')
    elif authorised_user not in channel['owner_members']:
        raise Exception('AccessError')

    channel['owner_members'].remove(old_owner)

    return {
    }