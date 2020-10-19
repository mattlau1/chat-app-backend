'''
Tests written to test user.py
'''
import pytest
from user import (
    user_profile, user_profile_setname,
    user_profile_setemail, user_profile_sethandle,
)
from other import clear
from auth import auth_register
from error import InputError, AccessError

# user_profile tests
def test_valid_user():
    '''
    Create a valid user
    Return the user detail associated with
    given token and u_id
    '''
    clear()
    # standard user
    user = auth_register('stvnnguyen69@hotmail.com', 'password', 'Steven', 'Nguyen')
    profile = user_profile(user['token'], user['u_id'])
    assert profile['user']['name_first'] == "Steven"
    assert profile['user']['name_last'] == "Nguyen"
    assert profile['user']['u_id'] == 1
    assert profile['user']['email'] == 'stvnnguyen69@hotmail.com'
    assert profile['user']['handle'] == '1stevennguyen'

    # user with long name to check handle name
    user2 = auth_register(
        'madeulook100@gmail.com', 'madeulook',
        'Verylongfirstname', 'Verylonglastname'
    )
    profile = user_profile(user2['token'], user2['u_id'])
    assert profile['user']['name_first'] == "Verylongfirstname"
    assert profile['user']['name_last'] == "Verylonglastname"
    assert profile['user']['u_id'] == 2
    assert profile['user']['email'] == 'madeulook100@gmail.com'
    assert profile['user']['handle'] == '2verylongfirstnameve'

def test_invalid_user():
    '''
    Raise exception when providing token and u_id that has not been created yet.
    Create valid users but call user detail with incorrrect u_id and token
    '''
    clear()
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

# user_profile_setname tests
def test_valid_setnames():
    '''
    Change name of the user with valid name and check that the id stays the same
    Use edge case to change into new name such as 1 character or exactly 50 characters
    '''
    clear()
    # original user
    user = auth_register('blastfire97@gmail.com', 'p@ssw0rd', 'Apple', 'Appleson')
    profile = user_profile(user['token'], user['u_id'])
    assert profile['user']['name_first'] == "Apple"
    assert profile['user']['name_last'] == "Appleson"
    assert profile['user']['u_id'] == 1

    # same token, id but different username
    user_profile_setname(user['token'], 'Banana', 'Bananason')
    assert profile['user']['name_first'] == "Banana"
    assert profile['user']['name_last'] == "Bananason"
    assert profile['user']['u_id'] == 1

    # change name multiple times under the same token
    user2 = auth_register('samsunggalaxy01@gmail.com', 'password', 'Orange', 'Orangeson')
    profile = user_profile(user2['token'], user2['u_id'])
    assert profile['user']['name_first'] == "Orange"
    assert profile['user']['name_last'] == "Orangeson"
    assert profile['user']['u_id'] == 2
    user_profile_setname(user2['token'], 'Strawberry', 'Strawberryson')
    assert profile['user']['name_first'] == "Strawberry"
    assert profile['user']['name_last'] == "Strawberryson"
    assert profile['user']['u_id'] == 2
    user_profile_setname(user2['token'], 'Michael', 'Michaelson')
    assert profile['user']['name_first'] == "Michael"
    assert profile['user']['name_last'] == "Michaelson"
    assert profile['user']['u_id'] == 2

    # changing name with 1 character
    user3 = auth_register('mmmonkey97@hotmail.com', 'password', 'John', 'Johnson')
    profile = user_profile(user3['token'], user3['u_id'])
    assert profile['user']['name_first'] == "John"
    assert profile['user']['name_last'] == "Johnson"
    user_profile_setname(user3['token'], "A", "B")
    assert profile['user']['name_first'] == "A"
    assert profile['user']['name_last'] == "B"

    # changing name with exactly 50 characters
    long_first = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    long_last = 'yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy'
    user4 = auth_register('austinnistau@hotmai.com', 'password', 'Austin', 'Austinson')
    profile = user_profile(user4['token'], user4['u_id'])
    assert profile['user']['name_first'] == "Austin"
    assert profile['user']['name_last'] == "Austinson"
    user_profile_setname(user4['token'], long_first, long_last)
    assert profile['user']['name_first'] == long_first
    assert profile['user']['name_last'] == long_last

def test_invalid_setnames():
    '''
    Raise exception when changing the name of user using invalid format
    such as names with more than 50 characers long, empty name and empty spaces
    '''
    clear()
    # changing name to more than 50 characters long
    long_first = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    long_last = 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
    user = auth_register('hardcoregamer02@hotmail.com', 'password', 'Raymond', 'Raymondson')
    profile = user_profile(user['token'], user['u_id'])
    assert profile['user']['name_first'] == "Raymond"
    assert profile['user']['name_last'] == "Raymondson"
    with pytest.raises(InputError):
        user_profile_setname(user['token'], long_first, long_last)

    # changing name with empty space
    user2 = auth_register('mmmonkey97@hotmail.com', 'password', 'John', 'Johnson')
    profile = user_profile(user2['token'], user2['u_id'])
    with pytest.raises(InputError):
        user_profile_setname(user2['token'], '', '')
    with pytest.raises(InputError):
        user_profile_setname(user2['token'], '  ', '  ')

# user_profile_setemail tests
def test_valid_email():
    '''
    Registers a user and sets their email to a valid email.
    '''
    clear()
    user = auth_register('hellothere44@gmail.com', 'ifajfiod1ad133', 'Matthew', 'Matthewson')
    profile = user_profile(user['token'], user['u_id'])

    # Check if email is still the same
    assert profile['user']['email'] == 'hellothere44@gmail.com'

    # Change user's email
    user_profile_setemail(user['token'], 'goodbye21@gmail.com')

    # Check if email has changed
    assert profile['user']['email'] == 'goodbye21@gmail.com'

def test_invalid_email():
    '''
    Registers valid users and attempts to change their email to strings
    that aren't emails.
    '''
    clear()
    user = auth_register('ilovescience10@hotmail.com', '7654321', 'Bill', 'Nye')

    # Alphanumeric string, no @ or domain
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], 'dkid12eid')

    # Alphanumeric string with @
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], 'ew9ijifewji90ejwiffjiifji1j2j@')

    # No string with @ and domain
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], '@.com')

    # No string or @ with domain
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], 'gmail.cn')

    # No string with @
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], '@')

def test_empty_email():
    '''
    Registers valid users and attempts to change their email to an empty email
    or one with whitespace only.
    '''
    clear()
    # Setting empty email
    user = auth_register('stvnnguyen69@hotmail.com', 'password', 'Steven', 'Nguyen')
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], '')

    # Setting email full of whitespaces
    user = auth_register('shortemail@gmail.com', '1234567', 'Michael', 'Jackson')
    with pytest.raises(InputError):
        user_profile_setemail(user['token'], '          ')

def test_taken_email():
    '''
    Registers two valid users and tries to set both their emails to each other's
    emails.
    '''
    clear()
    user1 = auth_register('blastfire97@gmail.com', 'p@ssw0rd', 'Apple', 'Appleson')
    user2 = auth_register('samsunggalaxy01@gmail.com', 'password', 'Orange', 'Orangeson')

    # user1 tries to set email to user2's email
    with pytest.raises(InputError):
        user_profile_setemail(user1['token'], 'samsunggalaxy01@gmail.com')

    # user2 tries to set email to user1's email
    with pytest.raises(InputError):
        user_profile_setemail(user2['token'], 'blastfire97@gmail.com')

def test_same_email():
    '''
    Registers two users and tries to set their emails to their current emails.
    '''
    clear()
    user1 = auth_register('mmmonkey97@hotmail.com', 'password', 'John', 'Johnson')
    with pytest.raises(InputError):
        user_profile_setemail(user1['token'], 'mmmonkey97@hotmail.com')

    user2 = auth_register('monkeymaster22@gmail.com', 'ilovebanaNas', 'Banana', 'Bananason')
    with pytest.raises(InputError):
        user_profile_setemail(user2['token'], 'monkeymaster22@gmail.com')

# user_profile_sethandle tests
def test_valid_handle():
    '''
    User registers and changes handle to normal handle
    '''
    clear()
    user = auth_register('therealbrucelee@gmail.com', 'gghgdshh', 'Bruce', 'Lee')
    profile = user_profile(user['token'], user['u_id'])

    user_profile_sethandle(user['token'], 'Real Bruce Lee')
    assert profile['user']['handle'] == 'Real Bruce Lee'

    user_profile_sethandle(user['token'], 'Actual Bruce Lee')
    assert profile['user']['handle'] == 'Actual Bruce Lee'

def test_handle_length():
    '''
    User registers and tries to change handle to 2 character and 27 character
    handles.
    '''
    clear()
    user = auth_register('peterpeterson222@hotmail.com', 'uaefhuasfnf', 'Peter', 'Peterson')
    profile = user_profile(user['token'], user['u_id'])

    # User tries to change to short handle
    with pytest.raises(InputError):
        user_profile_sethandle(user['token'], 'hi')

    # User tries to change to long handle
    with pytest.raises(InputError):
        user_profile_sethandle(user['token'], 'thisistwentyonechars!')

    # Make sure handle is still the same (default handle)
    user_profile_sethandle(user['token'], 'dog')
    assert len(profile['user']['handle']) == 3

def test_taken_handle():
    '''
    Two users register and try to change to the same valid handle.
    '''
    clear()
    user1 = auth_register('blastfire97@gmail.com', 'p@ssw0rd', 'Apple', 'Appleson')
    user2 = auth_register('samsunggalaxy01@gmail.com', 'password', 'Orange', 'Orangeson')

    # user1 changes handle to hello world
    user_profile_sethandle(user1['token'], 'hello world')

    # user2 tries to also change to hello world
    with pytest.raises(InputError):
        user_profile_sethandle(user2['token'], 'hello world')

    # user1 changes handle again
    user_profile_sethandle(user2['token'], 'goodbye world')

    with pytest.raises(InputError):
        user_profile_sethandle(user1['token'], 'goodbye world')
