from error import InputError, AccessError
from data import data

# initialise dictionary to store detail of the channel
scaffold = {}

def channels_list(token):
    # yet to be compeleted
    return data['channels']

def channels_listall(token):
    # yet to be completed
    return data['channels']

def channels_create(token, name, is_public):
    channel_length = len(name)
    max_channel_length = 20

    if (channel_length > max_channel_length):
        # Long channel names
        raise InputError
    if (not name):
        # Empty name
        raise InputError
    if (name.isspace()):
        # Whitespace name
        raise InputError

    # make a dictionary and append it
    d = scaffold.copy()
    d['id'] = 1
    d['name'] = name
    data['channels'].append(d)

    #if there is already a channel, change id
    if (len(data['channels']) > 1):
        d['id'] = len(data['channels'])
