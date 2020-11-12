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
## HTTP user ##
###############
def test_http_user_profile(url):
    '''
    HTTP test for user_profile
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Registering valid user
    resp = requests.post(url + 'auth/register', json={
        'email': 'stvnnguyen69@hotmail.com',
        'password': 'password',
        'name_first': 'Steven',
        'name_last': 'Nguyen',
    })
    assert resp.status_code == 200
    user = resp.json()

    resp = requests.put(url+"user/profile/sethandle", json={
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

    # Access user details without registering
    resp = requests.get(url+"user/profile", params={
        'tokens': "&73hf(s!)@",
        'u_id': 42
    })

    assert resp.status_code == 400

    # Retrieving information with correct token but wrong id
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

    # Create user
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

    # Check original name
    assert profile['user']['name_first'] == "John"
    assert profile['user']['name_last'] == "Johnson"
    assert profile['user']['u_id'] == user['u_id']

    # Change setname
    requests.put(url+'user/profile/setname', json={
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

    # Check new set name
    assert profile['user']['name_first'] == "Monkey"
    assert profile['user']['name_last'] == "Monkeyson"
    assert profile['user']['u_id'] == user['u_id']

    # Change name again with 1 character
    resp = requests.put(url+'user/profile/setname', json={
        'token': user['token'],
        'name_first': 'A',
        'name_last': 'B'
    })
    assert resp.status_code == 200
    
    resp = requests.get(url+"user/profile", params={
        'token': user['token'],
        'u_id': user['u_id']
    })

    assert resp.status_code == 200
    profile = resp.json()

    # Check new set name
    assert profile['user']['name_first'] == "A"
    assert profile['user']['name_last'] == "B"
    assert profile['user']['u_id'] == user['u_id']

    # Change name again with exactly 50 characters
    long_first = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    long_last = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'
    
    resp = requests.put(url+'user/profile/setname', json={
        'token': user['token'],
        'name_first': long_first,
        'name_last': long_last
    })
    assert resp.status_code == 200

    resp = requests.get(url+"user/profile", params={
        'token': user['token'],
        'u_id': user['u_id']
    })

    assert resp.status_code == 200
    profile = resp.json()

    assert profile['user']['name_first'] == long_first
    assert profile['user']['name_last'] == long_last
    assert profile['user']['u_id'] == user['u_id']

    # Change into empty name
    resp = requests.put(url+'user/profile/setname', json={
        'token': user['token'],
        'name_first': '',
        'name_last': ''
    })
    assert resp.status_code == 400

    # Change into 51 characters
    long_first = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxa'
    long_last = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyb'
    resp = requests.put(url+'user/profile/setname', json={
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

    # Registering valid user
    resp = requests.post(url + 'auth/register', json={
        'email': 'stvnnguyen69@hotmail.com',
        'password': 'password',
        'name_first': 'Steven',
        'name_last': 'Nguyen',
    })
    assert resp.status_code == 200
    user = resp.json()

    # Get user profile
    resp = requests.get(url+"user/profile", params={
        'token': user['token'],
        'u_id': user['u_id']
    })
    assert resp.status_code == 200
    profile = resp.json()

    # Check original email
    assert profile['user']['email'] == 'stvnnguyen69@hotmail.com'

    # Set new email
    requests.put(url+"user/profile/setemail", json={
        'token': user['token'],
        'email': 'stevennguyen22@gmail.com'
    })

    # Get user profile
    resp = requests.get(url+"user/profile", params={
        'token': user['token'],
        'u_id': user['u_id']
    })
    assert resp.status_code == 200
    profile = resp.json()

    # Check if email has changed
    assert profile['user']['email'] == 'stevennguyen22@gmail.com'

    # SETTING INVALID EMAIL

    # Register valid user
    resp = requests.post(url + 'auth/register', json={
        'email': 'andrewwashere@outlook.com',
        'password': '0987654321',
        'name_first': 'Andrew',
        'name_last': 'Andrewson',
    })
    assert resp.status_code == 200
    user = resp.json()

    # Set invalid email
    resp = requests.put(url+"user/profile/setemail", json={
        'token': user['token'],
        'email': 'steve.apple@'
    })

    assert resp.status_code == 400

    # EMAIL ADDRESS TAKEN

    # Register two valid users
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

    # Set valid email for user 1
    resp = requests.put(url+"user/profile/setemail", json={
        'token': user1['token'],
        'email': 'monkey@gmail.com'
    })
    assert resp.status_code == 200

    # Set user 2's email to user1's email (should be taken)
    resp = requests.put(url+"user/profile/setemail", json={
        'token': user2['token'],
        'email': 'monkey@gmail.com'
    })
    assert resp.status_code == 400

    # Get user 1's profile
    resp = requests.get(url+"user/profile", params={
        'token': user1['token'],
        'u_id': user1['u_id']
    })
    assert resp.status_code == 200
    profile1 = resp.json()

    # Get user2's profile
    resp = requests.get(url+"user/profile", params={
        'token': user2['token'],
        'u_id': user2['u_id']
    })
    assert resp.status_code == 200
    profile2 = resp.json()

    # Make sure user1's email has changed
    assert profile1['user']['email'] == 'monkey@gmail.com'

    # Make sure user2's email is unchanged
    assert profile2['user']['email'] == 'zippy@hotmail.com'


def test_http_user_profile_sethandle(url):
    '''
    HTTP test for user_profile_sethandle
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # SET VALID HANDLE

    # Registering valid user
    resp = requests.post(url + 'auth/register', json={
        'email': 'stvnnguyen69@hotmail.com',
        'password': 'password',
        'name_first': 'Steven',
        'name_last': 'Nguyen',
    })
    assert resp.status_code == 200
    user = resp.json()

    # Set new handle
    resp = requests.put(url+"user/profile/sethandle", json={
        'token': user['token'],
        'handle_str': 'Stevenson'
    })
    assert resp.status_code == 200

    # Get user profile
    resp = requests.get(url+"user/profile", params={
        'token': user['token'],
        'u_id': user['u_id']
    })
    assert resp.status_code == 200
    profile = resp.json()

    # Check new handle
    assert profile['user']['handle_str'] == 'Stevenson'

    # SET INVALID HANDLE LENGTH

    # Register valid user
    resp = requests.post(url + 'auth/register', json={
        'email': 'andrewwashere@outlook.com',
        'password': '0987654321',
        'name_first': 'Andrew',
        'name_last': 'Andrewson',
    })
    assert resp.status_code == 200
    user = resp.json()

    # Set invalid short handle
    resp = requests.put(url+"user/profile/sethandle", json={
        'token': user['token'],
        'handle_str': 'AA'
    })
    assert resp.status_code == 400

    # Set invalid long handle
    resp = requests.put(url+"user/profile/sethandle", json={
        'token': user['token'],
        'handle_str': 'thisistwentyonechars!'
    })
    assert resp.status_code == 400

    # HANDLE TAKEN

    # Register two valid users
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

    # User 1 changes handle
    resp = requests.put(url+"user/profile/sethandle", json={
        'token': user1['token'],
        'handle_str': 'Banana'
    })
    assert resp.status_code == 200

    # User 2 also changes handle
    resp = requests.put(url+"user/profile/sethandle", json={
        'token': user2['token'],
        'handle_str': 'Apple'
    })
    assert resp.status_code == 200

    # User 2 tries to take user1's handle (should be taken)
    resp = requests.put(url+"user/profile/sethandle", json={
        'token': user2['token'],
        'handle_str': 'Banana'
    })
    assert resp.status_code == 400

    # Get user1's profile
    resp = requests.get(url+"user/profile", params={
        'token': user1['token'],
        'u_id': user1['u_id']
    })
    assert resp.status_code == 200
    profile1 = resp.json()

    # Get user2's profile
    resp = requests.get(url+"user/profile", params={
        'token': user2['token'],
        'u_id': user2['u_id']
    })
    assert resp.status_code == 200
    profile2 = resp.json()

    # Make sure user1's handle has changed
    assert profile1['user']['handle_str'] == 'Banana'

    # Make sure user2's handle isn't the same as user1's
    assert profile2['user']['handle_str'] == 'Apple'


def test_http_user_profile_uploadphoto(url):
    '''
    HTTP test for user_profile_uploadphoto
    '''
    assert requests.delete(url + 'clear').status_code == 200

    # Registering valid user
    resp = requests.post(url + 'auth/register', json={
        'email': 'stvnnguyen69@hotmail.com',
        'password': 'password',
        'name_first': 'Steven',
        'name_last': 'Nguyen',
    })
    assert resp.status_code == 200
    user = resp.json()


