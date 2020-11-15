''' Import required modules '''
from threading import Timer
from data import (
    current_time, user_with_token, channel_with_id,
    Message, channel_with_message_id, message_with_message_id,
    react_with_id_for_message
)
from bot import bot_message_parser
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
    bot_message_parser(token, channel_id, message)

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
    '''
    Send a message from authorised_user to the channel specified
    by channel_id automatically at a specified time in the future.
    Input: token (str), channel_id (int), message (str), time_sent (UNIX timestamp - float)
    Output: message_id (int) of message to be sent
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel = channel_with_id(channel_id)
    time_diff = time_sent - current_time()

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
    elif time_diff < 0:
        raise InputError('Time is in the past')

    # Note that message will still be sent later even if the user
    # leaves channel or logs out before message is actually sent
    new_message = Message(auth_user, message, time_created=time_sent)
    t = Timer(time_diff, channel.messages.append, args=[new_message])
    t.start()
    
    return {
        'message_id': new_message.message_id,
    }


def message_react(token, message_id, react_id):
    '''
    Given a message within a channel, add react to the message using the
    provided id.
    Input: token (str), message_id (int), react_id (int)
    Output: empty dict
    '''
    auth_user = user_with_token(token)
    message = message_with_message_id(message_id)
    if auth_user is None:
        raise AccessError('Invalid token')
    elif message is None:
        raise AccessError('Invalid message_id')
    elif react_id != 1:
        raise InputError('Invalid react_id')

    message.add_react(auth_user, react_id)

    return {
    }


def message_unreact(token, message_id, react_id):
    '''
    Given a message that has a react on it, a matching user can unreact the 
    message based on user's token.
    Input: token (str), message_id (int), react_id (int)
    Output: empty dict
    '''
    auth_user = user_with_token(token)
    message = message_with_message_id(message_id)
    if auth_user is None:
        raise AccessError('Invalid token')
    elif message is None:
        raise AccessError('Invalid message_id')
    elif react_id != 1:
        raise InputError('Invalid react_id')
    react = react_with_id_for_message(message, react_id)
    if react is None or not react.reactors:
        raise InputError('Message does not contain an active react with react_id')
    elif auth_user not in react.reactors:
        raise AccessError(f'You have not reacted to this message with react_id {react_id}')

    message.remove_react(auth_user, react_id)

    return {
    }

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
    elif message is None:
        raise InputError('Invalid message_id')
    elif auth_user not in channel.all_members:
        raise AccessError('Invalid permission')
    elif auth_user not in channel.owner_members and auth_user.permission_id != 1:
        raise AccessError('Invalid permission for pinning messages')
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
    elif message is None:
        raise InputError('Invalid message_id')
    elif auth_user not in channel.all_members:
        raise AccessError('Invalid permission')
    elif auth_user not in channel.owner_members and auth_user.permission_id != 1:
        raise AccessError('Invalid permission for unpinning messages')
    elif not message.is_pinned:
        raise InputError('Message already unpinned')

    message.is_pinned = False

    return {
    }
