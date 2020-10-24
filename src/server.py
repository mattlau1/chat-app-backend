''' Import required modules '''
import sys
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from error import InputError
from auth import auth_login, auth_logout, auth_register
from channel import (channel_invite, channel_details, channel_messages, channel_leave,
                     channel_join, channel_addowner, channel_removeowner)
from channels import channels_list, channels_listall, channels_create
from message import message_send, message_remove, message_edit
from user import user_profile, user_profile_setname, user_profile_setemail, user_profile_sethandle
from other import users_all, admin_userpermission_change, search, clear

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

###############
## HTTP auth ##
###############
@APP.route('/auth/login', methods=['POST'])
def http_auth_login():
    '''
    Wrapper function for auth_login (logs a user in)
    POST: JSON containing "email" (str) and "password" (str)
    Returns JSON containing "u_id" (int) and "token" (str)
    '''
    payload = request.get_json()
    return dumps(auth_login(payload['email'], payload['password']))


@APP.route('/auth/logout', methods=['POST'])
def http_auth_logout():
    '''
    Wrapper function for auth_logout (logs a user out)
    POST: JSON containing "token" (str)
    Returns JSON containing "is_success" (bool)
    '''
    payload = request.get_json()
    return dumps(auth_logout(payload['token']))


@APP.route('/auth/register', methods=['POST'])
def http_auth_register():
    '''
    Wrapper function for auth_register (registers a new user)
    POST: JSON containing "email" (str), "password" (str), "name_first" (str), "name_last" (str)
    Returns JSON containing "u_id" (int), "token" (str)
    '''
    payload = request.get_json()
    return dumps(auth_register(payload['email'],
                               payload['password'],
                               payload['name_first'],
                               payload['name_last']))


##################
## HTTP channel ##
##################
@APP.route('/channel/invite', methods=['POST'])
def http_channel_invite():
    '''
    Wrapper function for channel_invite (invites a user to channel)
    POST: JSON containing "token" (str), "channel_id" (int), "u_id" (int)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(channel_invite(payload['token'], payload['channel_id'], payload['u_id']))


@APP.route('/channel/details', methods=['GET'])
def http_channel_details():
    '''
    Wrapper function for channel_details (returns details about a channel)
    GET: JSON containing "token" (str), "channel_id" (int)
    Returns JSON containing channel "name" (str),
            "owner_members" (list of dicts), "all_members" (list of dicts)
    '''
    return dumps(channel_details(request.args.get('token', type=str),
                                 request.args.get('channel_id', type=int)))


@APP.route('/channel/messages', methods=['GET'])
def http_channel_messages():
    '''
    Wrapper function for channel_messages (retrieves messages in a channel)
    GET: JSON containing "token" (str), "channel_id" (int), "start" (int)
    Returns JSON containing "messages" (list of dicts), "start" (int), "end" (int)
    '''
    return dumps(channel_messages(request.args.get('token', type=str),
                                  request.args.get('channel_id', type=int),
                                  request.args.get('start', type=int)))


@APP.route('/channel/leave', methods=['POST'])
def http_channel_leave():
    '''
    Wrapper function for channel_leave (request to leave a channel)
    POST: JSON containing "token" (str), "channel_id" (int)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(channel_leave(payload['token'], payload['channel_id']))


@APP.route('/channel/join', methods=['POST'])
def http_channel_join():
    '''
    Wrapper function for channel_join (request to join a channel)
    POST: JSON containing "token" (str), "channel_id" (int)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(channel_join(payload['token'], payload['channel_id']))


@APP.route('/channel/addowner', methods=['POST'])
def http_channel_addowner():
    '''
    Wrapper function for channel_addowner (adds a new channel owner)
    POST: JSON containing "token" (str), "channel_id" (int), "u_id" (int)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(channel_addowner(payload['token'], payload['channel_id'], payload['u_id']))


@APP.route('/channel/removeowner', methods=['POST'])
def http_channel_removeowner():
    '''
    Wrapper function for channel_removeowner (removes a channel owner)
    POST: JSON containing "token" (str), "channel_id" (int), "u_id" (int)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(channel_removeowner(payload['token'], payload['channel_id'], payload['u_id']))


###################
## HTTP channels ##
###################
@APP.route('/channels/list', methods=['GET'])
def http_channels_list():
    '''
    Wrapper function for channels_list (retrieves channels user is in)
    GET: JSON containing "token" (str)
    Returns JSON containing "channels" (list of dicts)
    '''
    return dumps(channels_list(request.args.get('token')))


@APP.route('/channels/listall', methods=['GET'])
def http_channels_listall():
    '''
    Wrapper function for channels_listall (retrieves all channels)
    GET: JSON containing "token" (str)
    Returns JSON containing "channels" (list of dicts)
    '''
    return dumps(channels_listall(request.args.get('token')))


@APP.route('/channels/create', methods=['POST'])
def http_channels_create():
    '''
    Wrapper function for channels_create (creates a new channel)
    POST: JSON containing "token" (str), "name" (str), "is_public" (bool)
    Returns JSON containing "channel_id" (int)
    '''
    payload = request.get_json()
    return dumps(channels_create(payload['token'], payload['name'], payload['is_public']))


##################
## HTTP message ##
##################
@APP.route('/messages/send', methods=['POST'])
def http_messages_send():
    '''
    Wrapper function for messages_send (sends a message to channel)
    POST: JSON containing "token" (str), "channel_id" (int), "message" (str)
    Returns JSON containing "message_id" (int)
    '''
    payload = request.get_json()
    return dumps(message_send(payload['token'], payload['channel_id'], payload['message']))


@APP.route('/messages/remove', methods=['DELETE'])
def http_messages_remove():
    '''
    Wrapper function for messages_remove (removes a message)
    DELETE: JSON containing "token" (str), "message_id" (int)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(message_remove(payload['token'], payload['message_id']))


@APP.route('/messages/edit', methods=['PUT'])
def http_messages_edit():
    '''
    Wrapper function for messages_edit (edits a message)
    PUT: JSON containing "token" (str), "message_id" (int), "message" (str)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(message_edit(payload['token'], payload['message_id'], payload['message']))


###############
## HTTP user ##
###############
@APP.route('/user/profile', methods=['GET'])
def http_user_profile():
    '''
    Wrapper function for user_profile (returns details about a user)
    GET: JSON containing "token" (str), "u_id" (int)
    Returns JSON containing "user" (dict)
    '''
    return dumps(user_profile(request.args.get('token', type=str),
                              request.args.get('u_id', type=int)))


@APP.route('/user/profile/setname', methods=['PUT'])
def http_user_profile_setname():
    '''
    Wrapper function for user_profile_setname (updates user's first and last name)
    PUT: JSON containing "token" (str), "name_first" (str), "name_last" (str)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(user_profile_setname(payload['token'],
                                      payload['name_first'],
                                      payload['name_last']))


@APP.route('/user/profile/setemail', methods=['PUT'])
def http_user_profile_setemail():
    '''
    Wrapper function for user_profile_setemail (updates user's email)
    PUT: JSON containing "token" (str), "email" (str)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(user_profile_setemail(payload['token'], payload['email']))


@APP.route('/user/profile/sethandle', methods=['PUT'])
def http_user_profile_sethandle():
    '''
    Wrapper function for user_profile_sethandle (updates user's handle)
    PUT: JSON containing "token" (str), "handle_str" (str)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(user_profile_sethandle(payload['token'], payload['handle_str']))


################
## HTTP other ##
################
@APP.route('/users/all', methods=['GET'])
def http_users_all():
    '''
    Wrapper function for users_all (retrieves all users)
    GET: JSON containing "token" (str)
    Returns JSON containing 'users' (list of dicts)
    '''
    return dumps(users_all(request.args.get('token')))


@APP.route('/admin/userpermission/change', methods=['POST'])
def http_admin_userpermission_change():
    '''
    Wrapper function for admin_userpermission_change (changes user permission)
    POST: JSON containing "token" (str), "u_id" (int), "permission_id" (int)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(admin_userpermission_change(payload['token'],
                                             payload['u_id'],
                                             payload['permission_id']))


@APP.route('/search', methods=['GET'])
def http_search():
    '''
    Wrapper function for search (search for substring)
    GET: JSON containing "token" (str), "query_str" (str)
    Returns JSON containing "messages" (list of dicts)
    '''
    return dumps(search(request.args.get('token'), request.args.get('query_str')))


@APP.route('/clear', methods=['DELETE'])
def http_clear():
    '''
    Wrapper function for clear (clears all data)
    DELETE: No input
    Returns JSON containing empty dict
    '''
    return dumps(clear())


if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port