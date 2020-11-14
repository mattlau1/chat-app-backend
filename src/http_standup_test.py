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
## HTTP standup ##
##################
def test_http_standup_start_valid(url):
    '''
    HTTP test for standup_start (valid)

    Test:
        - Validly start a standup
    
    Scenario:
        - The owner creates an account, and then a channel
        - The owner starts a standup for 5 seconds
        - Check that standup is active by calling standup_active
        - Check that the returned time_finish of standup_start and standup_active
        are the same
        - After standup ends, check that standup is inactive by calling 
        standup_active
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'owner@gmail.com',
        'password': 'password',
        'name_first': 'Flockr',
        'name_last': 'Owner',
    })
    assert resp.status_code == 200
    owner = resp.json()

    # Set up channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Test Channel',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # Owner starts standup for 5 seconds
    resp = requests.post(url + 'standup/start', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'length': 5,
    })
    assert resp.status_code == 200
    t_finish = resp.json()['time_finish']

    # Check that standup is active
    resp = requests.get(url + 'standup/active', params={
        'token': owner['token'],
        'channel_id': channel_id,
    })
    assert resp.status_code == 200
    standup_details = resp.json()
    assert standup_details['is_active'] is True

    # Check time_finish of both standup_start and standup_active are the same
    assert t_finish == standup_details['time_finish']

    # Check standup is inactive after standup ends
    sleep(6)
    resp = requests.get(url + 'standup/active', params={
        'token': owner['token'],
        'channel_id': channel_id,
    })
    assert resp.status_code == 200
    standup_details = resp.json()
    assert standup_details['is_active'] is False


def test_http_standup_start_invalid(url):
    '''
    HTTP test for standup_start (invalid)
    
    Test:
        - Invalidly start standups to check if errors are correctly raised
    
    Scenario:
        - The owner and a user create accounts
        - The owner creates a channel
        - Test starting standup with an invalid token
        - Test starting standup for an invalid channel ID
        - Test starting standup in channel that user is not a member of
        - Test starting standup with an invalid standup length
        - Test starting standup while an active standup is running
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'owner@gmail.com',
        'password': 'password',
        'name_first': 'Flockr',
        'name_last': 'Owner',
    })
    assert resp.status_code == 200
    owner = resp.json()

    # Register user
    resp = requests.post(url + 'auth/register', json={
        'email': 'user@gmail.com',
        'password': 'password',
        'name_first': 'Random',
        'name_last': 'User',
    })
    assert resp.status_code == 200
    user = resp.json()

    # Owner creates a channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Test Channel',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # Invalid token
    resp = requests.post(url + 'standup/start', json={
        'token': '',
        'channel_id': channel_id,
        'length': 5,
    })
    assert resp.status_code == 400

    # Invalid channel ID
    resp = requests.post(url + 'standup/start', json={
        'token': owner['token'],
        'channel_id': channel_id + 100,
        'length': 5,
    })
    assert resp.status_code == 400

    # User not member of channel
    resp = requests.post(url + 'standup/start', json={
        'token': user['token'],
        'channel_id': channel_id,
        'length': 5,
    })
    assert resp.status_code == 400

    # Invalid standup length
    resp = requests.post(url + 'standup/start', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'length': 0,
    })
    assert resp.status_code == 400
    resp = requests.post(url + 'standup/start', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'length': -5,
    })
    assert resp.status_code == 400

    # Active standup is currently running
    resp = requests.post(url + 'standup/start', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'length': 5,
    })
    assert resp.status_code == 200
    resp = requests.post(url + 'standup/start', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'length': 5,
    })
    assert resp.status_code == 400


def test_http_standup_active_valid(url):
    '''
    HTTP test for standup_active (valid)

    Test:
        - Validly check if a standup is active
    
    Scenario:
        - The owner creates an account, and then a channel
        - Check standup_active returns correct values when standup inactive
        - The owner starts a standup for 5 seconds
        - Check standup_active returns correct values when standup active
        - Check that the returned time_finish of standup_start and standup_active
        are the same
        - Check standup_active returns correct values after standup ends
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'owner@gmail.com',
        'password': 'password',
        'name_first': 'Flockr',
        'name_last': 'Owner',
    })
    assert resp.status_code == 200
    owner = resp.json()

    # Set up channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Test Channel',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # Check standup_active returns correct values
    resp = requests.get(url + 'standup/active', params={
        'token': owner['token'],
        'channel_id': channel_id,
    })
    assert resp.status_code == 200
    standup_details = resp.json()
    assert standup_details['is_active'] is False
    assert standup_details['time_finish'] is None

    # Owner starts standup for 5 seconds
    resp = requests.post(url + 'standup/start', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'length': 5,
    })
    assert resp.status_code == 200
    t_finish = resp.json()['time_finish']

    # Check standup_active returns correct values
    resp = requests.get(url + 'standup/active', params={
        'token': owner['token'],
        'channel_id': channel_id,
    })
    assert resp.status_code == 200
    standup_details = resp.json()
    assert standup_details['is_active'] is True
    # Check time_finish of both standup_start and standup_active are the same
    assert t_finish == standup_details['time_finish']

    # Check standup_active returns correct values
    sleep(6)
    resp = requests.get(url + 'standup/active', params={
        'token': owner['token'],
        'channel_id': channel_id,
    })
    assert resp.status_code == 200
    standup_details = resp.json()
    assert standup_details['is_active'] is False
    assert standup_details['time_finish'] is None


def test_http_standup_active_invalid(url):
    '''
    HTTP test for standup_active (invalid)

    Test:
        - Invalidly check if a standup is active to check if errors are
        correctly raised
    
    Scenario:
        - The owner and a user create accounts
        - The owner creates a channel
        - Test checking standup status with an invalid token
        - Test checking standup status for an invalid channel ID
        - Test checking standup status in channel that user is not a member of
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'owner@gmail.com',
        'password': 'password',
        'name_first': 'Flockr',
        'name_last': 'Owner',
    })
    assert resp.status_code == 200
    owner = resp.json()

    # Register user
    resp = requests.post(url + 'auth/register', json={
        'email': 'user@gmail.com',
        'password': 'password',
        'name_first': 'Random',
        'name_last': 'User',
    })
    assert resp.status_code == 200
    user = resp.json()

    # Owner creates a channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Test Channel',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # Invalid token
    resp = requests.get(url + 'standup/active', params={
        'token': '',
        'channel_id': channel_id,
    })
    assert resp.status_code == 400

    # Invalid channel ID
    resp = requests.get(url + 'standup/active', params={
        'token': owner['token'],
        'channel_id': channel_id + 100,
    })
    assert resp.status_code == 400

    # User not member of channel
    resp = requests.get(url + 'standup/active', params={
        'token': user['token'],
        'channel_id': channel_id,
    })
    assert resp.status_code == 400


def test_http_standup_send_valid(url):
    '''
    HTTP test for standup_send (valid)

    Test:
        - Validly send messages to get buffered in the standup queue
    
    Scenario:
        - The owner and a user create accounts
        - The owner creates a channel, and the user joins the channel
        - The owner starts standup for 8 seconds
        - The owner and user send messages during the standup
        - Check only one message (the packaged message containing all 
        standup messages) is sent after the standup ends
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'owner@gmail.com',
        'password': 'password',
        'name_first': 'Flockr',
        'name_last': 'Owner',
    })
    assert resp.status_code == 200
    owner = resp.json()

    # Register user
    resp = requests.post(url + 'auth/register', json={
        'email': 'user@gmail.com',
        'password': 'password',
        'name_first': 'Random',
        'name_last': 'User',
    })
    assert resp.status_code == 200
    user = resp.json()

    # Owner creates a channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Test Channel',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # User joins the channel
    resp = requests.post(url + 'channel/join', json={
        'token': user['token'],
        'channel_id': channel_id,
    })
    assert resp.status_code == 200

    # Owner starts standup for 8 seconds
    resp = requests.post(url + 'standup/start', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'length': 8,
    })
    assert resp.status_code == 200

    # Users send messages during the standup
    message1 = 'F' * 1000
    message2 = 'X' * 1000
    for _ in range(0, 3):
        resp = requests.post(url + 'standup/send', json={
            'token': owner['token'],
            'channel_id': channel_id,
            'message': message1,
        })
        assert resp.status_code == 200
        resp = requests.post(url + 'standup/send', json={
            'token': user['token'],
            'channel_id': channel_id,
            'message': message2,
        })
        assert resp.status_code == 200
    
    # Check only one message (containing all standup messages) is sent 
    # after the standup ends
    sleep(9)
    resp = requests.get(url + 'channel/messages', params={
        'token': owner['token'],
        'channel_id': channel_id,
        'start': 0,
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert len(payload['messages']) == 1


def test_http_standup_send_invalid(url):
    '''
    HTTP test for standup_send (invalid)

    Test:
        - Invalidly send messages to get buffered in the standup queue to
        check if errors are correctly raised
    
    Scenario:
        - The owner and a user create accounts
        - The owner creates a channel
        - Test sending standup message when standup inactive
        - The owner starts a standup
        - Test sending standup message with an invalid token
        - Test sending standup message for an invalid channel ID
        - Test sending standup message with invalid message length
        - Test sending standup message in channel user is not a member of
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'owner@gmail.com',
        'password': 'password',
        'name_first': 'Flockr',
        'name_last': 'Owner',
    })
    assert resp.status_code == 200
    owner = resp.json()

    # Register user
    resp = requests.post(url + 'auth/register', json={
        'email': 'user@gmail.com',
        'password': 'password',
        'name_first': 'Random',
        'name_last': 'User',
    })
    assert resp.status_code == 200
    user = resp.json()

    # Owner creates a channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Test Channel',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # Active standup is not currently running
    resp = requests.post(url + 'standup/send', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': 'Test message!',
    })
    assert resp.status_code == 400

    # Owner starts a standup
    resp = requests.post(url + 'standup/start', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'length': 8,
    })
    assert resp.status_code == 200

    # Invalid token
    resp = requests.post(url + 'standup/send', json={
        'token': '',
        'channel_id': channel_id,
        'message': 'Test message!',
    })
    assert resp.status_code == 400

    # Invalid channel ID
    resp = requests.post(url + 'standup/send', json={
        'token': owner['token'],
        'channel_id': channel_id + 100,
        'message': 'Test message!',
    })
    assert resp.status_code == 400

    # Invalid message length - empty message
    resp = requests.post(url + 'standup/send', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': '',
    })
    assert resp.status_code == 400
    
    message = 'F' * 1001
    # Invalid message length - 1001 characters
    resp = requests.post(url + 'standup/send', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': message,
    })
    assert resp.status_code == 400
    # Invalid message length - 1002 characters
    resp = requests.post(url + 'standup/send', json={
        'token': owner['token'],
        'channel_id': channel_id,
        'message': message + 'F',
    })
    assert resp.status_code == 400

    # User not member of channel
    resp = requests.post(url + 'standup/send', json={
        'token': user['token'],
        'channel_id': channel_id,
        'message': message,
    })
    assert resp.status_code == 400
