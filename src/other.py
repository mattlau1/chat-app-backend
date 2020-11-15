''' Import required modules '''
from data import data, user_with_id, user_with_token
from error import InputError, AccessError

def clear():
    '''
    Resets the internal data of the application to its initial state (no input/output)
    '''
    data['users'] = []
    data['channels'] = []
    data['latest_message_id'] = 0
    data['valid_reset_codes'] = []
    return {
    }

def users_all(token):
    '''
    Returns a list of all users and their associated details
    Input: token (str)
    Output: dict where 'user' key maps to a list of dictionaries containing user information
    '''
    # Error check
    if user_with_token(token) is None:
        # Invalid token
        raise AccessError('Invalid token')

    return {
        'users': [
            {
                'u_id': user.get_u_id(),
                'email': user.get_email(),
                'name_first': user.get_name_first(),
                'name_last': user.get_name_last(),
                'handle_str': user.get_handle(),
                'profile_img_url': user.get_profile_img_url(),
            }
            for user in data['users']
        ],
    }

def admin_userpermission_change(token, u_id, permission_id):
    '''
    Given a User by user ID, set their permissions to new permissions described by permission_id
    Input: token (str), u_id (int), permission_id (int)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    target_user = user_with_id(u_id)

    # Error check
    if auth_user is None:
        # Invalid token
        raise AccessError('Invalid token')
    elif auth_user.get_permission_id() != 1:
        # Requested user not a Flockr owner
        raise AccessError('Invalid permission')
    elif target_user is None:
        # Invalid user
        raise InputError('Invalid user')
    elif permission_id not in [1, 2]:
        # Invalid permission
        raise InputError('Invalid Permission ID')

    # Edit target_user's permissions
    target_user.set_permission_id(permission_id)

    return {
    }

def search(token, query_str):
    '''
    Given a query string, return a collection of messages in all
    of the channels that the user has joined that match the query
    Input: token (str), query_str (str)
    Output: dict where 'messages' maps to a list of dictionaries containing messages
            where query_str is a substring of the message content
    '''
    # Error check
    auth_user = user_with_token(token)
    if auth_user is None:
        # Invalid token
        raise AccessError('Invalid token')

    messages = []
    for channel in data['channels']:
        # Channels the auth_user is a member of
        if auth_user in channel.get_all_members():
            for message in channel.get_messages():
                # query_str is a substring of message
                if query_str in message.get_message():
                    messages.append(message)

    return {
        'messages': [
            {
                'message_id': message.get_message_id(),
                'u_id': message.get_sender().get_u_id(),
                'time_created': message.get_time_created(),
                'message': message.get_message(),
                'reacts': [
                    {
                        'react_id': react.get_react_id(),
                        'u_ids': [reactor.get_u_id() for reactor in react.get_reactors()],
                        'is_this_user_reacted': auth_user in react.get_reactors(),
                    }
                    for react in message.get_reacts()
                ],
                'is_pinned': message.get_is_pinned(),
            }
            for message in messages
        ],
    }
