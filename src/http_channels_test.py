''' Import required modules '''
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from echo_http_test import url

###################
## HTTP channels ##
###################
def test_http_channels_list(url):
    '''
    HTTP test for channels_list

    Tests:
        - Listing channels validly (valid token & name)
        - Listing channels with invalid token
    '''
    assert requests.delete(url + 'clear').status_code == 200


    # Test:
    #    - Listing user channels validly
    #
    # Scenario:
    #    - user registers and creates channel
    #    - user lists channel


    # Create user
    resp = requests.post(url + 'auth/register', json={
        'email': 'mmmonkey97@hotmail.com',
        'password': 'banana',
        'name_first': 'John',
        'name_last': 'Johnson',
    })
    assert resp.status_code == 200
    user = resp.json()

    # Create normal channel
    resp = requests.post(url + 'channels/create', json={
        'token': user['token'],
        'name': 'Movie Discussion',
        'is_public': True
    })
    assert resp.status_code == 200

    resp = requests.get(url + 'channels/list', params={
        'token': user['token'],
    })
    assert resp.status_code == 200
    channel = resp.json()

    assert len(channel['channels']) == 1

    # Create 2nd channel
    resp = requests.post(url + 'channels/create', json={
        'token': user['token'],
        'name': 'Banana Club',
        'is_public': False
    })
    assert resp.status_code == 200

    # Check user channels
    resp = requests.get(url + 'channels/list', params={
        'token': user['token'],
    })
    assert resp.status_code == 200
    channel = resp.json()

    assert len(channel['channels']) == 2


    # Test:
    #    - Listing user channels invalidly
    #
    # Scenario:
    #    - user creates another channel
    #    - test tries to list channels with invalid token


    # Create normal channel
    resp = requests.post(url + 'channels/create', json={
        'token': user['token'],
        'name': 'Gaming Hub',
        'is_public': True
    })
    assert resp.status_code == 200

    resp = requests.get(url + 'channels/list', params={
        'token': 'thisisaninvalidtoken',
    })
    assert resp.status_code == 400


def test_http_channels_listall(url):
    '''
    HTTP test for channels_listall

    Tests:
        - Validly listing all channels
        - Invalidly listing all channels
    '''


    # Test:
    #    - Listing all channels validly
    #
    # Scenario:
    #    - Two users register
    #    - user1 creates private channel
    #    - user2 creates private channel
    #    - Test checks if channels_listall is working correctly with private channels


    assert requests.delete(url + 'clear').status_code == 200

    # Register user 1
    resp = requests.post(url + 'auth/register', json={
        'email': 'mmmonkey97@hotmail.com',
        'password': 'banana',
        'name_first': 'John',
        'name_last': 'Johnson',
    })
    assert resp.status_code == 200
    user1 = resp.json()

    # Register user 2
    resp = requests.post(url + 'auth/register', json={
        'email': 'shakespearegaming@hotmail.com',
        'password': 'iloveenglish',
        'name_first': 'Shakespeare',
        'name_last': 'Shakespeareson',
    })
    assert resp.status_code == 200
    user2 = resp.json()

    # Create private channel for user 1
    resp = requests.post(url + 'channels/create', json={
        'token': user1['token'],
        'name': 'Banana Cave',
        'is_public': False
    })
    assert resp.status_code == 200

    # Check user 1 channels
    resp = requests.get(url + 'channels/list', params={
        'token': user1['token'],
    })
    assert resp.status_code == 200
    channel = resp.json()

    assert len(channel['channels']) == 1

    # Check user 2 channels
    resp = requests.get(url + 'channels/list', params={
        'token': user2['token'],
    })
    assert resp.status_code == 200
    channel = resp.json()

    assert len(channel['channels']) == 0

    # Create private channel for user2
    resp = requests.post(url + 'channels/create', json={
        'token': user2['token'],
        'name': 'English House',
        'is_public': False
    })
    assert resp.status_code == 200

    # Check user 2 channels
    resp = requests.get(url + 'channels/list', params={
        'token': user2['token'],
    })
    assert resp.status_code == 200
    channel = resp.json()

    assert len(channel['channels']) == 1

    # Check user 1 channels
    resp = requests.get(url + 'channels/list', params={
        'token': user1['token'],
    })
    assert resp.status_code == 200
    channel = resp.json()

    assert len(channel['channels']) == 1

    # Check list all channels
    resp = requests.get(url + 'channels/listall', params = {
        'token': user1['token'],
    })
    assert resp.status_code == 200
    all_channels = resp.json()

    assert len(all_channels['channels']) == 2


    # Test:
    #    - Listing all channels with invalid token
    #
    # Scenario:
    #    - Test tries to list all channels with an invalid token


    resp = requests.get(url + 'channels/listall', params={
        'token': 'thisisaninvalidtoken',
    })
    assert resp.status_code == 400


def test_http_channels_create(url):
    '''
    HTTP test for channels_create
    '''
    assert requests.delete(url + 'clear').status_code == 200
    
    # Create user
    resp = requests.post(url + 'auth/register', json={
        'email': 'stvnnguyen69@hotmail.com',
        'password': 'password',
        'name_first': 'Steven',
        'name_last': 'Nguyen',
    })
    assert resp.status_code == 200
    user = resp.json()

    # Create normal channel
    resp = requests.post(url + 'channels/create', json={
        'token': user['token'],
        'name': 'Gaming Hub',
        'is_public': True
    })
    assert resp.status_code == 200

    # Create a channel with name more than 20 characters
    resp = requests.post(url + 'channels/create', json={
        'token': user['token'],
        'name': 'a' * 21,
        'is_public': True
    })
    assert resp.status_code == 400

    # Create a channel with invalid token
    resp = requests.post(url + 'channels/create', json={
        'token': 'ASD@*(&!@*(s',
        'name': 'UNSW club',
        'is_public': True
    })
    assert resp.status_code == 400

    # Create a channel with empty name
    resp = requests.post(url + 'channels/create', json={
        'token': user['token'],
        'name': '',
        'is_public': False
    })
    assert resp.status_code == 400

    # Create a channel with spaces in name
    resp = requests.post(url + 'channels/create', json={
        'token': user['token'],
        'name': '     ',
        'is_public': False
    })
    assert resp.status_code == 400
