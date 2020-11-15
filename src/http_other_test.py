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

    Test:
        - Clearing all registered users
        - Clearing channels

    Scenario:
        - owner successfully registers and sets up channel
        - Test clears
        - owner now cannot see channel details
        - owner successfully registers
        - Test checks that registration was successful
        - owner successfully registers again
        - Test checks that registration was unsuccessful
        - Test clears
        - owner successfully registers again
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

    Test:
        - Getting details of all users validly
        - Getting details of all users with an invalid token

    Scenario:
        - Three users register and set handles
        - Test checks that details from users_all is correct
        - Test tries to get details from all users with an invalid token
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

    # Ignore profile_img_url from checks
    for member in payload['users']:
        del member['profile_img_url']

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

    Test:
        - Flockr owner changing permissions of a member to make them a Flockr owner
        - Flockr owner changing permissions of a Flockr owner to make them a member

    Scenario:
        - Two users register
        - User 1 creates a private channel
        - User 1 (a Flockr owner) changes permissions of User 2, making them
          a Flockr owner too
        - User 2 is now able to join the private channel as a Flockr owner
        - User 2 creates a private channel
        - User 2 changes permissions of User 1, making them a member
        - Check that User 1 is unable to join User 2's private channel as they
          are now a member
    '''
    assert requests.delete(url + 'clear').status_code == 200
    
    # Register two users
    resp = requests.post(url + 'auth/register', json={
        'email': 'billgates@gmail.com',
        'password': 'password',
        'name_first': 'Bill',
        'name_last': 'Gates',
    })
    assert resp.status_code == 200
    user1 = resp.json()

    resp = requests.post(url + 'auth/register', json={
        'email': 'steveballmer@gmail.com',
        'password': 'password',
        'name_first': 'Steve',
        'name_last': 'Ballmer',
    })
    assert resp.status_code == 200
    user2 = resp.json()

    # First user creates a private channel
    resp = requests.post(url + 'channels/create', json={
        'token': user1['token'],
        'name': 'Private Channel 1',
        'is_public': False,
    })
    assert resp.status_code == 200
    channel_id1 = resp.json()['channel_id']

    # First user changes permissions of second user to make them a Flockr owner
    resp = requests.post(url + 'admin/userpermission/change', json={
        'token': user1['token'],
        'u_id': user2['u_id'],
        'permission_id': 1,
    })
    assert resp.status_code == 200

    # Check that second user is now a Flockr owner
    # (verified by now being able to join the private channel)
    resp = requests.post(url + 'channel/join', json={
        'token': user2['token'],
        'channel_id': channel_id1
    })
    assert resp.status_code == 200

    # Second user creates a private channel
    resp = requests.post(url + 'channels/create', json={
        'token': user2['token'],
        'name': 'Private Channel 2',
        'is_public': False,
    })
    assert resp.status_code == 200
    channel_id2 = resp.json()['channel_id']

    # Second user changes permissions of first user to make them a member
    resp = requests.post(url + 'admin/userpermission/change', json={
        'token': user2['token'],
        'u_id': user1['u_id'],
        'permission_id': 2,
    })
    assert resp.status_code == 200

    # Check that first user is now a member
    # (verified by now not being able to join private channels)
    resp = requests.post(url + 'channel/join', json={
        'token': user1['token'],
        'channel_id': channel_id2
    })
    assert resp.status_code == 400

    # Test:
    #    - Changing an invalid user's permissions
    #    - Changing a user's permissions to an invalid permission
    #    - Changing a user's permissions without owner permissions
    #    - Changing a user's permissions using an invalid token
    #
    # Scenario:
    #    - Check that a user with invalid u_id's permissions cannot be changed
    #    - Check that a user's permissions cannot be changed to an invalid permission_id
    #    - Check that a user without owner permissions cannot change permissions
    #    - Check that a user's permissions cannot be changed with an invalid token

    # u_id does not refer to a valid user
    resp = requests.post(url + 'admin/userpermission/change', json={
        'token': user2['token'],
        'u_id': user1['u_id'] + 100,
        'permission_id': 1,
    })
    assert resp.status_code == 400

    # permission_id does not refer to a valid permission
    resp = requests.post(url + 'admin/userpermission/change', json={
        'token': user2['token'],
        'u_id': user1['u_id'],
        'permission_id': 3,
    })
    assert resp.status_code == 400

    # Authorised user is not an owner
    resp = requests.post(url + 'admin/userpermission/change', json={
        'token': user1['token'],
        'u_id': user2['u_id'],
        'permission_id': 2,
    })
    assert resp.status_code == 400

    # Invalid token
    resp = requests.post(url + 'admin/userpermission/change', json={
        'token': '',
        'u_id': user2['u_id'],
        'permission_id': 1,
    })
    assert resp.status_code == 400


def test_http_search(url):
    '''
    HTTP test for search

    Test:
        - Searching for a query string, only returns the messages containing the string
          in channels the user has joined

    Scenario:
        - Admin registers and sets up a channel
        - User registers, and sets up a private channel
        - User joins the admin channel, then sends the message: 'Hello world'
        - Admin sends two messages, 'Hello' and 'hello' to admin channel
        - User sends a message, 'Hellooo', to both channels
        - Check that 3 messages appear when admin searches for the substring 'Hello'
        - Check that 4 messages appear when user searches for the substring 'Hello'
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

    # Test:
    #    - Searching for a string with an invalid token
    #    - Searching for a string not contained in any messages
    #
    # Scenario:
    #    - Check that you cannot search with an invalid token
    #    - Admin searches for substring 'asdf' - check that no messages are returned
    #    - User searches for substring 'asdf' - check that no messages are returned

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
