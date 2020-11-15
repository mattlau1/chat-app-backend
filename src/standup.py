''' Import required modules '''
from data import user_with_token, channel_with_id, current_time, Message
from error import InputError, AccessError


def standup_start(token, channel_id, length):
    '''
    For a given channel, start the standup period whereby for the next "length" seconds
    if someone calls "standup_send" with a message, it is buffered in the standup queue
    then at the end of the standup period a message will be added to the message queue
    in the channel from the user who started the standup.
    Input: token (str), channel_id (int), length (int)
    Output: time_finish (UNIX timestamp int)
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel = channel_with_id(channel_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel is None:
        raise InputError('Invalid channel')
    elif auth_user not in channel.get_all_members():
        raise AccessError('User not member of channel')
    elif length <= 0:
        raise InputError('Invalid standup time')
    elif channel.get_standup_status()['is_active']:
        raise InputError('An active standup is currently running')

    end_time = channel.start_standup(initiator=auth_user, length=length)

    return {
        'time_finish': end_time,
    }


def standup_active(token, channel_id):
    '''
    For a given channel, return whether a standup is active in it,
    and what time the standup finishes. If no standup is active,
    then time_finish returns None.
    Input: token (str), channel_id (int)
    Output: is_active (bool), time_finish (UNIX timestamp int)
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel = channel_with_id(channel_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel is None:
        raise InputError('Invalid channel')
    elif auth_user not in channel.get_all_members():
        raise AccessError('User not member of channel')

    standup_status = channel.get_standup_status()

    return {
        'is_active': standup_status['is_active'],
        'time_finish': standup_status['time_finish'],
    }


def standup_send(token, channel_id, message):
    '''
    Send a message to get buffered in the standup queue,
    assuming a standup is currently active
    Input: token (str), channel_id (int), message (str)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel = channel_with_id(channel_id)

    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel is None:
        raise InputError('Invalid channel')
    elif auth_user not in channel.get_all_members():
        raise AccessError('User not member of channel')
    elif not channel.get_standup_status()['is_active']:
        raise InputError('An active standup is not currently running')
    elif not message:
        raise InputError('Empty message not allowed')
    elif len(message) > 1000:
        raise InputError('Message should be 1000 characters or less')

    # Add message to queue
    msg = Message(auth_user, message, time_created=current_time())
    channel.get_standup_status()['queued_messages'].append(msg)

    return {
    }
