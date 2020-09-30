# Test file for channel.py

from channel import channel_invite, channel_details, channel_messages, channel_leave, channel_join, channel_addowner, channel_removeowner
from channels import channels_create
from auth import auth_register
from error import InputError, AccessError
from other import clear
import pytest

def test():
    pass

def test_channel_addowner():
    owner = auth_register('bobsmith@gmail.com', 'hello', 'Bob', 'Smith')
    work = channels_create(owner['token'], 'work', True)
    user = auth_register('jesschen@gmail.com', 'hello', 'Jess', 'Chen')
    
    # Checking if someone can be added (verified if they can be immediately removed)
    channel_addowner(owner['token'], work['channel_id'], user['u_id'])
    channel_removeowner(owner['token'], work['channel_id'], user['u_id'])

    # Adding someone who is already the owner
    with pytest.raises(InputError):
        channel_addowner(owner['token'], work['channel_id'], user['u_id'])
        channel_addowner(owner['token'], work['channel_id'], user['u_id'])

    # Channel ID is not a valid channel
    with pytest.raises(InputError):
        channel_addowner(owner['token'], work['channel_id'] + 100, user['u_id'])
    
    # Authorised user is not the owner
    with pytest.raises(AccessError):
        channel_addowner(user['token'], work['channel_id'], user['u_id'])

    clear()




def test_channel_removeowner():
    # Checking if someone can be removed (Add then remove)

    # Removing someone who is already removed

    pass


def test_channel_invite():
    user1 = auth_register('user1@gmail.com', 'password1', 'John', 'Smith')
    user2 = auth_register('user2@gmail.com', 'password2', 'Steve', 'Jackson') 
    # User 1 creates a new channel, and invites User 2
    test_channel1 = channels_create(user1['token'], 'Test Channel 1', True)
    channel_invite(user1['token'], test_channel1['channel_id'], user2['u_id'])

    # Checking if User 2 is a member of the channel (by attempting to access channel details through User 2)
    channel_details(user2['token'], test_channel1['channel_id'])
    
    test_channel2 = channels_create(user1['token'], 'Test Channel 2', True)

    # Channel ID does not refer to a valid channel
    with pytest.raises(InputError):
        channel_invite(user1['token'], test_channel2['channel_id'] + 100, user2['u_id'])

    # User ID does not refer to a valid user
    with pytest.raises(InputError):
        channel_invite(user1['token'], test_channel2['channel_id'], user2['u_id'] + 100)

    # Authorised user is not a member of the channel
    with pytest.raises(AccessError):
        user3 = auth_register('user3@gmail.com', 'password3', 'Jim', 'Johnson')
        channel_invite(user3['token'], test_channel2['channel_id'], user2['u_id'])


    clear()