''' Test file for auth.py '''
import pytest
from auth import auth_login, auth_logout, auth_register
from channels import channels_create
from error import InputError, AccessError
from other import clear

def test_register_email_invalid():
    '''
    Testing invalid email formats for auth_register
    '''
    clear()
    with pytest.raises(InputError):
        auth_register('', 'password', 'Ben', 'Bill')
    with pytest.raises(InputError):
        auth_register('abcgmail.com', 'password', 'Pen', 'Pill')
    with pytest.raises(InputError):
        auth_register('TESTING@GMAIL.COM', 'password', 'FIRST', 'LAST')
    with pytest.raises(InputError):
        auth_register('TESTING@gmail.com', 'password', 'FIRST', 'Last')
    with pytest.raises(InputError):
        auth_register('@ndrew@gm@il.com', 'password', 'Oops', 'Forgot')
    with pytest.raises(InputError):
        auth_register('5#$%@gmail.com', 'password', 'Special', 'Snowflake')
    with pytest.raises(InputError):
        auth_register('domain@email.long', 'password', 'Haha', 'Unless')
    with pytest.raises(InputError):
        auth_register('shouldbevalid@yahoo.com.au', 'password', 'Champ', 'Chimp')
    with pytest.raises(InputError):
        auth_register('@gmail.com', 'password', 'Nameis', 'Mia')
    with pytest.raises(InputError):
        auth_register('d.o.t@double.com', 'password', 'Double', 'Dot')

def test_register_email_valid():
    '''
    Testing valid email formats for auth_register
    '''
    clear()
    long_email = "abcdefghijklmnopqrstuvwxyz@gmail.com"
    auth_register(long_email, 'password', 'Stephen', 'Long')
    long_domain = 'abc@alsdkjfhadslkfhsdajkfasdfdsadfadsadfdsf.com'
    auth_register(long_domain, 'password', 'First', 'Last')
    auth_register('test@gmail.com', 'password', 'Generic', 'Name')
    auth_register('idk123@yahoo.com', 'password', 'Anonymous', 'Unknown')
    auth_register('email@example.co', 'password', 'Forgotten', 'Surname')
    auth_register('5py@unitedstates.ru', 'gudpassword', 'Donald', 'Trump')

def test_register_existing_email():
    '''
    Testing already taken emails for auth_register
    '''
    clear()
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
    assert auth_logout(user1['token'])['is_success'] is True
    # Trying to register using user 1's email if user 1 is logged out
    with pytest.raises(InputError):
        auth_register(user1_email, 'sample', 'Agent', 'Unknown')

def test_register_password_invalid():
    '''
    Testing invalid passwords for auth_register
    '''
    clear()
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

def test_register_password_valid():
    '''
    Testing valid passwords for auth_register
    '''
    clear()
    auth_register('google@google.co', '123456', 'IveRun', 'OfNames')
    pwd = "aaaaaaaaa@@@@@@@@@@@@aaaaaaaaaaaaa@@@@@@@@@@@aaaaaaaaaaa"
    auth_register('user@seaworld.com', pwd, 'Steven', 'Long')
    auth_register('nemo@finding.com', 'password', 'Secure', 'Pwd')
    auth_register('email@sample.cn', 'V3ryS#cuR3', 'Forgot', 'Password')
    auth_register('empty@space.com', '      ', 'Limit', 'Testing')
    auth_register('seven@seven.com', '1234567', 'S7v7n', 'Teen')

def test_register_name_invalid():
    '''
    Testing invalid first and last names for auth_register
    '''
    clear()
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
    # Empty name
    with pytest.raises(InputError):
        auth_register('valid@email.com', 'password', '   ', 'Last')
    with pytest.raises(InputError):
        auth_register('valid@email.com', 'password', 'First', '    ')

def test_register_name_valid():
    '''
    Testing valid first and last names for auth_register
    '''
    clear()
    auth_register('bob@gmail.com', 'password', 'Just', 'bob')
    auth_register('cc@gmail.com', 'password', 'c', 'c')
    auth_register('num@gmail.com', 'password', '1', '23')
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


def test_login_email_invalid():
    '''
    Testing invalid emails for auth_login
    '''
    clear()
    with pytest.raises(InputError):
        auth_login('!@#$@gmail.com', 'password')
    with pytest.raises(InputError):
        auth_login('invalid@invalid.invalid', 'password')
    with pytest.raises(InputError):
        auth_login('', 'password')

def test_login_unregistered_email():
    '''
    Testing unregistered emails for auth_login
    '''
    clear()
    with pytest.raises(InputError):
        auth_login('admin@gmail.com', 'password')
    with pytest.raises(InputError):
        auth_login('unknown@gmail.com', 'password')
    auth_register('registered@gmail.com', 'password', 'Registered', 'User')
    with pytest.raises(InputError):
        auth_login('unregistered@gmail.com', 'password')
    with pytest.raises(InputError):
        auth_login('google@gmail.com', 'password')

def test_login_incorrect_password():
    '''
    Testing incorrect passwords for auth_login
    '''
    clear()
    auth_register('user1@gmail.com', 'iuser1', 'User', 'One')
    with pytest.raises(InputError):
        auth_login('user1@gmail.com', 'iuserone')
    with pytest.raises(InputError):
        auth_login('user1@gmail.com', 'user 1')
    with pytest.raises(InputError):
        auth_login('user1@gmail.com', 'user1 ')
    with pytest.raises(InputError):
        auth_login('user1@gmail.com', 'iUser1')
    with pytest.raises(InputError):
        auth_login('user1@gmail.com', '')
    auth_register('user2@gmail.com', 'iuser2', 'User', 'Two')
    with pytest.raises(InputError):
        auth_login('user1@gmail.com', 'user2')
    with pytest.raises(InputError):
        auth_login('user2@gmail.com', 'user1')

def test_login_success():
    '''
    Testing successful auth_login
    '''
    clear()
    auth_register('user1@gmail.com', 'iuser1', 'User', 'One')
    auth_login('user1@gmail.com', 'iuser1')
    auth_register('user2@gmail.com', 'iuser2', 'User', 'Two')
    auth_register('user3@gmail.com', 'iuser3', 'User', 'Three')
    auth_login('user3@gmail.com', 'iuser3')
    auth_login('user2@gmail.com', 'iuser2')
    # Assume login works even if user already logged in
    auth_login('user1@gmail.com', 'iuser1')


def test_logout_invalid_token():
    '''
    Testing invalid tokens for auth_logout
    '''
    clear()
    # User not logged in
    with pytest.raises(AccessError):
        auth_logout('weirdtokenthatdoesntexistyet')
    token = auth_register('test@user.com', 'password', 'Test', 'Tube')['token']
    with pytest.raises(AccessError):
        auth_logout('')
    with pytest.raises(AccessError):
        auth_logout('RANDOMTOKEN')
    with pytest.raises(AccessError):
        auth_logout('invalid' + token + 'randompadding123')
    with pytest.raises(AccessError):
        auth_logout(' ' + token)

def test_logout_success():
    '''
    Testing successful auth_logout
    '''
    clear()
    # Logout from register token
    user1 = auth_register('test1@gmail.com', 'password', 'Testing', '123')
    assert auth_logout(user1['token'])['is_success'] is True
    # Logout from login token
    user2 = auth_register('test2@gmail.com', 'password', 'User', 'Two')
    user2 = auth_login('test2@gmail.com', 'password')
    assert auth_logout(user2['token'])['is_success'] is True
    # After logging in again
    user2 = auth_login('test2@gmail.com', 'password')
    assert auth_logout(user2['token'])['is_success'] is True
    user1 = auth_login('test1@gmail.com', 'password')
    assert auth_logout(user1['token'])['is_success'] is True
    # User now unable to use token normally
    with pytest.raises(AccessError):
        channels_create(user1['token'], 'Test Channel', True)
    with pytest.raises(AccessError):
        channels_create(user2['token'], 'Test Channel', True)
    with pytest.raises(AccessError):
        auth_logout(user1['token'])
    with pytest.raises(AccessError):
        auth_logout(user2['token'])

def test_token_tampering():
    clear()
    # Assumes token is JWT-encoded
    user1_token = auth_register('admin@gmail.com', 'password', 'User', 'One')['token']
    user1_payload = user1_token.split('.')[1]
    user2_token = auth_register('test@gmail.com', 'password', 'User', 'One')['token']
    user2_token_components = user2_token.split('.')
    # User 2 tries to sign in with token including User 1's payload
    fake_user1_token_components = user2_token_components
    fake_user1_token_components[1] = user1_payload
    fake_user1_token = '.'.join(fake_user1_token_components)
    with pytest.raises(AccessError):
        channels_create(fake_user1_token, 'Attempt', True)
