''' Import required modules '''
import threading
from data import (
    current_time, user_with_token, channel_with_id,
    Message, channel_with_message_id, message_with_message_id
)
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
    new_message = Message(auth_user, message, current_time())
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
    channel = channel_with_message_id(message_id)
    message = message_with_message_id(message_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif message is None:
        raise InputError('Invalid Message ID')

    user_is_channel_owner = (auth_user in channel.owner_members)
    user_is_flockr_owner = (auth_user.permission_id == 1)

    if auth_user is not message.sender and not user_is_channel_owner and not user_is_flockr_owner:
        raise AccessError('Invalid permissions')

    # Remove message
    channel.messages.remove(message)

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
    channel = channel_with_message_id(message_id)
    message_object = message_with_message_id(message_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif message_object is None:
        raise InputError('Invalid Message ID')

    sender = message_object.sender
    user_is_channel_owner = (auth_user in channel.owner_members)
    user_is_flockr_owner = (auth_user.permission_id == 1)

    if auth_user is not sender and not user_is_channel_owner and not user_is_flockr_owner:
        raise AccessError('Invalid permissions')

    # Update message
    message_object.message = message

    return {
    }

def message_sendlater(token, channel_id, message, time_sent):
    pass

def message_react(token, message_id, react_id):
    pass

def message_unreact(token, message_id, react_id):
    pass

def message_pin(token, message_id):
    '''
    Given a message within a channel, mark it as "pinned" to be given special
    display treatment by the frontend.
    Input: token (str), message_id (int)
    Output: empty dict
    '''
    auth_user = user_with_token(token)
    channel = channel_with_message_id(message_id)
    message = message_with_message_id(message_id)

    if auth_user is None:
        raise AccessError('Invalid token')
    elif auth_user not in channel.all_members:
        raise AccessError('Invalid permission')
    elif auth_user not in channel.owner_members and auth_user.permission_id != 1:
        # Only owners can pin messages
        raise AccessError('Invalid permission for pinning messages')
    elif message is None:
        raise InputError('Invalid message_id')
    elif message.is_pinned:
        raise InputError('Message already pinned')

    message.is_pinned = True

    return {
    }

def message_unpin(token, message_id):
    '''
    Given a message within a channel, remove it's mark as unpinned.
    Input: token (str), message_id (int)
    Output: empty dict
    '''
    auth_user = user_with_token(token)
    channel = channel_with_message_id(message_id)
    message = message_with_message_id(message_id)

    if auth_user is None:
        raise AccessError('Invalid token')
    elif auth_user not in channel.all_members:
        raise AccessError('Invalid permission')
    elif auth_user not in channel.owner_members and auth_user.permission_id != 1:
        # Only owners can pin messages
        raise AccessError('Invalid permission for unpinning messages')
    elif message is None:
        raise InputError('Invalid message_id')
    elif not message.is_pinned:
        raise InputError('Message already unpinned')

    message.is_pinned = False

    return {
    }
