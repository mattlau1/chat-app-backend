''' Import required modules '''
import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json
from echo_http_test import url

###############
## HTTP auth ##
###############
def test_http_auth_login(url):
    '''
    HTTP test for auth_login

    Test:
        - Logging in with an invalid email format
        - Logging in without registering
        - Logging in with invalid password
        - Logging in validly
    
    Scenario:
        - User tries to login with invalid email format
        - User tries to login with unregistered account
        - User registers
        - User attempts to login with incorrect password
        - User logs in with correct password
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

    Test:
        - Logging out with invalid token
        - Logging out normally
    
    Scenario:
        - Test tries to logout with invalid token
        - User registers and logs in
        - User logs out normally
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

    Test:
        - Registering with an invalid email format
        - Registering with a password less than 6 characters long
        - Registering with invalid first and last name Length
        - Registering normally
        - Registering with email already in use
    
    Scenario:
        - User tries to register with invalid email format
        - User tries to register with passwords shorter than 6 characters
        - User tries to register with empty names and long names (first & last names)
        - Users successfully register
        - New user tries to register with another user's email
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
