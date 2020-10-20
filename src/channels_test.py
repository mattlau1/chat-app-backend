''' Test file for channels.py '''
import pytest
from channels import channels_list, channels_listall, channels_create
from error import InputError, AccessError
from other import clear
from auth import auth_register

def test_create_long_names():
    '''
    Creating a channel that has more than 20 characters (max length) in name
    '''
    clear()
    user = auth_register('jesschen@gmail.com', 'password', 'Jess', 'Chen')
    long_name = "abcdefghijklmnopqrstuvwxyz"
    with pytest.raises(InputError):
        channels_create(user['token'], long_name, True)
    long_name = "thisnameisverylong000"
    with pytest.raises(InputError):
        channels_create(user['token'], long_name, True)
    long_name = "ijxiqwji9xq9iqdjim9dwq89n189819me781neuensa9xaj9xd"
    with pytest.raises(InputError):
        channels_create(user['token'], long_name, False)

def test_create_empty_name():
    '''
    Creating channels with empty names, public and private
    '''
    clear()
    user = auth_register('user1@gmail.com', 'password1', 'John', 'Smith')
    with pytest.raises(InputError):
        channels_create(user['token'], '', True)
    with pytest.raises(InputError):
        channels_create(user['token'], '', False)

def test_create_whitespace_name():
    '''
    Creating channels with whitespace as name
    '''
    clear()
    user = auth_register('petermichaels@gmail.com', 'password', 'Peter', 'Michaels')
    with pytest.raises(InputError):
        channels_create(user['token'], ' ', True)
    with pytest.raises(InputError):
        channels_create(user['token'], '          ', True)
    with pytest.raises(InputError):
        channels_create(user['token'], '      ', False)
    with pytest.raises(InputError):
        channels_create(user['token'], '    ', True)

def test_hidden_channels():
    '''
    Testing if certain channels are hidden to users
    '''
    clear()
    # User1 makes 3 channels
    user1 = auth_register('stevengaming@gmail.com', 'ilikeapPlEs', 'Steven', 'Stevenson')
    channels_create(user1['token'], 'Private Channel 1', False)
    channels_create(user1['token'], 'Secret Club', False)
    channels_create(user1['token'], 'HIDDEN channel', False)
    assert len(channels_list(user1['token'])['channels']) == 3
    assert len(channels_listall(user1['token'])['channels']) == 3

    # Public channel created, user1 should be able to see all 4
    channels_create(user1['token'], 'Public', True)
    assert len(channels_list(user1['token'])['channels']) == 4

    # New user should only see public channel
    user2 = auth_register('matthew2323@gmail.com', 'idontlikeapples', 'Matthew', 'Matthewson')
    assert len(channels_list(user2['token'])['channels']) == 0
    assert len(channels_listall(user2['token'])['channels']) == 4

    # User2 has 1 channel
    channels_create(user2['token'], 'matthew lair', False)
    assert len(channels_list(user2['token'])['channels']) == 1

    # User1 can still only see 4
    assert len(channels_list(user1['token'])['channels']) == 4

    # There should be a total of 5 channels
    assert len(channels_listall(user2['token'])['channels']) == 5

def test_invalid_tokens():
    '''
    Creating a channel without a valid token
    '''
    clear()
    with pytest.raises(AccessError):
        channels_create("thisisaninvalidtoken", 'steven lair', True)
    with pytest.raises(AccessError):
        channels_create("!)@(#*)!@*", 'steven lair2', False)

    with pytest.raises(AccessError):
        channels_list("anotherinvalidtoken")
    with pytest.raises(AccessError):
        channels_list("!@#(*&%")

    with pytest.raises(AccessError):
        channels_listall("this is not valid")
    with pytest.raises(AccessError):
        channels_listall("!@#* !@(*#&")

def test_create_valid_channels():
    '''
    Creating valid channels
    '''
    clear()
    # User1 creating 3 channels normally
    user1 = auth_register('andrew42421s23@gmail.com', 'thisisagoodpassword', 'Andrew', 'Smith')
    channels_create(user1['token'], "FirstChannel", True)
    channels_create(user1['token'], "UNSW discussion", True)
    channels_create(user1['token'], "Private", False)
    assert len(channels_list(user1['token'])['channels']) == 3
    assert len(channels_listall(user1['token'])['channels']) == 3

    # User2 creating channel
    user2 = auth_register('stevenmatthewson@gmail.com', 'khjsdfiowefh2', 'Steven', 'Matthewson')
    assert len(channels_list(user2['token'])['channels']) == 0
    channels_create(user2['token'], "Steven land", True)
    assert len(channels_list(user2['token'])['channels']) == 1
    assert len(channels_listall(user1['token'])['channels']) == 4

    # User3 creating no channels
    user3 = auth_register('stevensmithson@gmail.com', 'dwfwefhf', 'Steven', 'Smithson')
    assert len(channels_list(user3['token'])['channels']) == 0
