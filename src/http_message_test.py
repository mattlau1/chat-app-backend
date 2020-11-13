''' Import required modules '''
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
from datetime import datetime
import json
import requests
import pytest
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


    # Test:
    #   - Check that it only sends a valid message after a certain period has elapsed
    #
    # Scenario:
    #   - The owner registers and creates the channel
    #   - Cannot message_sendlater() if the time is in the past
    #   - Check message_sendlater() only works if the token of the authorised user is
    #   valid and the person is in the channel
    #   - Check that the message being sent later is not empty and is less than 1000 characters


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

    # Time is in the past
    time_sent = datetime.timestamp(datetime.now()) - 2

    resp = requests.post(url + 'message/sendlater', json={
        'token': admin_token,
        'channel_id': admin_channel_id,
        'message': 'First message',
        'time_sent': time_sent,

    })
    assert resp.status_code == 400

    # Time is now valid
    time_sent = datetime.timestamp(datetime.now()) + 2

    # Invalid token
    resp = requests.post(url + 'message/sendlater', json={
        'token': '',
        'channel_id': admin_channel_id,
        'message': 'test',
        'time_sent': time_sent,
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

    resp = requests.post(url + 'message/sendlater', json={
        'token': random_token,
        'channel_id': admin_channel_id,
        'message': 'test',
        'time_sent': time_sent,
    })
    assert resp.status_code == 400

    # Admin sends message
    resp = requests.post(url + 'message/sendlater', json={
        'token': admin_token,
        'channel_id': admin_channel_id,
        'message': 'First message',
        'time_sent': time_sent,
    })
    assert resp.status_code == 200

    # Random user sends message after joining
    resp = requests.post(url + 'channel/join', json={
        'token': random_token,
        'channel_id': admin_channel_id,
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'message/sendlater', json={
        'token': random_token,
        'channel_id': admin_channel_id,
        'message': 'Second message',
        'time_sent': time_sent,
    })
    assert resp.status_code == 200

    # Empty messages
    resp = requests.post(url + 'message/sendlater', json={
        'token': random_token,
        'channel_id': admin_channel_id,
        'message': '',
        'time_sent': time_sent,
    })
    assert resp.status_code == 400

    # Long messages
    resp = requests.post(url + 'message/sendlater', json={
        'token': random_token,
        'channel_id': admin_channel_id,
        'message': 'A' * 1000,
        'time_sent': time_sent,
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'message/sendlater', json={
        'token': random_token,
        'channel_id': admin_channel_id,
        'message': 'A' * 1001,
        'time_sent': time_sent,
    })
    assert resp.status_code == 400

    # Check messages have not been sent immediately
    resp = requests.get(url + 'channel/messages', params={
        'token': admin_token,
        'channel_id': admin_channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 0

    # Check messages have been sent after time elapsed
    sleep(3)
    resp = requests.get(url + 'channel/messages', params={
        'token': admin_token,
        'channel_id': admin_channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 3


def test_http_message_react(url):
    '''
    HTTP test for message_react
    '''
    assert requests.delete(url + 'clear').status_code == 200


    # Test:
    #    - React to the message normally
    #    - User can see themselves if they have reacted or not
    #
    # Scenario:
    #    - The owner, user1 and user2 creates an account
    #    - The owner creates a channel, invites user1 and user2 and sends a message
    #    - user1 and user2 react to the message
    #    - test that the user1 and user2 has both reacted to the message from owner's
    #    point of view


    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'thisismymail69@gmail.com',
        'password': 'password',
        'name_first': 'Owner',
        'name_last': 'Ownerson',
    })
    assert resp.status_code == 200
    owner = resp.json()

    # Set up channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Main HUB',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # Register user 1
    resp = requests.post(url + 'auth/register', json={
        'email': 'useremail01@gmail.com',
        'password': 'password',
        'name_first': 'User',
        'name_last': 'Userson',
    })
    assert resp.status_code == 200
    user1 = resp.json()

    # Register user 2
    resp = requests.post(url + 'auth/register', json={
        'email': 'bigbadwolf97@gmail.com',
        'password': 'password',
        'name_first': 'Wolf',
        'name_last': 'Wolfson',
    })
    user2 = resp.json()

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

    # Owner sends a message
    resp = requests.post(url + 'message/send', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': 'I am good with alphebet',
    })
    assert resp.status_code == 200
    m_id1 = resp.json()['message_id']

    # User1 and user2 reacts to the message
    resp = requests.post(url + 'message/react', json={
        'token': user1['token'],
        'message_id': m_id1,
        'react_id': 1,
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'message/react', json={
        'token': user2['token'],
        'message_id': m_id1,
        'react_id': 1,
    })
    assert resp.status_code == 200

    # Get any information in regards to the message
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    messages = resp.json()['messages']

    # check that user1 and user2 reacted and owner sees that
    # owner itself didn't react
    for message in messages:
        if message['message_id'] == m_id1:
            assert message['reacts'][0]['react_id'] == 1
            assert message['reacts'][0]['u_ids'] == [user1['u_id'], user2['u_id']]
            assert message['reacts'][0]['is_this_user_reacted'] is False


    # Test:
    #    - React with invalid token
    #    - React with invalid message id
    #    - React with invalid react id
    #
    # Scenario:
    #    - Test invalid user reacts to the message
    #    - Test valid user reacts to invalid message
    #    - Test valid user reacts to the message with invalid react id


    # invalid user react
    resp = requests.post(url + 'message/react', json={
        'token': 'ASLDKJ',
        'message_id': m_id1,
        'react_id': 1,
    })
    assert resp.status_code == 400

    # valid user react to invalid message
    resp = requests.post(url + 'message/react', json={
        'token': owner['token'],
        'message_id': m_id1+666,
        'react_id': 1,
    })
    assert resp.status_code == 400

    # valid user react with invalid react id
    resp = requests.post(url + 'message/react', json={
        'token': owner['token'],
        'message_id': m_id1,
        'react_id': 666,
    })
    assert resp.status_code == 400

def test_http_message_unreact(url):
    '''
    HTTP test for message_unreact
    '''
    assert requests.delete(url + 'clear').status_code == 200


    # Test:
    #    - React to the message
    #    - Unreact to the message normally
    #
    # Scenario:
    #    - Owner, user1 and user2 create account
    #    - owner invites user1 and user2 and sends a message
    #    - Owner, user1 and user2 reacts to the message
    #    - Test that all 3 users reacted to the message


    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'ilovebanana69@gmail.com',
        'password': 'password',
        'name_first': 'Johnny',
        'name_last': 'Monkeyson',
    })
    assert resp.status_code == 200
    owner = resp.json()

    # Set up channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Main HUB',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # Register user 1
    resp = requests.post(url + 'auth/register', json={
        'email': 'hellokitty01@gmail.com',
        'password': 'password',
        'name_first': 'Hello',
        'name_last': 'Helloson',
    })
    assert resp.status_code == 200
    user1 = resp.json()

    # Register user 2
    resp = requests.post(url + 'auth/register', json={
        'email': 'snowsmasher666@gmail.com',
        'password': 'password',
        'name_first': 'Snow',
        'name_last': 'Snowson',
    })
    user2 = resp.json()

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

    # owner sends a message
    resp = requests.post(url + 'message/send', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': 'I am good with alphebet',
    })
    assert resp.status_code == 200
    m_id1 = resp.json()['message_id']

    # owner, user1 and user2 react to the message
    resp = requests.post(url + 'message/react', json={
        'token': owner['token'],
        'message_id': m_id1,
        'react_id': 1,
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'message/react', json={
        'token': user1['token'],
        'message_id': m_id1,
        'react_id': 1,
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'message/react', json={
        'token': user2['token'],
        'message_id': m_id1,
        'react_id': 1,
    })
    assert resp.status_code == 200

    # check that all 3 users has reacted to the message
    # Get any information in regards to the message
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    messages = resp.json()['messages']

    # check that user1 and user2 reacted and owner sees that
    id_list = [owner['u_id'], user1['u_id'], user2['u_id']]
    for message in messages:
        if message['message_id'] == m_id1:
            assert message['reacts'][0]['u_ids'] == id_list

    # user1 and user2 unreact
    resp = requests.post(url + 'message/unreact', json={
        'token': user1['token'],
        'message_id': m_id1,
        'react_id': 1,
    })
    assert resp.status_code == 200

    resp = requests.post(url + 'message/unreact', json={
        'token': user2['token'],
        'message_id': m_id1,
        'react_id': 1,
    })
    assert resp.status_code == 200

    # update information about message
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    messages = resp.json()['messages']

    # check that user1 and user2 has unreacted to the message
    # and it should be owner that has react
    for message in messages:
        if message['message_id'] == m_id1:
            assert message['reacts'][0]['u_ids'] == [owner['u_id']]


    # Test:
    #    - Unreact to the message with invalid token
    #    - Unreact to the message with invalid message id
    #    - Unreact to the message with invalid react id
    #
    # Scenario:
    #    - invalid user unreact to the message
    #    - valid user unreact to invalid message
    #    - valid user unreact to the message with invalid react id


    # invalid user unreact
    resp = requests.post(url + 'message/unreact', json={
        'token': 'sdf)8sd',
        'message_id': m_id1,
        'react_id': 1,
    })
    assert resp.status_code == 400

    # owner unreact to invalid message id
    resp = requests.post(url + 'message/unreact', json={
        'token': owner['token'],
        'message_id': m_id1+666,
        'react_id': 1,
    })
    assert resp.status_code == 400

    # owner unreact with invalid react id
    resp = requests.post(url + 'message/unreact', json={
        'token': owner['token'],
        'message_id': m_id1,
        'react_id': 666,
    })


    # Test:
    #    - Unreact to the message that has no reacts
    #    - Unreact to the message without using react beforehand
    #
    # Scenario:
    #    - owner unreacts to the message
    #    - user1 attempts to unreact the message that has no react at all
    #    - user1 reacts to the message
    #    - user2 attempts to unreact the message that user1 reacted to


    # owner unreacts
    resp = requests.post(url + 'message/unreact', json={
        'token': owner['token'],
        'message_id': m_id1,
        'react_id': 1,
    })
    assert resp.status_code == 200

    # check that the message has no reacts
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    messages = resp.json()['messages']

    for message in messages:
        if message['message_id'] == m_id1:
            assert message['reacts'][0]['u_ids'] == []

    # user 1 unreacts to the message with no reacts
    resp = requests.post(url + 'message/unreact', json={
        'token': user1['token'],
        'message_id': m_id1,
        'react_id': 1,
    })
    assert resp.status_code == 400

    # user1 reacts to the message
    resp = requests.post(url + 'message/react', json={
        'token': user1['token'],
        'message_id': m_id1,
        'react_id': 1,
    })
    assert resp.status_code == 200

    # check that only user1 react to the message
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    messages = resp.json()['messages']

    for message in messages:
        if message['message_id'] == m_id1:
            assert message['reacts'][0]['u_ids'] == [user1['u_id']]

    # user2 unreact user1's react
    resp = requests.post(url + 'message/unreact', json={
        'token': user2['token'],
        'message_id': m_id1,
        'react_id': 1,
    })
    assert resp.status_code == 400


def test_http_message_pin(url):
    '''
    HTTP test for message_pin

    Tests:
        - Pinning a message normally
        - Pinning with invalid token
        - Pinning messages whilst not being in channel
        - Pinning with invalid message id
        - Pinning without being owner of channel
        - Pinning an already pinned message
    '''
    assert requests.delete(url + 'clear').status_code == 200


    # Test:
    #    - Pinning a message normally
    #
    # Scenario:
    #    - The owner and user1 register
    #    - The owner creates a channel, invites user1
    #    - user1 sends a message
    #    - The owner pins the message
    #    - Test checks that the message is pinned


    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'thisismymail69@gmail.com',
        'password': 'password',
        'name_first': 'Owner',
        'name_last': 'Ownerson',
    })
    assert resp.status_code == 200
    owner = resp.json()

    # Set up channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Main HUB',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # Register user 1
    resp = requests.post(url + 'auth/register', json={
        'email': 'useremail01@gmail.com',
        'password': 'password',
        'name_first': 'User',
        'name_last': 'Userson',
    })
    assert resp.status_code == 200
    user1 = resp.json()

    # Invite user 1
    resp = requests.post(url + 'channel/invite', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'u_id': user1['u_id'],
    })
    assert resp.status_code == 200

    # user1 sends a message
    resp = requests.post(url + 'message/send', json={
        'token': user1['token'],
        'channel_id': channel_id,
        'message': 'I am good with alphebet',
    })
    assert resp.status_code == 200
    m_id1 = resp.json()['message_id']

    # Owner pins message
    resp = requests.post(url + 'message/pin', json={
        'token': owner['token'],
        'message_id': m_id1,
    })
    assert resp.status_code == 200

    # Update messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })

    assert resp.status_code == 200
    messages = resp.json()['messages']

    # Check that message is pinned
    for message in messages:
        if message['message_id'] == m_id1:
            assert message['is_pinned'] is True


    # Test:
    #    - Pinning with invalid token
    #    - Pinning messages whilst not being in channel
    #    - Pinning with invalid message id
    #    - Pinning without being owner of channel
    #
    # Scenario:
    #    - user2 registers (not in channel)
    #    - user1 sends another message
    #    - Test tries pinning with invalid token and message id
    #    - user2 tries pinning without being in channel
    #    - user1 tries pinning whilst being in channel (not owner)
    #    - Test checks that message is still not pinned


    # Register user 2
    resp = requests.post(url + 'auth/register', json={
        'email': 'snowsmasher666@gmail.com',
        'password': 'password',
        'name_first': 'Snow',
        'name_last': 'Snowson',
    })
    user2 = resp.json()

    # user1 sends a message
    resp = requests.post(url + 'message/send', json={
        'token': user1['token'],
        'channel_id': channel_id,
        'message': 'hello everyone',
    })
    assert resp.status_code == 200
    m_id2 = resp.json()['message_id']

    # Update messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })

    assert resp.status_code == 200
    messages = resp.json()['messages']

    # Pinning with invalid token
    resp = requests.post(url + 'message/pin', json={
        'token': 'notavalidtoken',
        'message_id': m_id2,
    })
    assert resp.status_code == 400

    # Pinning with invalid message id
    resp = requests.post(url + 'message/pin', json={
        'token': owner['token'],
        'message_id': -404,
    })
    assert resp.status_code == 400

    # Pinning without being in the channel
    resp = requests.post(url + 'message/pin', json={
        'token': user2['token'],
        'message_id': m_id2,
    })
    assert resp.status_code == 400

    # Pinning without being owner of channel
    resp = requests.post(url + 'message/pin', json={
        'token': user1['token'],
        'message_id': m_id2,
    })
    assert resp.status_code == 400

    # Update messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    messages = resp.json()['messages']

    # Check that message is not pinned
    for message in messages:
        if message['message_id'] == m_id2:
            assert message['is_pinned'] is False


    # Test:
    #    - Pinning an already pinned message
    #
    # Scenario:
    #    - owner sends a message
    #    - owner pins the message
    #    - test checks that message is pinned
    #    - owner tries to pin the same message again


    # owner sends a message
    resp = requests.post(url + 'message/send', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': 'hello user1',
    })
    assert resp.status_code == 200
    m_id3 = resp.json()['message_id']

    # Owner pins message (m_id3)
    resp = requests.post(url + 'message/pin', json={
        'token': owner['token'],
        'message_id': m_id3,
    })

    # Update messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    messages = resp.json()['messages']

    # Check that message is pinned
    for message in messages:
        if message['message_id'] == m_id3:
            assert message['is_pinned'] is True

    # Owner tries to pin message again
    resp = requests.post(url + 'message/pin', json={
        'token': owner['token'],
        'message_id': m_id3,
    })
    assert resp.status_code == 400


def test_http_message_unpin(url):
    '''
    HTTP test for message_unpin
    Tests:
        - Unpinning a message normally
        - Unpinning with invalid token
        - Unpinning messages whilst not being in channel
        - Unpinning with invalid message id
        - Unpinning without being owner of channel
        - Unpinning an already unpinned message
    '''
    assert requests.delete(url + 'clear').status_code == 200


    # Test:
    #    - Unpinning a message normally
    #
    # Scenario:
    #    - The owner and user1 register
    #    - The owner creates a channel, invites user1
    #    - user1 sends a message
    #    - The owner pins the message
    #    - Test checks that the message is pinned
    #    - owner unpins the message
    #    - Test checks that the message is not pinned


    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'thisismymail69@gmail.com',
        'password': 'password',
        'name_first': 'Owner',
        'name_last': 'Ownerson',
    })
    assert resp.status_code == 200
    owner = resp.json()

    # Set up channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Main HUB',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # Register user 1
    resp = requests.post(url + 'auth/register', json={
        'email': 'useremail01@gmail.com',
        'password': 'password',
        'name_first': 'User',
        'name_last': 'Userson',
    })
    assert resp.status_code == 200
    user1 = resp.json()

    # Invite user 1
    resp = requests.post(url + 'channel/invite', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'u_id': user1['u_id'],
    })
    assert resp.status_code == 200

    # user1 sends a message
    resp = requests.post(url + 'message/send', json={
        'token': user1['token'],
        'channel_id': channel_id,
        'message': 'I am good with alphebet',
    })
    assert resp.status_code == 200
    m_id1 = resp.json()['message_id']

    # Owner pins message
    resp = requests.post(url + 'message/pin', json={
        'token': owner['token'],
        'message_id': m_id1,
    })
    assert resp.status_code == 200

    # Update messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })

    assert resp.status_code == 200
    messages = resp.json()['messages']

    # Check that message is pinned
    for message in messages:
        if message['message_id'] == m_id1:
            assert message['is_pinned'] is True

    # Owner unpins message
    resp = requests.post(url + 'message/unpin', json={
        'token': owner['token'],
        'message_id': m_id1,
    })
    assert resp.status_code == 200

    # Update messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })

    assert resp.status_code == 200
    messages = resp.json()['messages']

    # Check that message is not pinned
    for message in messages:
        if message['message_id'] == m_id1:
            assert message['is_pinned'] is False


    # Test:
    #    - Unpinning with invalid token
    #    - Unpinning messages whilst not being in channel
    #    - Unpinning with invalid message id
    #    - Unpinning without being owner of channel
    #
    # Scenario:
    #    - user2 registers (not in channel)
    #    - user1 sends another message
    #    - owner pins the message
    #    - Test tries unpinning with invalid token and message id
    #    - user2 tries unpinning without being in channel
    #    - user1 tries unpinning whilst being in channel (not owner)
    #    - Test checks that message is still pinned


    # Register user 2
    resp = requests.post(url + 'auth/register', json={
        'email': 'snowsmasher666@gmail.com',
        'password': 'password',
        'name_first': 'Snow',
        'name_last': 'Snowson',
    })
    user2 = resp.json()

    # user1 sends a message
    resp = requests.post(url + 'message/send', json={
        'token': user1['token'],
        'channel_id': channel_id,
        'message': 'hello everyone',
    })
    assert resp.status_code == 200
    m_id2 = resp.json()['message_id']

    # Update messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })

    assert resp.status_code == 200
    messages = resp.json()['messages']

    # Owner pins message
    resp = requests.post(url + 'message/pin', json={
        'token': owner['token'],
        'message_id': m_id2,
    })
    assert resp.status_code == 200

    # Update messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    messages = resp.json()['messages']

    # Unpinning with invalid token
    resp = requests.post(url + 'message/unpin', json={
        'token': 'notavalidtoken',
        'message_id': m_id2,
    })
    assert resp.status_code == 400

    # Unpinning with invalid message id
    resp = requests.post(url + 'message/unpin', json={
        'token': owner['token'],
        'message_id': -400,
    })
    assert resp.status_code == 400

    # Unpinning without being in the channel
    resp = requests.post(url + 'message/unpin', json={
        'token': user2['token'],
        'message_id': m_id2,
    })
    assert resp.status_code == 400

    # Unpinning without being owner of channel
    resp = requests.post(url + 'message/unpin', json={
        'token': user1['token'],
        'message_id': m_id2,
    })
    assert resp.status_code == 400

    # Update messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    messages = resp.json()['messages']

    # Check that message is still pinned
    for message in messages:
        if message['message_id'] == m_id2:
            assert message['is_pinned'] is True


    # Test:
    #    - Unpinning an already unpinned message
    #
    # Scenario:
    #    - owner sends a message
    #    - owner pins the message
    #    - Test checks that message is pinned
    #    - owner unpins the message
    #    - owner tries to unpin the message again
    #    - Test checks that the message is unpinned


    # owner sends a message
    resp = requests.post(url + 'message/send', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': 'hello user1',
    })
    assert resp.status_code == 200
    m_id3 = resp.json()['message_id']

    # Owner pins message (m_id3)
    resp = requests.post(url + 'message/pin', json={
        'token': owner['token'],
        'message_id': m_id3,
    })

    # Update messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    messages = resp.json()['messages']

    # Check that message is pinned
    for message in messages:
        if message['message_id'] == m_id3:
            assert message['is_pinned'] is True

    # Owner unpins message
    resp = requests.post(url + 'message/unpin', json={
        'token': owner['token'],
        'message_id': m_id3,
    })
    assert resp.status_code == 200

    # Owner tries to unpins message again
    resp = requests.post(url + 'message/unpin', json={
        'token': owner['token'],
        'message_id': m_id3,
    })
    assert resp.status_code == 400

    # Update messages
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    messages = resp.json()['messages']

    # Check that message is not pinned
    for message in messages:
        if message['message_id'] == m_id3:
            assert message['is_pinned'] is False
