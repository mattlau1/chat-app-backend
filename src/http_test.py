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
    
    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'owner@gmail.com',
        'password': 'password',
        'name_first': 'John',
        'name_last': 'Smith',
    })
    assert resp.status_code == 200
    owner = resp.json()

    # Register user
    resp = requests.post(url + 'auth/register', json={
        'email': 'user@gmail.com',
        'password': 'password',
        'name_first': 'Steve',
        'name_last': 'Jackson',
    })
    assert resp.status_code == 200
    user = resp.json()

    # Set up channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Test Channel',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # channel_id does not refer to a valid channel
    resp = requests.post(url + 'channel/invite', json ={
        'token': owner['token'],
        'channel_id': channel_id + 100,
        'u_id': user['u_id'],
    })
    assert resp.status_code == 400

    # u_id does not refer to a valid channel
    resp = requests.post(url + 'channel/invite', json ={
        'token': owner['token'],
        'channel_id': channel_id,
        'u_id': user['u_id'] + 100,
    })
    assert resp.status_code == 400

    # Authorised user not in channel
    resp = requests.post(url + 'channel/invite', json ={
        'token': user['token'],
        'channel_id': channel_id,
        'u_id': user['u_id'],
    })
    assert resp.status_code == 400

    # Invite the user successfully
    resp = requests.post(url + 'channel/invite', json ={
        'token': owner['token'],
        'channel_id': channel_id,
        'u_id': user['u_id'],
    })
    assert resp.status_code == 200


def test_http_channel_details(url):
    '''
    HTTP test for channel_details
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'liambrown@gmail.com',
        'password': 'password',
        'name_first': 'Liam',
        'name_last': 'Brown',
    })
    assert resp.status_code == 200
    owner = resp.json()

    # Register user
    resp = requests.post(url + 'auth/register', json={
        'email': 'victorzhang@gmail.com',
        'password': 'password',
        'name_first': 'Victor',
        'name_last': 'Zhang',
    })
    assert resp.status_code == 200
    user = resp.json()

    # Set up channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Test Channel',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # channel_id does not refer to a valid channel
    resp = requests.post(url + 'channel/details', json ={
        'token': owner['token'],
        'channel_id': channel_id + 100,
    })
    assert resp.status_code == 400    

    # Authorised user not in channel
    resp = requests.post(url + 'channel/details', json ={
        'token': user['token'],
        'channel_id': channel_id,
    })
    assert resp.status_code == 400
    
    # Invite the user successfully
    resp = requests.post(url + 'channel/invite', json ={
        'token': owner['token'],
        'channel_id': channel_id,
        'u_id': user['u_id'],
    })
    assert resp.status_code == 200

    # User can now view the channel details
    resp = requests.post(url + 'channel/details', json ={
        'token': user['token'],
        'channel_id': channel_id,
    })
    assert resp.status_code == 200

    payload = resp.json()
    assert payload == {
        'name': 'Test Channel',
        'owner_members': [
            {
                'u_id': owner['u_id'],
                'name_first': 'Liam',
                'name_last': 'Brown',
            }
        ],
        'all_members': [
            {
                'u_id': owner['u_id'],
                'name_first': 'Liam',
                'name_last': 'Brown',
            },
            {
                'u_id': user['u_id'],
                'name_first': 'Victor',
                'name_last': 'Zhang',
            }
        ],
    }


def test_http_channel_messages(url):
    '''
    HTTP test for channel_messages
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Register users
    resp = requests.post(url + 'auth/register', json={
        'email': 'admin@gmail.com',
        'password': 'password',
        'name_first': 'Admin',
        'name_last': 'User',
    })
    assert resp.status_code == 200
    admin_user = resp.json()

    resp = requests.post(url + 'auth/register', json={
        'email': 'random@gmail.com',
        'password': 'password',
        'name_first': 'Random',
        'name_last': 'User',
    })
    assert resp.status_code == 200
    random_user = resp.json()

    # Set up channel
    resp = requests.post(url + 'channels/create', json={
        'token': admin_user['token'],
        'name': 'Admin Channel',
        'is_public': True,
    })
    assert resp.status_code == 200
    admin_channel_id = resp.json()['channel_id']

    # Invalid token
    resp = requests.get(url + 'channel/messages', params={
        'token': '',
        'channel_id': admin_channel_id,
        'start': 0,
    })
    assert resp.status_code == 400

    # User not in channel
    resp = requests.get(url + 'channel/messages', params={
        'token': random_user['token'],
        'channel_id': admin_channel_id,
        'start': 0,
    })
    assert resp.status_code == 400

    # Invalid channel_id
    resp = requests.get(url + 'channel/messages', params={
        'token': admin_user['token'],
        'channel_id': admin_channel_id + 1,
        'start': 0,
    })
    assert resp.status_code == 400

    # Test start index - testing 50 messages
    for message_sent in range(1, 51):
        # Send message
        resp = requests.post(url + 'message/send', json={
            'token': admin_user['token'],
            'channel_id': admin_channel_id,
            'message': f'Message {message_sent}',
        })
        assert resp.status_code == 200
        # Invalid start index
        resp = requests.get(url + 'channel/messages', params={
            'token': admin_user['token'],
            'channel_id': admin_channel_id,
            'start': message_sent + 1,
        })
        assert resp.status_code == 400
        # Valid request from start index 0
        resp = requests.get(url + 'channel/messages', params={
            'token': admin_user['token'],
            'channel_id': admin_channel_id,
            'start': 0,
        })
        assert resp.status_code == 200
        payload = resp.json()
        assert len(payload['messages']) == message_sent
        assert payload['start'] == 0
        assert payload['end'] == -1
        # Valid request from previous message
        resp = requests.get(url + 'channel/messages', params={
            'token': admin_user['token'],
            'channel_id': admin_channel_id,
            'start': message_sent - 1,
        })
        assert resp.status_code == 200
        payload = resp.json()
        assert len(payload['messages']) == 1
        assert payload['start'] == message_sent - 1
        assert payload['end'] == -1
        # Valid request from current message
        resp = requests.get(url + 'channel/messages', params={
            'token': admin_user['token'],
            'channel_id': admin_channel_id,
            'start': message_sent,
        })
        assert resp.status_code == 200
        payload = resp.json()
        assert len(payload['messages']) == 0
        assert payload['start'] == message_sent
        assert payload['end'] == -1

    # Test message 51
    resp = requests.post(url + 'message/send', json={
        'token': admin_user['token'],
        'channel_id': admin_channel_id,
        'message': 'Message 51',
    })
    assert resp.status_code == 200

    resp = requests.get(url + 'channel/messages', params={
        'token': admin_user['token'],
        'channel_id': admin_channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 50
    assert payload['start'] == 0
    assert payload['end'] == 50

    resp = requests.get(url + 'channel/messages', params={
        'token': admin_user['token'],
        'channel_id': admin_channel_id,
        'start': 1,
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 50
    assert payload['start'] == 1
    assert payload['end'] == -1


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

    # Register user
    resp = requests.post(url + 'auth/register', json={
        'email': 'admin@gmail.com',
        'password': 'password',
        'name_first': 'Admin',
        'name_last': 'User',
    })
    assert resp.status_code == 200
    payload = resp.json()
    admin_token = payload['token']

    # Set up channel
    resp = requests.post(url + 'channels/create', json={
        'token': admin_token,
        'name': 'Admin Channel',
        'is_public': True,
    })
    assert resp.status_code == 200
    admin_channel_id = resp.json()['channel_id']

    # Invalid token
    resp = requests.post(url + 'message/send', json={
        'token': '',
        'channel_id': admin_channel_id,
        'message': 'test',
    })
    assert resp.status_code == 400

    # User not in channel tries to send message
    resp = requests.post(url + 'auth/register', json={
        'email': 'random@gmail.com',
        'password': 'password',
        'name_first': 'Random',
        'name_last': 'User',
    })
    assert resp.status_code == 200
    payload = resp.json()
    random_token = payload['token']

    resp = requests.post(url + 'message/send', json={
        'token': random_token,
        'channel_id': admin_channel_id,
        'message': 'test',
    })
    assert resp.status_code == 400

    # Admin sends message
    resp = requests.post(url + 'message/send', json={
        'token': admin_token,
        'channel_id': admin_channel_id,
        'message': 'First message',
    })
    assert resp.status_code == 200

    # Random user sends message after joining
    resp = requests.post(url + 'channel/join', json={
        'token': random_token,
        'channel_id': admin_channel_id,
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'message/send', json={
        'token': random_token,
        'channel_id': admin_channel_id,
        'message': 'Second message',
    })
    assert resp.status_code == 200

    # Empty messages
    resp = requests.post(url + 'message/send', json={
        'token': random_token,
        'channel_id': admin_channel_id,
        'message': '',
    })
    assert resp.status_code == 400

    # Long messages
    resp = requests.post(url + 'message/send', json={
        'token': random_token,
        'channel_id': admin_channel_id,
        'message': 'A' * 1000,
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'message/send', json={
        'token': random_token,
        'channel_id': admin_channel_id,
        'message': 'A' * 1001,
    })
    assert resp.status_code == 400

    # Check messages have been sent
    resp = requests.get(url + 'channel/messages', params={
        'token': admin_token,
        'channel_id': admin_channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 3


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

    # registering valid user
    resp = requests.post(url + 'auth/register', json={
        'email': 'stvnnguyen69@hotmail.com',
        'password': 'password',
        'name_first': 'Steven',
        'name_last': 'Nguyen',
    })
    assert resp.status_code == 200
    user = resp.json()

    resp = requests.put(url+"user/profile/sethandle", params={
        'token': user['token'],
        'handle_str': 'Stevenson'
    })
    assert resp.status_code == 200

    resp = requests.get(url+"user/profile", params={
        'token': user['token'],
        'u_id': user['u_id']
    })

    assert resp.status_code == 200
    profile = resp.json()

    assert profile['user']['name_first'] == "Steven"
    assert profile['user']['name_last'] == "Nguyen"
    assert profile['user']['u_id'] == user['u_id']
    assert profile['user']['email'] == 'stvnnguyen69@hotmail.com'
    assert profile['user']['handle_str'] == 'Stevenson'

    # access user details without registering
    resp = requests.get(url+"user/profile", params={
        'tokens': "&73hf(s!)@",
        'u_id': 42
    })

    assert resp.status_code == 400

    # retrieving information with correct token but wrong id
    resp = requests.post(url + 'auth/register', json={
        'email': 'andrewwashere@outlook.com',
        'password': '0987654321',
        'name_first': 'Andrew',
        'name_last': 'Andrewson',
    })
    user = resp.json()
    resp = requests.get(url+"user/profile", params = {
        'token': user['token'],
        'u_id': 34
    })
    assert resp.status_code == 400

def test_http_user_profile_setname(url):
    '''
    HTTP test for user_profile_setname
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # create user
    resp = requests.post(url + 'auth/register', json={
        'email': 'mmmonkey97@hotmail.com',
        'password': 'banana',
        'name_first': 'John',
        'name_last': 'Johnson',
    })
    user = resp.json()
    resp = requests.get(url+"user/profile", params={
        'token': user['token'],
        'u_id': user['u_id']
    })

    assert resp.status_code == 200
    profile = resp.json()

    # check original name
    assert profile['user']['name_first'] == "John"
    assert profile['user']['name_last'] == "Johnson"
    assert profile['user']['u_id'] == user['u_id']

    # change setname
    requests.put(url+'user/profile/setname', params={
        'token': user['token'],
        'name_first': 'Monkey',
        'name_last': 'Monkeyson'
    })

    resp = requests.get(url+"user/profile", params={
        'token': user['token'],
        'u_id': user['u_id']
    })

    assert resp.status_code == 200
    profile = resp.json()

    # check new set name
    assert profile['user']['name_first'] == "Monkey"
    assert profile['user']['name_last'] == "Monkeyson"
    assert profile['user']['u_id'] == user['u_id']

    # change name again with 1 character
    requests.put(url+'user/profile/setname', params={
        'token': user['token'],
        'name_first': 'A',
        'name_last': 'B'
    })

    resp = requests.get(url+"user/profile", params={
        'token': user['token'],
        'u_id': user['u_id']
    })

    assert resp.status_code == 200
    profile = resp.json()

    # check new set name
    assert profile['user']['name_first'] == "A"
    assert profile['user']['name_last'] == "B"
    assert profile['user']['u_id'] == user['u_id']

    # change name again with exactly 50 characters
    long_first = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    long_last = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'
    resp = requests.get(url+"user/profile", params={
        'token': user['token'],
        'u_id': user['u_id']
    })

    assert resp.status_code == 200
    profile = resp.json()

    assert profile['user']['name_first'] == long_first
    assert profile['user']['name_last'] == long_last
    assert profile['user']['u_id'] == user['u_id']

    # change into empty name
    resp = requests.put(url+'user/profile/setname', params={
        'token': user['token'],
        'name_first': '',
        'name_last': ''
    })
    assert resp.status_code == 400

    # change into 51 characters
    long_first = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxa'
    long_last = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyb'
    resp = requests.put(url+'user/profile/setname', params={
        'token': user['token'],
        'name_first': long_first,
        'name_last': long_last
    })
    assert resp.status_code == 400

def test_http_user_profile_setemail(url):
    '''
    HTTP test for user_profile_setemail
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # SET VALID EMAIL

    # registering valid user
    resp = requests.post(url + 'auth/register', json={
        'email': 'stvnnguyen69@hotmail.com',
        'password': 'password',
        'name_first': 'Steven',
        'name_last': 'Nguyen',
    })
    assert resp.status_code == 200
    user = resp.json()

    # get user profile
    resp = requests.get(url+"user/profile", params={
        'token': user['token'],
        'u_id': user['u_id']
    })
    assert resp.status_code == 200
    profile = resp.json()

    # check original email
    assert profile['user']['email'] == 'stvnnguyen69@hotmail.com'

    # set new email
    requests.put(url+"user/profile/setemail", params={
        'token': user['token'],
        'email': 'stevennguyen22@gmail.com'
    })

    # get user profile
    resp = requests.get(url+"user/profile", params={
        'token': user['token'],
        'u_id': user['u_id']
    })
    assert resp.status_code == 200
    profile = resp.json()

    # check if email has changed
    assert profile['user']['email'] == 'stevennguyen22@gmail.com'

    # SETTING INVALID EMAIL

    # register valid user
    resp = requests.post(url + 'auth/register', json={
        'email': 'andrewwashere@outlook.com',
        'password': '0987654321',
        'name_first': 'Andrew',
        'name_last': 'Andrewson',
    })
    assert resp.status_code == 200
    user = resp.json()

    # set invalid email
    resp = requests.put(url+"user/profile/setemail", params={
        'token': user['token'],
        'email': 'steve.apple@'
    })

    assert resp.status_code == 400

    # EMAIL ADDRESS TAKEN

    # register two valid users
    resp = requests.post(url + 'auth/register', json={
        'email': 'mmmonkey97@hotmail.com',
        'password': 'banana',
        'name_first': 'John',
        'name_last': 'Johnson',
    })
    assert resp.status_code == 200
    user1 = resp.json()

    resp = requests.post(url + 'auth/register', json={
        'email': 'zippy@hotmail.com',
        'password': 'carrot',
        'name_first': 'Carrot',
        'name_last': 'Carrotson',
    })
    assert resp.status_code == 200
    user2 = resp.json()

    # set valid email for user1
    resp = requests.put(url+"user/profile/setemail", params={
        'token': user1['token'],
        'email': 'monkey@gmail.com'
    })
    assert resp.status_code == 200

    # set user2's email to user1's email (should be taken)
    resp = requests.put(url+"user/profile/setemail", params={
        'token': user2['token'],
        'email': 'monkey@gmail.com'
    })
    assert resp.status_code == 400

    # get user1's profile
    resp = requests.get(url+"user/profile", params={
        'token': user1['token'],
        'u_id': user1['u_id']
    })
    assert resp.status_code == 200
    profile1 = resp.json()

    # get user2's profile
    resp = requests.get(url+"user/profile", params={
        'token': user2['token'],
        'u_id': user2['u_id']
    })
    assert resp.status_code == 200
    profile2 = resp.json()

    # make sure user1's email has changed
    assert profile1['user']['email'] == 'monkey@gmail.com'

    # make sure user2's email is unchanged
    assert profile2['user']['email'] == 'zippy@hotmail.com'

def test_http_user_profile_sethandle(url):
    '''
    HTTP test for user_profile_sethandle
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # SET VALID HANDLE

    # registering valid user
    resp = requests.post(url + 'auth/register', json={
        'email': 'stvnnguyen69@hotmail.com',
        'password': 'password',
        'name_first': 'Steven',
        'name_last': 'Nguyen',
    })
    assert resp.status_code == 200
    user = resp.json()

    # set new handle
    resp = requests.put(url+"user/profile/sethandle", params={
        'token': user['token'],
        'handle_str': 'Stevenson'
    })
    assert resp.status_code == 200

    # get user profile
    resp = requests.get(url+"user/profile", params={
        'token': user['token'],
        'u_id': user['u_id']
    })
    assert resp.status_code == 200
    profile = resp.json()

    # check new handle
    assert profile['user']['handle_str'] == 'Stevenson'

    # SET INVALID HANDLE LENGTH

    # register valid user
    resp = requests.post(url + 'auth/register', json={
        'email': 'andrewwashere@outlook.com',
        'password': '0987654321',
        'name_first': 'Andrew',
        'name_last': 'Andrewson',
    })
    assert resp.status_code == 200
    user = resp.json()

    # set invalid short handle
    resp = requests.put(url+"user/profile/sethandle", params={
        'token': user['token'],
        'handle_str': 'AA'
    })
    assert resp.status_code == 400

    # set invalid long handle
    resp = requests.put(url+"user/profile/sethandle", params={
        'token': user['token'],
        'handle_str': 'thisistwentyonechars!'
    })
    assert resp.status_code == 400

    # HANDLE TAKEN

    # register two valid users
    resp = requests.post(url + 'auth/register', json={
        'email': 'mmmonkey97@hotmail.com',
        'password': 'banana',
        'name_first': 'John',
        'name_last': 'Johnson',
    })
    assert resp.status_code == 200
    user1 = resp.json()

    resp = requests.post(url + 'auth/register', json={
        'email': 'zippy@hotmail.com',
        'password': 'carrot',
        'name_first': 'Carrot',
        'name_last': 'Carrotson',
    })
    assert resp.status_code == 200
    user2 = resp.json()

    # user1 changes handle
    resp = requests.put(url+"user/profile/sethandle", params={
        'token': user1['token'],
        'handle_str': 'Banana'
    })
    assert resp.status_code == 200

    # user2 also changes handle
    resp = requests.put(url+"user/profile/sethandle", params={
        'token': user1['token'],
        'handle_str': 'Apple'
    })
    assert resp.status_code == 200

    # user2 tries to take user1's handle (should be taken)
    resp = requests.put(url+"user/profile/sethandle", params={
        'token': user2['token'],
        'handle_str': 'Banana'
    })
    assert resp.status_code == 400

    # get user1's profile
    resp = requests.get(url+"user/profile", params={
        'token': user1['token'],
        'u_id': user1['u_id']
    })
    assert resp.status_code == 200
    profile1 = resp.json()

    # get user2's profile
    resp = requests.get(url+"user/profile", params={
        'token': user2['token'],
        'u_id': user2['u_id']
    })
    assert resp.status_code == 200
    profile2 = resp.json()

    # make sure user1's handle has changed
    assert profile1['user']['handle_str'] == 'Banana'

    # make sure user2's handle isn't the same as user1's
    assert profile2['user']['handle_str'] == 'Apple'

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
    
    # Register user
    resp = requests.post(url + 'auth/register', json={
        'email': 'admin@gmail.com',
        'password': 'password',
        'name_first': 'Admin',
        'name_last': 'User',
    })
    assert resp.status_code == 200
    payload = resp.json()
    admin_token = payload['token']

    resp = requests.post(url + 'auth/register', json={
        'email': 'random@gmail.com',
        'password': 'password',
        'name_first': 'Random',
        'name_last': 'User',
    })
    assert resp.status_code == 200
    payload = resp.json()
    random_token = payload['token']

    # Set up channel
    resp = requests.post(url + 'channels/create', json={
        'token': admin_token,
        'name': 'Admin Channel',
        'is_public': True,
    })
    assert resp.status_code == 200
    admin_channel_id = resp.json()['channel_id']

    resp = requests.post(url + 'channels/create', json={
        'token': random_token,
        'name': 'Secret Channel',
        'is_public': False,
    })
    assert resp.status_code == 200
    secret_channel_id = resp.json()['channel_id']

    # Random user sends 'Hello world' to Admin Channel after joining
    resp = requests.post(url + 'channel/join', json={
        'token': random_token,
        'channel_id': admin_channel_id,
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'message/send', json={
        'token': random_token,
        'channel_id': admin_channel_id,
        'message': 'Hello world',
    })
    assert resp.status_code == 200

    # Admin sends 'Hello' and 'hello' to Admin Channel
    resp = requests.post(url + 'message/send', json={
        'token': admin_token,
        'channel_id': admin_channel_id,
        'message': 'Hello',
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'message/send', json={
        'token': admin_token,
        'channel_id': admin_channel_id,
        'message': 'hello',
    })
    assert resp.status_code == 200

    # Random User sends 'Helloooo' to Admin and Secret channel
    resp = requests.post(url + 'message/send', json={
        'token': random_token,
        'channel_id': admin_channel_id,
        'message': 'Helloooo',
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'message/send', json={
        'token': random_token,
        'channel_id': secret_channel_id,
        'message': 'Helloooo',
    })
    assert resp.status_code == 200

    # Search for substring 'Hello'
    # From Admin User's perspective
    resp = requests.get(url + 'search', params={
        'token': admin_token,
        'query_str': 'Hello',
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 3

    # From Random User's perspective
    resp = requests.get(url + 'search', params={
        'token': random_token,
        'query_str': 'Hello',
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 4

    # Invalid token
    resp = requests.get(url + 'search', params={
        'token': '',
        'query_str': 'Hello',
    })
    assert resp.status_code == 400

    # Search for substring 'asdf'
    # From Admin User's perspective
    resp = requests.get(url + 'search', params={
        'token': admin_token,
        'query_str': 'asdf',
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 0

    # From Random User's perspective
    resp = requests.get(url + 'search', params={
        'token': random_token,
        'query_str': 'asdf',
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 0


def test_http_clear(url):
    '''
    HTTP test for clear
    '''
    assert requests.delete(url + 'clear').status_code == 200
    pass
