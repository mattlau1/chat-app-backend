# Test file for auth.py
import pytest
from auth import auth_login, auth_logout, auth_register
from error import InputError, AccessError
from other import clear

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

# Test valid passwords
def test_register_password_valid():
    auth_register('google@google.co', '123456', 'IveRun', 'OfNames')
    pwd = "aaaaaaaaa@@@@@@@@@@@@aaaaaaaaaaaaa@@@@@@@@@@@aaaaaaaaaaa"
    auth_register('user@seaworld.com', pwd, 'Steven', 'Long')
    auth_register('nemo@finding.com', 'password', 'Secure', 'Pwd')
    auth_register('email@sample.cn', 'V3ryS#cuR3', 'Forgot', 'Password')
    clear()


# Todo:

####################
# Test name length #
####################

# Test login and logout with different tokens



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


