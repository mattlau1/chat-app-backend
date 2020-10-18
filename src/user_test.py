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

def test_invalid_user();
    '''
    Returns invalid user
    when providing token and u_id that has not been
    created yet
    '''
    pass

