''' Import required modules '''
from datetime import datetime
from data import data, user_with_token, channel_with_id, channel_with_message_id, message_with_id
from error import InputError, AccessError

def message_send(token, channel_id, message):
    '''
    Sends the message (str) by storing it in the channel
    with channel_id (int) and sender as user with token (str)
    Returns message_id (int) of message stored
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
    return {
    }

def message_edit(token, message_id, message):
    return {
    }
