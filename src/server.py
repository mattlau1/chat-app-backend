''' Import required modules '''
import sys
from json import dumps
from flask import Flask, request, send_from_directory
from flask_cors import CORS
from flask_mail import Mail, Message
from error import InputError
from auth import auth_login, auth_logout, auth_register, generate_reset_code, password_reset
from channel import (channel_invite, channel_details, channel_messages, channel_leave,
                     channel_join, channel_addowner, channel_removeowner)
from channels import channels_list, channels_listall, channels_create
from message import (message_send, message_remove, message_edit, message_sendlater,
                     message_react, message_unreact, message_pin, message_unpin)
from user import (user_profile, user_profile_setname, user_profile_setemail,
                  user_profile_sethandle, user_profile_uploadphoto)
from other import users_all, admin_userpermission_change, search, clear
from standup import standup_start, standup_active, standup_send

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

APP = Flask(__name__, static_folder='../static/')
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Configure email server
APP.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='comp1531flockr@gmail.com',
    MAIL_PASSWORD='HelloWorld'
)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
        raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route('/static/<path:path>')
def serve(path):
    '''
    Serves a given static file
    '''
    return send_from_directory('', path)


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


@APP.route('/auth/passwordreset/request', methods=['POST'])
def http_auth_passwordreset_request():
    # Retrieve data
    payload = request.get_json()
    email = payload['email']
    # Generate reset code
    reset_code = generate_reset_code(email)
    # Create email message
    message = Message("Flockr Password Reset Request",
                      sender='comp1531flockr@gmail.com',
                      recipients=[email])
    message.html = f'''
    <p>Your reset code is: <b>{reset_code}</b></p>
    <p>Please enter this code when prompted.</p>
    <p>If you were not expecting this email, please ignore it.</p>
    '''
    # Send email
    mail = Mail(app=APP)
    mail.send(message)
    return dumps({})


@APP.route('/auth/passwordreset/reset', methods=['POST'])
def http_auth_passwordreset_reset():
    # Retrieve data
    payload = request.get_json()
    return dumps(password_reset(payload['reset_code'], payload['new_password']))


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
@APP.route('/message/send', methods=['POST'])
def http_message_send():
    '''
    Wrapper function for message_send (sends a message to channel)
    POST: JSON containing "token" (str), "channel_id" (int), "message" (str)
    Returns JSON containing "message_id" (int)
    '''
    payload = request.get_json()
    return dumps(message_send(payload['token'], payload['channel_id'], payload['message']))


@APP.route('/message/remove', methods=['DELETE'])
def http_message_remove():
    '''
    Wrapper function for message_remove (removes a message)
    DELETE: JSON containing "token" (str), "message_id" (int)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(message_remove(payload['token'], payload['message_id']))


@APP.route('/message/edit', methods=['PUT'])
def http_message_edit():
    '''
    Wrapper function for message_edit (edits a message)
    PUT: JSON containing "token" (str), "message_id" (int), "message" (str)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(message_edit(payload['token'], payload['message_id'], payload['message']))


@APP.route('/message/sendlater', methods=['POST'])
def http_message_sendlater():
    '''
    Wrapper function for message_sendlater (sends a message at a later date)
    POST: JSON containing "token" (str), "channel_id" (int),
          "message" (str), "time_sent" (UNIX timestamp - float)
    Returns JSON containing "message_id" (int)
    '''
    payload = request.get_json()
    return dumps(message_sendlater(payload['token'], payload['channel_id'],
                                   payload['message'], payload['time_sent']))


@APP.route('/message/react', methods=['POST'])
def http_message_react():
    '''
    Wrapper function for message_react (reacts to a given message)
    POST: JSON containing "token" (str), "message_id" (int), "react_id" (int)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(message_react(payload['token'], payload['message_id'], payload['react_id']))


@APP.route('/message/unreact', methods=['POST'])
def http_message_unreact():
    '''
    Wrapper function for message_unreact (unreacts to a given message)
    POST: JSON containing "token" (str), "message_id" (int), "react_id" (int)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(message_unreact(payload['token'], payload['message_id'], payload['react_id']))


@APP.route('/message/pin', methods=['POST'])
def http_message_pin():
    '''
    Wrapper function for message_pin (pins given message)
    POST: JSON containing "token" (str), "message_id" (int)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(message_pin(payload['token'], payload['message_id']))


@APP.route('/message/unpin', methods=['POST'])
def http_message_unpin():
    '''
    Wrapper function for message_unpin (unpins given message)
    POST: JSON containing "token" (str), "message_id" (int)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(message_unpin(payload['token'], payload['message_id']))


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


@APP.route('/user/profile/uploadphoto', methods=['POST'])
def http_user_profile_uploadphoto():
    '''
    Wrapper function for user_profile_uploadphoto (uploads a profile pic for a user)
    POST: JSON containing "token" (str), "img_url" (str), "x_start" (int),
          "y_start" (int), "x_end" (int), "y_end" (int)
    Returns JSON containing empty dict
    '''
    url_root = request.url_root
    payload = request.get_json()
    return dumps(user_profile_uploadphoto(payload['token'], url_root, payload['img_url'],
                                          payload['x_start'], payload['y_start'],
                                          payload['x_end'], payload['y_end']))


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


##################
## HTTP standup ##
##################
@APP.route('/standup/start', methods=['POST'])
def http_standup_start():
    '''
    Wrapper for standup_start (starts a standup)
    POST: JSON containing "token" (str), "channel_id" (int), "length" (int)
    Returns JSON containing "time_finish" (UNIX timestamp float)
    '''
    payload = request.get_json()
    return dumps(standup_start(payload['token'], payload['channel_id'], payload['length']))


@APP.route('/standup/active', methods=['GET'])
def http_standup_active():
    '''
    Wrapper for standup_active (returns information about standup status)
    POST: JSON containing "token" (str), "channel_id" (int)
    Returns JSON containing "is_active" (bool), "time_finish" (UNIX timestamp float)
    '''
    return dumps(standup_active(request.args.get('token', type=str),
                                request.args.get('channel_id', type=int)))


@APP.route('/standup/send', methods=['POST'])
def http_standup_send():
    '''
    Wrapper for standup_send (adds a message to the standup message queue)
    POST: JSON containing "token" (str), "channel_id" (int), "message" (str)
    Returns JSON containing empty dict
    '''
    payload = request.get_json()
    return dumps(standup_send(payload['token'], payload['channel_id'], payload['message']))


if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
