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
        # Invalid token
        raise AccessError('Invalid token')
    elif channel is None:
        # Invalid channel_id
        raise InputError('Invalid channel')
    elif auth_user['id'] not in channel['all_members']:
        # User not a channel member
        raise AccessError('User not in channel')
    elif not message:
        # Empty message (whitespace allowed)
        raise InputError('Empty message not allowed')
    elif len(message) > 1000:
        # Message longer than 1000 characters
        raise InputError('Message should be 1000 characters or less')

    # Store message
    message_id = data['latest_message_id'] + 1
    data['latest_message_id'] += 1

    for channel in data['channels']:
        if channel['id'] == channel_id:
            channel['messages'].append({
                'message_id': message_id,
                'sender': auth_user['id'],
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
