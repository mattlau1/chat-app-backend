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

def test_http_message_edit(url):
    '''
    HTTP test for message_edit
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

    # Register user 1
    resp = requests.post(url + 'auth/register', json={
        'email': 'victorzhang@gmail.com',
        'password': 'password',
        'name_first': 'Victor',
        'name_last': 'Zhang',
    })
    assert resp.status_code == 200
    user1 = resp.json()

    # Register user 2
    resp = requests.post(url + 'auth/register', json={
        'email': 'jesschen@gmail.com',
        'password': 'password',
        'name_first': 'Jess',
        'name_last': 'Chen',
    })
    assert resp.status_code == 200
    user2 = resp.json()

    # Set up channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Test Channel',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # Invite user 1
    resp = requests.post(url + 'channel/invite', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'u_id': user1['u_id'],
    })
    assert resp.status_code == 200

    # Invite user 2
    resp = requests.post(url + 'channel/invite', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'u_id': user2['u_id'],
    })
    assert resp.status_code == 200

    # Owner sends message 1
    resp = requests.post(url + 'message/send', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': 'First message',
    })
    assert resp.status_code == 200
    m_id1 = resp.json()['message_id']

    # User 1 sends message 2
    resp = requests.post(url + 'message/send', json={
        'token': user1['token'],
        'channel_id': channel_id,
        'message': 'Second message',
    })
    assert resp.status_code == 200
    m_id2 = resp.json()['message_id']

    # User 2 sends message 3
    resp = requests.post(url + 'message/send', json={
        'token': user2['token'],
        'channel_id': channel_id,
        'message': 'Third message',
    })
    assert resp.status_code == 200
    m_id3 = resp.json()['message_id']

    # Invalid token
    resp = requests.put(url + 'message/edit', json={
        'token': '',
        'message_id': m_id1,
        'message': 'Edited first message',
    })
    assert resp.status_code == 400

    # Invalid message_id
    resp = requests.put(url + 'message/edit', json={
        'token': owner['token'],
        'message_id': '',
        'message': 'Edited second message',
    })
    assert resp.status_code == 400

    # Authorised user did not send the message and is not channel or Flockr owner
    resp = requests.put(url + 'message/edit', json={
        'token': user1['token'],
        'message_id': m_id1,
        'message': 'Edited first message',
    })
    assert resp.status_code == 400

    resp = requests.put(url + 'message/edit', json={
        'token': user2['token'],
        'message_id': m_id2,
        'message': 'Edited second message',
    })
    assert resp.status_code == 400

    # Message sender can successfully edit their own message
    resp = requests.put(url + 'message/edit', json={
        'token': user2['token'],
        'message_id': m_id3,
        'message': 'Edited third message',
    })
    assert resp.status_code == 200

    # Owner can successfully edit anyone's message
    resp = requests.put(url + 'message/edit', json={
        'token': owner['token'],
        'message_id': m_id2,
        'message': 'Edited second message',
    })
    assert resp.status_code == 200

    # Owner can successfully edit their own message
    resp = requests.put(url + 'message/edit', json={
        'token': owner['token'],
        'message_id': m_id1,
        'message': 'Edited first message',
    })
    assert resp.status_code == 200

    # If the edited message becomes an empty string, it should be deleted
    resp = requests.post(url + 'message/send', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': 'Fourth message',
    })
    assert resp.status_code == 200
    m_id4 = resp.json()['message_id']

    resp = requests.post(url + 'message/send', json={
        'token': user1['token'],
        'channel_id': channel_id,
        'message': 'Fifth message',
    })
    assert resp.status_code == 200
    m_id5 = resp.json()['message_id']

    resp = requests.post(url + 'message/send', json={
        'token': user2['token'],
        'channel_id': channel_id,
        'message': 'Sixth message',
    })
    assert resp.status_code == 200
    m_id6 = resp.json()['message_id']

    # Check that there are 6 messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 6

    # Authorised user did not send the message is not channel or Flockr owner
    resp = requests.put(url + 'message/edit', json={
        'token': user1['token'],
        'message_id': m_id4,
        'message': '',
    })
    assert resp.status_code == 400

    resp = requests.put(url + 'message/edit', json={
        'token': user2['token'],
        'message_id': m_id5,
        'message': '',
    })
    assert resp.status_code == 400

    # Message sender can successfully delete their own message by editing it to an empty message
    resp = requests.put(url + 'message/edit', json={
        'token': user2['token'],
        'message_id': m_id6,
        'message': '',
    })
    assert resp.status_code == 200

    # Owner can successfully delete anyone's message by editing it to an empty message
    resp = requests.put(url + 'message/edit', json={
        'token': owner['token'],
        'message_id': m_id5,
        'message': '',
    })
    assert resp.status_code == 200

    # Owner can successfully delete their own message by editing it to an empty message
    resp = requests.put(url + 'message/edit', json={
        'token': owner['token'],
        'message_id': m_id4,
        'message': '',
    })
    assert resp.status_code == 200

    # Check that there are 3 messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 3
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


