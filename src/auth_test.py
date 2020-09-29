# Test file for auth.py
import pytest
from auth import auth_login, auth_logout, auth_register
from error import InputError, AccessError
from other import clear

""" Tests for auth_register """

# Invalid email format
def test_register_email_invalid():
    with pytest.raises(InputError):
        auth_register('', 'password', 'Ben', 'Bill')
    with pytest.raises(InputError):
        auth_register('abcgmail.com', 'password', 'Pen', 'Pill')
    with pytest.raises(InputError):
        auth_register('TESTING@GMAIL.COM', 'password', 'First', 'Last')
    with pytest.raises(InputError):
        auth_register('@ndrew@gm@il.com', 'password', 'Oops', 'Forgot')
    with pytest.raises(InputError):
        auth_register('domain@email.long', 'password', 'Haha', 'Unless')
    with pytest.raises(InputError):
        auth_register('shouldbevalid@yahoo.com.au', 'password', 'Champ', 'Chimp')
    with pytest.raises(InputError):
        auth_register('@gmail.com', 'password', 'Nameis', 'Mia')
    clear()

# Valid email format
def test_register_email_valid():
    long_email = "abcdefghijklmnopqrstuvwxyz@gmail.com"
    auth_register(long_email, 'password', 'Stephen', 'Long')
    long_domain = 'abc@alsdkjfhadslkfhsdajkfasdfdsadfadsadfdsf.com'
    auth_register(long_domain, 'password', 'First', 'Last')
    auth_register('test@gmail.com', 'password', 'Generic', 'Name')
    auth_register('idk123@yahoo.com', 'password', 'Anonymous', 'Unknown')
    auth_register('email@example.co', 'password', 'Forgotten', 'Surname')
    auth_register('5py@unitedstates.ru', 'gudpassword', 'Donald', 'Trump')
    clear()

# Email already in use
def test_register_existing_email():
    # Successfully register user 1
    user1_email = "test@gmail.com"
    user1_password = "password"
    auth_register(user1_email, user1_password, 'User', 'One')
    # Try to register user 2 using user 1's email
    user2_password = "password123"
    with pytest.raises(InputError):
        # Try to register user 2 using user 1's email
        auth_register(user1_email, user2_password, 'User', 'Two')
    with pytest.raises(InputError):
        # Trying to login to email using user 2's password
        auth_login(user1_email, user2_password)
    # Login with user 1's email using user 1's password should work
    user1 = auth_login(user1_email, user1_password)
    # Testing logged out user 1
    assert auth_logout(user1['token'])['is_success'] == True
    # Trying to register using user 1's email if user 1 is logged out
    with pytest.raises(InputError):
        auth_register(user1_email, 'sample', 'Agent', 'Unknown')
    clear()

# Test invalid passwords
def test_register_password_invalid():
    with pytest.raises(InputError):
        auth_register('google@gmail.com', '12345', 'Bob', 'Chen')
    with pytest.raises(InputError):
        auth_register('yahoo@yahoo.com', '1234 ', 'Bob', 'Bob')
    with pytest.raises(InputError):
        auth_register('bing@bing.com', '', 'Just', 'Bob')
    with pytest.raises(InputError):
        auth_register('spaced@out.com', ' ', 'Spaced', 'Out')
    with pytest.raises(InputError):
        auth_register('valid@email.com', 'pass', 'Whois', 'Bob')
    clear()

# Test valid passwords
def test_register_password_valid():
    auth_register('google@google.co', '123456', 'IveRun', 'OfNames')
    pwd = "aaaaaaaaa@@@@@@@@@@@@aaaaaaaaaaaaa@@@@@@@@@@@aaaaaaaaaaa"
    auth_register('user@seaworld.com', pwd, 'Steven', 'Long')
    auth_register('nemo@finding.com', 'password', 'Secure', 'Pwd')
    auth_register('email@sample.cn', 'V3ryS#cuR3', 'Forgot', 'Password')
    auth_register('empty@space.com', '      ', 'Limit', 'Testing')
    auth_register('seven@seven.com', '1234567', 'S7v7n', 'Teen')
    clear()

# Test invalid first and last names
def test_register_name_invalid():
    invalid_string1 = ''
    # 52 characters
    invalid_string2 = 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxyz'
    # 51 characters
    invalid_string3 = 'abcdefghijklmnopqrstuvwxyzabcdefghijklmnopqrstuvwxy'
    invalid_string4 = invalid_string3 + invalid_string2
    # Test name_first
    with pytest.raises(InputError):
        auth_register('email@sample.com', 'password', invalid_string1, 'Name')
    with pytest.raises(InputError):
        auth_register('fmail@sample.com', 'password', invalid_string2, 'Name')
    with pytest.raises(InputError):
        auth_register('gmail@sample.com', 'password', invalid_string3, 'Name')
    with pytest.raises(InputError):
        auth_register('hmail@sample.com', 'password', invalid_string4, 'Name')
    # Test name_last
    with pytest.raises(InputError):
        auth_register('imail@sample.com', 'password', 'Name', invalid_string1)
    with pytest.raises(InputError):
        auth_register('jmail@sample.com', 'password', 'Name', invalid_string2)
    with pytest.raises(InputError):
        auth_register('kmail@sample.com', 'password', 'Name', invalid_string3)
    with pytest.raises(InputError):
        auth_register('lmail@sample.com', 'password', 'Name', invalid_string4)
    # Test both
    with pytest.raises(InputError):
        auth_register('mmail@sample.com', 'password', invalid_string1, invalid_string2)
    with pytest.raises(InputError):
        auth_register('femail@sample.com', 'password', invalid_string3, invalid_string4)
    with pytest.raises(InputError):
        auth_register('tmail@sample.com', 'password', invalid_string1, invalid_string1)
    clear()
    
# Test valid first and last names
def test_register_name_valid():
    auth_register('bob@gmail.com', 'password', 'Just', 'bob')
    auth_register('cc@gmail.com', 'password', 'c', 'c')
    valid_string1 = 'c' * 49
    valid_string2 = 'c' * 50
    auth_register('long@gmail.com', 'password', valid_string1, 'Normal')
    auth_register('dragon@gmail.com', 'password', 'Normal', valid_string1)
    auth_register('fire@gmail.com', 'password', valid_string1, valid_string1)
    auth_register('long1@gmail.com', 'password', valid_string2, 'Normal')
    auth_register('dragon1@gmail.com', 'password', 'Normal', valid_string2)
    auth_register('fire1@gmail.com', 'password', valid_string2, valid_string2)
    auth_register('secret@me.com', 'password', 'CryP+1c', 'N4m3')
    auth_register('very@interesting.com', 'password', 'Anne-Marie', 'Sirn@m3')
    auth_register('dot.dot@dot.com', 'password', 'Dot', 'Dot')
    auth_register('sc_re@under.com', 'password', 'Under', 'Score')
    clear()

""" Tests for auth_login """

def test_login_email_invalid():
    pass

def test_login_unregistered_email():
    pass

def test_login_incorrect_password():
    pass

def test_login_success():
    pass

""" Tests for auth_logout """

def test_logout_invalid_token():
    # User not logged in
    pass

def test_logout_success():
    pass

# Random:

def test_valid_auth():
    # User 1
    user1_email = "test@gmail.com"
    user1_password = "password"
    auth_register(user1_email, user1_password, "Ben", "Bill")
    user1 = auth_login(user1_email, user1_password)
    assert auth_logout(user1['token'])['is_success'] == True

def test_invalid_auth():
    # with pytest.raises(InputError):
    pass


