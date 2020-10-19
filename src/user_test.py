'''
Tests written to test user.py
'''
import pytest
from user import user_profile
from other import clear
from auth import auth_register
from error import InputError, AccessError

def test_valid_user():
    '''
    Create a valid user
    Return the user detail associated with
    given token and u_id
    '''
    # standard user
    user = auth_register('stvnnguyen69@hotmail.com', 'password', 'Steven', 'Nguyen')
    user_profile = user_profile(user['token'], user['u_id'])
    assert user_profile['user']['name_first'] == "Steven"
    assert user_profile['user']['name_last'] == "Nguyen"
    assert user_profile['user']['u_id'] == 1
    assert user_profile['user']['email'] == 'stvnnguyen69@hotmail.com'
    assert user_profile['user']['handle'] == '1stevennguyen'

    # user with long name
    user2 = auth_register('madeulook100@gmail.com', 'madeulook', 'Verylongfirstname', 'Verylonglastname')
    user_profile = user_profile(user2['token'], user2['u_id'])
    assert user_profile['user']['name_first'] == "Verylongfirstname"
    assert user_profile['user']['name_last'] == "Verylonglastname"
    assert user_profile['user']['u_id'] == 2
    assert user_profile['user']['email'] == 'madeulook100@gmail.com'
    assert user_profile['user']['handle'] == '2verylongfirstnameve'

    clear()

def test_invalid_user():
    '''
    Returns invalid user
    when providing token and u_id that has not been
    created yet
    '''
    # retrieving information without registering
    with pytest.raises(AccessError):
        user_profile('@#*&$^', 11)
    with pytest.raises(AccessError):
        user_profile(')(!*#$', 12)
    with pytest.raises(AccessError):
        user_profile('*%&^', 13)

    # retrieving information with correct token but wrong id
    user = auth_register('shortemail@gmail.com', '1234567', 'Michael', 'Jackson')
    user2 = auth_register('ilovescience10@hotmail.com', '7654321', 'Bill', 'Nye')
    user3 = auth_register('roariscool64@gmail.com', 'password123', 'Taylor', 'Series')
    with pytest.raises(AccessError):
        # actual id is 1
        user_profile(user['token'], 5)
    with pytest.raises(AccessError):
        # actual id is 2
        user_profile(user2['token'], 7)
    with pytest.raises(AccessError):
        # actual id is 3
        user_profile(user3['token'], 7)

    # retrieving information with wrong token but correct id
    with pytest.raises(AccessError):
        user_profile('@#*&$^', 1)
    with pytest.raises(AccessError):
        user_profile(')(!*#$', 2)
    with pytest.raises(AccessError):
        user_profile('*%&^', 3)

    clear()

# user_profile_setemail(token, email) tests
def test_empty_email():
    '''
    
    
    '''
    pass

def test_invalid_email():
    pass

# user_profile_sethandle(token, handle_str) tests
def test_handle_length():
    pass

def test_taken_handle():    
    pass