''' Import required modules '''
from data import data, user_with_token, user_with_id, channel_with_id
from error import InputError, AccessError

def channel_invite(token, channel_id, u_id):
    '''
    Invites a user (with user id u_id) to join a channel with ID channel_id.
    Once invited the user is added to the channel immediately
    Input: token (str), channel_id (int), u_id (int)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel = channel_with_id(channel_id)
    invited_user = user_with_id(u_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel is None:
        raise InputError('Invalid channel_id')
    elif invited_user is None:
        raise InputError('Invalid u_id')
    elif auth_user['u_id'] not in channel['all_members']:
        raise AccessError('Authorised user not a member of channel')

    # Append invited user to all_members
    for channel in data['channels']:
        if channel['channel_id'] == channel_id and invited_user['u_id'] not in channel['all_members']:
            channel['all_members'].append(invited_user['u_id'])

    return {
    }


def channel_details(token, channel_id):
    '''
    Given a Channel with ID channel_id that the authorised user is part of,
    provide basic details about the channel
    Input: token (str), channel_id (int)
    Output: dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel = channel_with_id(channel_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel is None:
        raise InputError('Invalid channel_id')
    elif auth_user['u_id'] not in channel['all_members']:
        raise AccessError('Authorised user not a member of channel')

    return {
        'name': channel['name'],
        'owner_members': [
            {
                'u_id': owner_id,
                'name_first': user_with_id(owner_id)['name_first'],
                'name_last': user_with_id(owner_id)['name_last'],
            }
            for owner_id in channel['owner_members']
        ],
        'all_members': [
            {
                'u_id': member_id,
                'name_first': user_with_id(member_id)['name_first'],
                'name_last': user_with_id(member_id)['name_last'],
            }
            for member_id in channel['all_members']
        ],
    }


def channel_messages(token, channel_id, start):
    '''
    Given a Channel with ID channel_id that the authorised user is part of,
    return up to 50 messages between index "start" and "start + 50".
    Message with index 0 is the most recent message in the channel.
    This function returns a new index "end" which is the value of "start + 50", or,
    if this function has returned the least recent messages in the channel,
    returns -1 in "end" to indicate there are no more messages to load after this return.
    Input: token (str), channel_id (int), start (int)
    Ouput: dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel = channel_with_id(channel_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel is None:
        raise InputError('Invalid channel_id')
    elif auth_user['u_id'] not in channel['all_members']:
        raise AccessError('Authorised user not a member of channel')
    elif start > len(channel['messages']):
        raise InputError('Invalid start index')

    # Messages originally ordered chronologically -
    # reverse and retrieve a maximum of 50 most recent messages
    messages = list(reversed(channel['messages']))[start : start + 50]
    # The end is reached if the first message (id) is included in messages
    if len(messages) == 0:
        end = -1
    else:
        first_message_id = channel['messages'][0]['message_id']
        first_message_reached = any(message['message_id'] == first_message_id for message in messages)
        end = -1 if first_message_reached else start + 50

    # THIS NEEDS TO BE REVIEWED
    # THIS NEEDS TO BE REVIEWED
    # THIS NEEDS TO BE REVIEWED

    return {
        'messages': messages,
        'start': start,
        'end': end,
    }


def channel_leave(token, channel_id):
    '''
    Given a channel ID, the user removed as a member of this channel
    Input: token (str), channel_id (int)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel = channel_with_id(channel_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel is None:
        raise InputError('Invalid channel_id')
    elif auth_user['u_id'] not in channel['all_members']:
        raise AccessError('Authorised user not a member of channel')

    # Remove user from all_members
    channel['all_members'].remove(auth_user['u_id'])

    # Attempt to remove user from owner_members if they are an owner
    if auth_user['u_id'] in channel['owner_members']:
        channel['owner_members'].remove(auth_user['u_id'])

    return {
    }


def channel_join(token, channel_id):
    '''
    Given a channel_id of a channel that the authorised user can join, adds them to that channel
    Input: token (str), channel_id (int)
    Output: empty dict
    '''
    # Retrieve data
    channel = channel_with_id(channel_id)
    auth_user = user_with_token(token)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel is None:
        raise InputError('Invalid channel_id')
    elif not channel['is_public'] and auth_user['permission_id'] != 1:
        raise AccessError('Private channel and authorised user is not Flockr owner')

    # Adds user to channel if not already in channel (don't want to add duplicate users to list)
    if auth_user['u_id'] not in channel['all_members']:
        channel['all_members'].append(auth_user['u_id'])

    return {
    }


def channel_addowner(token, channel_id, u_id):
    '''
    Make user with user id u_id an owner of this channel
    Input: token (str), channel_id (int), u_id (int)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel = channel_with_id(channel_id)
    new_owner = user_with_id(u_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel is None:
        raise InputError('Invalid channel_id')
    elif new_owner is None or new_owner['u_id'] not in channel['all_members']:
        raise AccessError('Invalid u_id or user is not a member in the channel')
    elif auth_user['u_id'] not in channel['owner_members'] and auth_user['permission_id'] != 1:
        raise AccessError('Authorised user is not an owner of channel and not Flockr owner')
    elif auth_user['u_id'] not in channel['all_members']:
        # Note that Flockr owner may not be a channel member
        raise AccessError('Authorised user is not a member in the channel')
    elif new_owner['u_id'] in channel['owner_members']:
        raise InputError('User to be added as an owner is already an owner in the channel')

    # Add user as owner
    channel['owner_members'].append(new_owner['u_id'])

    return {
    }


def channel_removeowner(token, channel_id, u_id):
    '''
    Remove user with user id u_id an owner of this channel
    Input: token (str), channel_id (int), u_id (int)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel = channel_with_id(channel_id)
    old_owner = user_with_id(u_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel is None:
        raise InputError('Invalid channel_id')
    elif old_owner is None:
        raise AccessError('Invalid u_id')
    elif auth_user['u_id'] not in channel['owner_members'] and auth_user['permission_id'] != 1:
        raise AccessError('Authorised user is not an owner of channel and not Flockr owner')
    elif auth_user['u_id'] not in channel['all_members']:
        # Flockr owner may not be a channel member
        raise AccessError('Authorised user is not a member in the channel')
    elif old_owner['u_id'] not in channel['owner_members']:
        raise InputError('User to be removed as an owner was not an owner in the channel')

    # Remove owner
    channel['owner_members'].remove(old_owner['u_id'])

    return {
    }
