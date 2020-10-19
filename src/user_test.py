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
    user = auth_register('stvnnguyen69@hotmail.com', 'password', 'Steven', 'Nguyen')
    pass

def test_invalid_user():
    '''
    Returns invalid user
    when providing token and u_id that has not been
    created yet
    '''
    pass

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