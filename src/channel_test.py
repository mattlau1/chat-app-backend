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