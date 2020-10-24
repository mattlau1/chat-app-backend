''' Import required modules '''
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from echo_http_test import url

################
## HTTP other ##
################
def test_http_clear(url):
    '''
    HTTP test for clear
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'bobsmith@gmail.com',
        'password': 'password',
        'name_first': 'Bob',
        'name_last': 'Smith',
    })
    assert resp.status_code == 200
    owner = resp.json()

    # Set up channel
    resp = requests.post(url + 'channels/create', json={
        'token': owner['token'],
        'name': 'Channel 1',
        'is_public': True,
    })
    assert resp.status_code == 200
    channel_id = resp.json()['channel_id']

    # Clear
    assert requests.delete(url + 'clear').status_code == 200

    # User now cannot view the channel details
    resp = requests.get(url + 'channel/details', params={
        'token': owner['token'],
        'channel_id': channel_id,
    })
    assert resp.status_code == 400

    # Register owner
    resp = requests.post(url + 'auth/register', json={
        'email': 'bobsmith@gmail.com',
        'password': 'password',
        'name_first': 'Bob',
        'name_last': 'Smith',
    })
    assert resp.status_code == 200

    # Cannot register same person twice
    resp = requests.post(url + 'auth/register', json={
        'email': 'bobsmith@gmail.com',
        'password': 'password',
        'name_first': 'Bob',
        'name_last': 'Smith',
    })
    assert resp.status_code == 400

    # Clear
    assert requests.delete(url + 'clear').status_code == 200

    # Register owner again successfully
    resp = requests.post(url + 'auth/register', json={
        'email': 'bobsmith@gmail.com',
        'password': 'password',
        'name_first': 'Bob',
        'name_last': 'Smith',
    })
    assert resp.status_code == 200


def test_http_users_all(url):
    '''
    HTTP test for users_all
    '''
    assert requests.delete(url + 'clear').status_code == 200
    
    # Register three users
    resp = requests.post(url + 'auth/register', json={
        'email': 'markzuckerberg@gmail.com',
        'password': 'password',
        'name_first': 'Mark',
        'name_last': 'Zuckerberg',
    })
    assert resp.status_code == 200
    f_owner = resp.json()

    resp = requests.post(url + 'auth/register', json={
        'email': 'brianpaul@gmail.com',
        'password': 'password',
        'name_first': 'Brian',
        'name_last': 'Paul',
    })
    assert resp.status_code == 200
    random_user1 = resp.json()

    resp = requests.post(url + 'auth/register', json={
        'email': 'gregstevens@gmail.com',
        'password': 'password',
        'name_first': 'Greg',
        'name_last': 'Stevens',
    })
    assert resp.status_code == 200
    random_user2 = resp.json()

    # Set handles of the users
    resp = requests.put(url + 'user/profile/sethandle', json= {
        'token': f_owner['token'],
        'handle_str': 'MARKZUCKERBERG'
    })
    assert resp.status_code == 200

    resp = requests.put(url + 'user/profile/sethandle', json= {
        'token': random_user1['token'],
        'handle_str': 'BRIANPAUL'
    })
    assert resp.status_code == 200

    resp = requests.put(url + 'user/profile/sethandle', json= {
        'token': random_user2['token'],
        'handle_str': 'GREGSTEVENS'
    })
    assert resp.status_code == 200

    # Check that the details returned from users_all are correct
    resp = requests.get(url + 'users/all', params={
        'token': f_owner['token'],
    })
    assert resp.status_code == 200
    payload = resp.json()
    assert payload == {
        'users': [
            {
                'u_id': f_owner['u_id'],
                'email': 'markzuckerberg@gmail.com',
                'name_first': 'Mark',
                'name_last': 'Zuckerberg',
                'handle_str': 'MARKZUCKERBERG',
            },
            {
                'u_id': random_user1['u_id'],
                'email': 'brianpaul@gmail.com',
                'name_first': 'Brian',
                'name_last': 'Paul',
                'handle_str': 'BRIANPAUL',
            },
            {
                'u_id': random_user2['u_id'],
                'email': 'gregstevens@gmail.com',
                'name_first': 'Greg',
                'name_last': 'Stevens',
                'handle_str': 'GREGSTEVENS',
            },
        ],
    }

    # Invalid token
    resp = requests.get(url + 'users/all', params={
        'token': '',
    })
    assert resp.status_code == 400


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
