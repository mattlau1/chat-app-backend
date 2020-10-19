from error import InputError, AccessError
from data import valid_email
def user_profile(token, u_id):
    return {
        'user': {
        	'u_id': 1,
        	'email': 'cs1531@cse.unsw.edu.au',
        	'name_first': 'Hayden',
        	'name_last': 'Jacobs',
        	'handle_str': 'hjacobs',
        },
    }

def user_profile_setname(token, name_first, name_last):
    return {
    }

def user_profile_setemail(token, email):
    if not valid_email(email):
        # Invalid email format
        raise InputError('Invalid email format')

    return {
    }

def user_profile_sethandle(token, handle_str):
    return {
    }