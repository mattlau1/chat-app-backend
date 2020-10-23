import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json

# Use this fixture to get the URL of the server.
@pytest.fixture
def url():
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "server.py"], stderr=PIPE, stdout=PIPE)
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

# IMPLEMENT TEST FUNCTIONS HERE


# user_profile tests
def test_valid_user():
    '''
    Create a valid user
    Return the user detail associated with
    given token and u_id
    '''
    requests.post(url + reset)
    
    # auth_register IS SUBJECTED TO CHANGE WITH REQUESTS
    user = auth_register('stvnnguyen69@hotmail.com', 'password', 'Steven', 'Nguyen')
    requests.put(url+"profile/sethandle", params = {'token': user['token'],'handle_str': 'Stevenson'})
    r = requests.get(url+"profile", params = {'token': user['token'],'u_id': user['u_id']})
    profile = r.json()
    assert profile['user']['name_first'] == "Steven"
    assert profile['user']['name_last'] == "Nguyen"
    assert profile['user']['u_id'] == user['u_id']
    assert profile['user']['email'] == 'stvnnguyen69@hotmail.com'
    assert profile['user']['handle_str'] == 'Stevenson'

def test_invalid_user():
    '''
    Raise exception when providing token and u_id that has not been created yet.
    Create valid users but call user detail with incorrrect u_id and token
    '''
    requests.post(url + reset)

    # access user details without registering
    with pytest.raises(AccessError):
        requests.get(url+"profile", params = {'tokens': "&73hf(s!)@",'u_id': 42})
    with pytest.raises(AccessError):
        requests.get(url+"profile", params = {'tokens': "12js*sj21$$",'u_id': 24})
    with pytest.raises(AccessError):
        requests.get(url+"profile", params = {'tokens': "notAtoken",'u_id': 666})

    # retrieving information with correct token but wrong id
    user = auth_register('andrewwashere@outlook.com', '0987654321', 'Andrew', 'Andrewson')
    r = requests.get(url+"profile", params = {'token': user['token'],'u_id': user['u_id']})
    profile = r.json()
    with pytest.raises(InputError):
        user_profile(user['token'], 34)

    # retrieving information with wrong token but correct id
    with pytest.raises(AccessError):
        user_profile('@#*&$^', user['u_id'])

# user_profile_setname tests
def test_valid_setnames():
    
    requests.post(url + reset)

    user = auth_register('stvnnguyen69@hotmail.com', 'password', 'Steven', 'Nguyen')
    requests.put(url+"profile/sethandle", params = {'token': user['token'],'handle_str': 'Stevenson'})
    r = requests.get(url+"profile", params = {'token': user['token'],'u_id': user['u_id']})