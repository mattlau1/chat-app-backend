''' Import required modules '''
from datetime import datetime
from data import data, Message, user_with_token, channel_with_id, channel_with_message_id, message_with_message_id
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
    elif auth_user not in channel.all_members:
        raise AccessError('User not in channel')
    elif not message:
        raise InputError('Empty message not allowed')
    elif len(message) > 1000:
        raise InputError('Message should be 1000 characters or less')

    # Store message
    new_message = Message(auth_user, message)
    channel.messages.append(new_message)

    return {
        'message_id': new_message.message_id,
    }

def message_remove(token, message_id):
    '''
    Given a message_id for a message, this message is removed from the channel
    Input: token (str), message_id (int)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel_with_message, _ = channel_with_message_id(message_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel_with_message is None:
        raise InputError('Invalid Message ID')

    message = message_with_message_id(channel_with_message, message_id)
    user_is_channel_owner = (auth_user in channel_with_message.owner_members)
    user_is_flockr_owner = (auth_user.permission_id == 1)

    if auth_user != message.sender and not user_is_channel_owner and not user_is_flockr_owner:
        raise AccessError('Invalid permissions')

    # Remove message
    channel_with_message.messages.remove(message)

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

    sender = message_with_message_id(channel_with_message, message_id).sender
    user_is_channel_owner = (auth_user in channel_with_message.owner_members)
    user_is_flockr_owner = (auth_user.permission_id == 1)

    if auth_user != sender and not user_is_channel_owner and not user_is_flockr_owner:
        raise AccessError('Invalid permissions')

    # Update message
    channel_with_message.messages[message_index].message = message

    return {
    }
