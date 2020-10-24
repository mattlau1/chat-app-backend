''' Import required modules '''
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json


# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture
def url():
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "src/server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

###############
## HTTP auth ##
###############
def test_http_auth_login(url):
    '''
    HTTP test for auth_login
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Invalid email format
    resp = requests.post(url + 'auth/login', json={
        'email': 's#3%9@m@l3.comm',
        'password': 'password',
    })
    assert resp.status_code == 400

    # Unregistered
    resp = requests.post(url + 'auth/login', json={
        'email': 'unregistered@gmail.com',
        'password': 'password',
    })
    assert resp.status_code == 400

    # Registered
    resp = requests.post(url + 'auth/register', json={
        'email': 'admin@gmail.com',
        'password': 'password',
        'name_first': 'Admin',
        'name_last': 'User',
    })
    assert resp.status_code == 200

    # Incorrect password
    resp = requests.post(url + 'auth/login', json={
        'email': 'admin@gmail.com',
        'password': 'PASSWORD',
    })
    assert resp.status_code == 400

    # Correct password
    resp = requests.post(url + 'auth/login', json={
        'email': 'admin@gmail.com',
        'password': 'password',
    })
    assert resp.status_code == 200
    payload = resp.json()
    token = payload['token']
    u_id = payload['u_id']

    # Successful login - valid token
    resp = requests.get(url + 'user/profile', params={
        'token': token,
        'u_id': u_id,
    })
    assert resp.status_code == 200
    payload = json.loads(resp.text)['user']
    assert payload['u_id'] == u_id
    assert payload['email'] == 'admin@gmail.com'
    assert payload['name_first'] == 'Admin'
    assert payload['name_last'] == 'User'


def test_http_auth_logout(url):
    '''
    HTTP test for auth_logout
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Invalid token
    resp = requests.post(url + 'auth/logout', json={
        'token': ''
    })
    assert resp.status_code == 400

    # Registered
    resp = requests.post(url + 'auth/register', json={
        'email': 'admin@gmail.com',
        'password': 'password',
        'name_first': 'Admin',
        'name_last': 'User',
    })
    assert resp.status_code == 200

    # Login
    resp = requests.post(url + 'auth/login', json={
        'email': 'admin@gmail.com',
        'password': 'password',
    })
    assert resp.status_code == 200
    payload = resp.json()
    token = payload['token']
    u_id = payload['u_id']

    # Logout
    resp = requests.post(url + 'auth/logout', json={
        'token': token,
    })
    assert resp.status_code == 200
    assert json.loads(resp.text)['is_success']

    # Successful logout - token invalidated
    resp = requests.get(url + 'user/profile', params={
        'token': token,
        'u_id': u_id,
    })
    assert resp.status_code == 400


def test_http_auth_register(url):
    '''
    HTTP test for auth_register
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Invalid email format
    resp = requests.post(url + 'auth/register', json={
        'email': 's#3%9@m@l3.comm',
        'password': 'password',
        'name_first': 'Admin',
        'name_last': 'User',
    })
    assert resp.status_code == 400

    # Password less than 6 characters
    for multiple in range(6):
        resp = requests.post(url + 'auth/register', json={
            'email': 'admin@gmail.com',
            'password': 'a' * multiple,
            'name_first': 'Admin',
            'name_last': 'User',
        })
        assert resp.status_code == 400

    # Length of name not 1-50 characters inclusive
    # name_first
    resp = requests.post(url + 'auth/register', json={
        'email': 'admin@gmail.com',
        'password': 'password',
        'name_first': '',
        'name_last': 'User',
    })
    assert resp.status_code == 400

    resp = requests.post(url + 'auth/register', json={
        'email': 'admin@gmail.com',
        'password': 'password',
        'name_first': 'A' * 51,
        'name_last': 'User',
    })
    assert resp.status_code == 400

    # name_last
    resp = requests.post(url + 'auth/register', json={
        'email': 'admin@gmail.com',
        'password': 'password',
        'name_first': 'Admin',
        'name_last': '',
    })
    assert resp.status_code == 400

    resp = requests.post(url + 'auth/register', json={
        'email': 'admin@gmail.com',
        'password': 'password',
        'name_first': 'Admin',
        'name_last': 'A' * 51,
    })
    assert resp.status_code == 400

    # both names
    resp = requests.post(url + 'auth/register', json={
        'email': 'admin@gmail.com',
        'password': 'password',
        'name_first': '',
        'name_last': '',
    })
    assert resp.status_code == 400

    resp = requests.post(url + 'auth/register', json={
        'email': 'admin@gmail.com',
        'password': 'password',
        'name_first': 'A' * 51,
        'name_last': 'A' * 51,
    })
    assert resp.status_code == 400

    # Registered
    resp = requests.post(url + 'auth/register', json={
        'email': 'admin@gmail.com',
        'password': 'password',
        'name_first': 'Admin',
        'name_last': 'User',
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'auth/register', json={
        'email': 'short@gmail.com',
        'password': 'password',
        'name_first': 'A',
        'name_last': 'U',
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'auth/register', json={
        'email': 'long@gmail.com',
        'password': 'password',
        'name_first': 'A' * 50,
        'name_last': 'U' * 50,
    })
    assert resp.status_code == 200

    # Email in use
    resp = requests.post(url + 'auth/register', json={
        'email': 'admin@gmail.com',
        'password': 'password',
        'name_first': 'Bob',
        'name_last': 'Chen',
    })
    assert resp.status_code == 400

    # Registered users can login now
    resp = requests.post(url + 'auth/login', json={
        'email': 'admin@gmail.com',
        'password': 'password',
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'auth/login', json={
        'email': 'short@gmail.com',
        'password': 'password',
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'auth/login', json={
        'email': 'long@gmail.com',
        'password': 'password',
    })
    assert resp.status_code == 200


##################
## HTTP channel ##
##################
def test_http_channel_invite(url):
    '''
    HTTP test for channel_invite
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_channel_details(url):
    '''
    HTTP test for channel_details
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_channel_messages(url):
    '''
    HTTP test for channel_messages
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_channel_leave(url):
    '''
    HTTP test for channel_leave
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_channel_join(url):
    '''
    HTTP test for channel_join
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_channel_addowner(url):
    '''
    HTTP test for channel_addowner
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_channel_removeowner(url):
    '''
    HTTP test for channel_removeowner
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


###################
## HTTP channels ##
###################
def test_http_channels_list(url):
    '''
    HTTP test for channels_list
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_channels_listall(url):
    '''
    HTTP test for channels_listall
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_channels_create(url):
    '''
    HTTP test for channels_create
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


##################
## HTTP message ##
##################
def test_http_message_send(url):
    '''
    HTTP test for message_send
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_message_remove(url):
    '''
    HTTP test for message_remove
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_message_edit(url):
    '''
    HTTP test for message_edit
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


###############
## HTTP user ##
###############
def test_http_user_profile(url):
    '''
    HTTP test for user_profile
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_user_profile_setname(url):
    '''
    HTTP test for user_profile_setname
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_user_profile_setemail(url):
    '''
    HTTP test for user_profile_setemail
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_user_profile_sethandle(url):
    '''
    HTTP test for user_profile_sethandle
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


################
## HTTP other ##
################
def test_http_users_all(url):
    '''
    HTTP test for users_all
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_admin_userpermission_change(url):
    '''
    HTTP test for admin_userpermission_change
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_search(url):
    '''
    HTTP test for search
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass


def test_http_clear(url):
    '''
    HTTP test for clear
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass
