''' Import required modules '''
from datetime import datetime
from data import data, user_with_token, channel_with_id, channel_with_message_id, message_with_id
from error import InputError, AccessError


def message_send(token, channel_id, message):
    '''
    Sends the message (str) by storing it in the channel
    with channel_id (int) and sender as user with token (str)
    Output: message_id (int) of message stored
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel = channel_with_id(channel_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel is None:
        raise InputError('Invalid channel')
    elif auth_user['u_id'] not in channel['all_members']:
        raise AccessError('User not in channel')
    elif not message:
        raise InputError('Empty message not allowed')
    elif len(message) > 1000:
        raise InputError('Message should be 1000 characters or less')

    # Store message
    message_id = data['latest_message_id'] + 1
    data['latest_message_id'] += 1

    channel['messages'].append({
        'message_id': message_id,
        'u_id': auth_user['u_id'],
        'time_created': datetime.timestamp(datetime.now()),
        'message': message,
    })

    return {
        'message_id': message_id,
    }

def message_remove(token, message_id):
    '''
    Given a message_id for a message, this message is removed from the channel
    Input: token (str), message_id (int)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    message = message_with_id(message_id)
    channel_with_message, _ = channel_with_message_id(message_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel_with_message is None:
        raise InputError('Invalid Message ID')

    sender = message['u_id']
    user_is_channel_owner = (auth_user['u_id'] in channel_with_message['owner_members'])
    user_is_flockr_owner = (auth_user['permission_id'] == 1)

    if auth_user['u_id'] != sender and not user_is_channel_owner and not user_is_flockr_owner:
        raise AccessError('Invalid permissions')

    # Remove message
    channel_id = channel_with_message['channel_id']
    data['channels'][channel_id]['messages'].remove(message)

    return {
    }


def message_edit(token, message_id, message):
    '''
    Given a message, update its text with new text.
    If the new message is an empty string, the message is deleted.
    Input: token (str), message_id (int), message (str)
    Output: empty dict
    '''
    # Remove message if empty ('')
    if not message:
        return message_remove(token, message_id)

    # Retrieve data
    auth_user = user_with_token(token)
    channel_with_message, message_index = channel_with_message_id(message_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel_with_message is None:
        raise InputError('Invalid Message ID')

    sender = message_with_id(message_id)['u_id']
    user_is_channel_owner = (auth_user['u_id'] in channel_with_message['owner_members'])
    user_is_flockr_owner = (auth_user['permission_id'] == 1)

    if auth_user['u_id'] != sender and not user_is_channel_owner and not user_is_flockr_owner:
        raise AccessError('Invalid permissions')

    # Update message
    channel_id = channel_with_message['channel_id']
    data['channels'][channel_id]['messages'][message_index]['message'] = message

    return {
    }
