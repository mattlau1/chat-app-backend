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
    Output: time_finish (UNIX timestamp - float)
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    channel = channel_with_id(channel_id)
    
    # Error check
    if auth_user is None:
        raise AccessError('Invalid token')
    elif channel is None:
        raise InputError('Invalid channel')
    elif length <= 0:
        raise InputError('Invalid standup time')
    elif channel.standup_status['is_active']:
        raise InputError('An active standup is currently running')

    end_time = channel.start_standup(initiator=auth_user, length=length)

    # Threading for end_standup

    return {
        'time_finish': end_time,
    }


def standup_active(token, channel_id):
    pass

def standup_send(token, channel_id, message):
    pass
