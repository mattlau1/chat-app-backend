''' Import required modules '''
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from echo_http_test import url

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

    # Invalid message_id
    resp = requests.delete(url + 'message/remove', json={
        'token': owner['token'],
        'message_id': m_id1 + 1,
    })
    assert resp.status_code == 400

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
    resp = requests.delete(url + 'message/remove', json={
        'token': '',
        'message_id': m_id1,
    })
    assert resp.status_code == 400

    # Authorised user did not send the message and is not channel or Flockr owner
    resp = requests.delete(url + 'message/remove', json={
        'token': user1['token'],
        'message_id': m_id1,
    })
    assert resp.status_code == 400

    resp = requests.delete(url + 'message/remove', json={
        'token': user2['token'],
        'message_id': m_id2,
    })
    assert resp.status_code == 400

    # Check that there are 3 messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 3

    # Message sender can successfully remove their own message
    resp = requests.delete(url + 'message/remove', json={
        'token': user2['token'],
        'message_id': m_id3,
    })
    assert resp.status_code == 200

    # Check that there are 2 messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 2

    # Owner can successfully remove anyone's message
    resp = requests.delete(url + 'message/remove', json={
        'token': owner['token'],
        'message_id': m_id2,
    })
    assert resp.status_code == 200

    # Check that there is 1 message
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 1

    # Owner can successfully remove their own message
    resp = requests.delete(url + 'message/remove', json={
        'token': owner['token'],
        'message_id': m_id1,
    })
    assert resp.status_code == 200

    # Check that there are 0 messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 0


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

    # Invalid message_id
    resp = requests.put(url + 'message/edit', json={
        'token': owner['token'],
        'message_id': m_id1 + 1,
        'message': 'Edited second message',
    })
    assert resp.status_code == 400

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

def test_http_message_sendlater(url):
    '''
    HTTP test for message_sendlater
    '''
    assert requests.delete(url + 'clear').status_code == 200

def test_http_message_react(url):
    '''
    HTTP test for message_react
    '''
    assert requests.delete(url + 'clear').status_code == 200

def test_http_message_unreact(url):
    '''
    HTTP test for message_unreact
    '''
    assert requests.delete(url + 'clear').status_code == 200

def test_http_message_pin(url):
    '''
    HTTP test for message_pin
    '''
    assert requests.delete(url + 'clear').status_code == 200

def test_http_message_unpin(url):
    '''
    HTTP test for message_unpin
    '''
    assert requests.delete(url + 'clear').status_code == 200

