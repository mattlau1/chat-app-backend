from data import data, user_with_token
from datetime import datetime

def message_send(token, channel_id, message):
    # No error testing yet - will add in future iteration
    message_id = 0
    # Add to data
    for channel in data['channels']:
        if channel['id'] == channel_id:
            message_id = len(channel['messages']) + 1
            channel['messages'].append({
                'message_id': message_id,
                'u_id': user_with_token(token)['id'],
                'time_created': datetime.now(),
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