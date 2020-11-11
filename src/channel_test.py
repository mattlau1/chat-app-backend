''' Test file for channel.py '''
import pytest
from channel import (channel_invite, channel_details, channel_messages, channel_leave,
                     channel_join, channel_addowner, channel_removeowner, channel_kick)
from channels import channels_create
from auth import auth_register
from message import message_send
from error import InputError, AccessError
from other import clear
from user import user_profile_setname


def test_channel_invite():
    '''
    Testing the channel_invite function
    '''
    clear()
    owner = auth_register('johnsmith@gmail.com', 'password', 'John', 'Smith')
    user = auth_register('stevejackson@gmail.com', 'password', 'Steve', 'Jackson')
    # User 1 creates a new channel, and invites User 2
    channel1 = channels_create(owner['token'], 'Test Channel 1', True)
    channel_invite(owner['token'], channel1['channel_id'], user['u_id'])
    # Already invited
    channel_invite(owner['token'], channel1['channel_id'], user['u_id'])

    # Checking if User 2 is a member of the channel (whether they can access channel details)
    channel_details(user['token'], channel1['channel_id'])

    channel2 = channels_create(owner['token'], 'Test Channel 2', True)

    # Authorised user does not have a valid token
    with pytest.raises(AccessError):
        channel_invite('', channel2['channel_id'], user['u_id'])

    # Channel ID does not refer to a valid channel
    with pytest.raises(InputError):
        channel_invite(owner['token'], channel2['channel_id'] + 100, user['u_id'])

    # User ID does not refer to a valid user
    with pytest.raises(InputError):
        channel_invite(owner['token'], channel2['channel_id'], user['u_id'] + 100)

    # Authorised user is not a member of the channel
    with pytest.raises(AccessError):
        user3 = auth_register('user3@gmail.com', 'password', 'Jim', 'Johnson')
        channel_invite(user3['token'], channel2['channel_id'], user['u_id'])


def test_channel_details():
    '''
    Testing the channel_details function
    '''
    clear()
    owner = auth_register('liambrown@gmail.com', 'password', 'Liam', 'Brown')
    channel = channels_create(owner['token'], 'Test Channel', True)
    user = auth_register('victorzhang@gmail.com', 'password', 'Victor', 'Zhang')

    # Checking if owner of channel can check channel details, and if they are correct
    details = channel_details(owner['token'], channel['channel_id'])
    assert details == {
        'name': 'Test Channel',
        'owner_members': [
            {
                'u_id': owner['u_id'],
                'name_first': 'Liam',
                'name_last': 'Brown',
            }
        ],
        'all_members': [
            {
                'u_id': owner['u_id'],
                'name_first': 'Liam',
                'name_last': 'Brown',
            },
        ],
    }

    # Checking if member of channel can check channel details, and if they are correct
    channel_join(user['token'], channel['channel_id'])
    details = channel_details(user['token'], channel['channel_id'])
    assert len(details['owner_members']) == 1
    assert len(details['all_members']) == 2
    
    channel_addowner(owner['token'], channel['channel_id'], user['u_id'])
    details = channel_details(user['token'], channel['channel_id'])
    assert len(details['owner_members']) == 2
    assert len(details['all_members']) == 2

    # Change the name of 'user' (2nd person) and check that all instances are updated
    user_profile_setname(user['token'], 'Kevin', 'Zhu')     
    details = channel_details(user['token'], channel['channel_id'])
    assert details == {
        'name': 'Test Channel',
        'owner_members': [
            {
                'u_id': owner['u_id'],
                'name_first': 'Liam',
                'name_last': 'Brown',
            },
            {
                'u_id': user['u_id'],
                'name_first': 'Kevin',
                'name_last': 'Zhu',
            }
        ],
        'all_members': [
            {
                'u_id': owner['u_id'],
                'name_first': 'Liam',
                'name_last': 'Brown',
            },
            {
                'u_id': user['u_id'],
                'name_first': 'Kevin',
                'name_last': 'Zhu',
            }
        ],
    }   

    # Authorised user does not have a valid token
    with pytest.raises(AccessError):
        channel_details('', channel['channel_id'])

    # Channel ID is not a valid channel
    with pytest.raises(InputError):
        channel_details(user['token'], channel['channel_id'] + 100)

    # Authorised user is not a member of the channel
    channel_leave(user['token'], channel['channel_id'])
    with pytest.raises(AccessError):
        channel_details(user['token'], channel['channel_id'])


# It is not feasible to do valid testing for channel_messages during iteration one
def test_channel_messages():
    '''
    Testing the channel_messages function
    '''
    clear()
    # Standard error check
    user = auth_register('testing@gmail.com', 'password', 'Test', 'User')
    channel = channels_create(user['token'], 'Test Channel', True)
    message_send(user['token'], channel['channel_id'], 'Test message')
    # Invalid channel_id
    with pytest.raises(InputError):
        channel_messages(user['token'], channel['channel_id'] + 100, 0)
    # Invalid token
    with pytest.raises(AccessError):
        channel_messages('', channel['channel_id'], 0)
    # Random user
    random_user = auth_register('test@gmail.com', 'password', 'Test', 'Mee')
    with pytest.raises(AccessError):
        channel_messages(random_user['token'], channel['channel_id'], 0)

    # Invalid start index
    messages = channel_messages(user['token'], channel['channel_id'], 0)
    assert len(messages['messages']) == 1
    assert messages['start'] == 0
    assert messages['end'] == -1
    messages = channel_messages(user['token'], channel['channel_id'], 1)
    assert len(messages['messages']) == 0
    assert messages['start'] == 1
    assert messages['end'] == -1
    with pytest.raises(InputError):
        channel_messages(user['token'], channel['channel_id'], 2)
    # Send 48 more messages - 49 total
    for _ in range(2, 50):
        message_send(user['token'], channel['channel_id'], 'Test message')
    messages = channel_messages(user['token'], channel['channel_id'], 0)
    assert len(messages['messages']) == 49
    assert messages['start'] == 0
    assert messages['end'] == -1
    # 50 total messages
    message_send(user['token'], channel['channel_id'], 'Test message')
    messages = channel_messages(user['token'], channel['channel_id'], 0)
    assert len(messages['messages']) == 50
    assert messages['start'] == 0
    assert messages['end'] == -1
    # 51 total messages
    # Start from index 0
    message_send(user['token'], channel['channel_id'], 'Test message')
    messages = channel_messages(user['token'], channel['channel_id'], 0)
    assert len(messages['messages']) == 50
    assert messages['start'] == 0
    assert messages['end'] == 50
    # Start from index 1
    messages = channel_messages(user['token'], channel['channel_id'], 1)
    assert len(messages['messages']) == 50
    assert messages['start'] == 1
    assert messages['end'] == -1


def test_channel_leave():
    '''
    Testing the channel_leave function
    '''
    clear()
    owner = auth_register('petermichaels@gmail.com', 'password', 'Peter', 'Michaels')
    channel = channels_create(owner['token'], 'Test Channel', True)
    user = auth_register('kimwilliams@gmail.com', 'password', 'Kim', 'Williams')

    # Checking if a user can leave (verified if not able to access channel details afterwards)
    channel_join(user['token'], channel['channel_id'])
    channel_details(user['token'], channel['channel_id'])
    channel_leave(user['token'], channel['channel_id'])
    with pytest.raises(AccessError):
        channel_details(user['token'], channel['channel_id'])

    # Checking if a user can leave (verified if number of members becomes 1 afterwards)
    channel_join(user['token'], channel['channel_id'])
    details = channel_details(owner['token'], channel['channel_id'])
    assert len(details['all_members']) == 2

    channel_leave(user['token'], channel['channel_id'])
    details = channel_details(owner['token'], channel['channel_id'])
    assert len(details['all_members']) == 1

    # Authorised user does not have a valid token
    with pytest.raises(AccessError):
        channel_leave('', channel['channel_id'])

    # Channel ID is not a valid channel
    channel_join(user['token'], channel['channel_id'])
    with pytest.raises(InputError):
        channel_leave(user['token'], channel['channel_id'] + 100)

    # Authorised user is not a member of the channel (leaving channel twice)
    channel_leave(user['token'], channel['channel_id'])
    with pytest.raises(AccessError):
        channel_leave(user['token'], channel['channel_id'])

    # Checking if an owner can leave (verified if not able to access channel details
    # and not able to further remove owners)
    channel_join(user['token'], channel['channel_id'])
    channel_addowner(owner['token'], channel['channel_id'], user['u_id'])
    channel_leave(owner['token'], channel['channel_id'])
    with pytest.raises(AccessError):
        channel_details(owner['token'], channel['channel_id'])


def test_channel_join():
    '''
    Testing the channel_join function
    '''
    clear()
    owner = auth_register('petermichaels@gmail.com', 'password', 'Peter', 'Michaels')
    channel1 = channels_create(owner['token'], 'Channel 1', True)
    user = auth_register('kimwilliams@gmail.com', 'password', 'Kim', 'Williams')

    details = channel_details(owner['token'], channel1['channel_id'])
    assert len(details['all_members']) == 1

    # Checking if a user can join a channel
    # (verified if number of members becomes 2 and if they can leave the channel)
    channel_join(user['token'], channel1['channel_id'])
    details = channel_details(user['token'], channel1['channel_id'])
    assert len(details['all_members']) == 2
    channel_leave(user['token'], channel1['channel_id'])

    # Authorised user does not have a valid token
    with pytest.raises(AccessError):
        channel_join('', channel1['channel_id'])

    # Channel ID is not a valid channel
    with pytest.raises(InputError):
        channel_join(user['token'], channel1['channel_id'] + 100)

    # Channel ID is a private channel (authorised user is not a global owner)
    channel2 = channels_create(owner['token'], 'Channel 2', False)
    with pytest.raises(AccessError):
        channel_join(user['token'], channel2['channel_id'])

    # User joining multiple times - doesn't raise error
    channel_join(user['token'], channel1['channel_id'])
    channel_join(user['token'], channel1['channel_id'])


def test_channel_addowner():
    '''
    Testing the channel_addowner function
    '''
    clear()
    owner = auth_register('bobsmith@gmail.com', 'password', 'Bob', 'Smith')
    channel = channels_create(owner['token'], 'Test channel', True)
    user = auth_register('jesschen@gmail.com', 'password', 'Jess', 'Chen')
    channel_join(user['token'], channel['channel_id'])

    details = channel_details(owner['token'], channel['channel_id'])
    assert len(details['owner_members']) == 1

    # Checking if someone can be added as an owner
    # (verified if number of owners becomes 2 and if they can be immediately removed)
    channel_addowner(owner['token'], channel['channel_id'], user['u_id'])
    details = channel_details(owner['token'], channel['channel_id'])
    assert len(details['owner_members']) == 2
    channel_removeowner(owner['token'], channel['channel_id'], user['u_id'])

    # Adding someone who is already the owner
    channel_addowner(owner['token'], channel['channel_id'], user['u_id'])
    with pytest.raises(InputError):
        channel_addowner(owner['token'], channel['channel_id'], user['u_id'])
    channel_removeowner(owner['token'], channel['channel_id'], user['u_id'])

    # Authorised user does not have a valid token
    with pytest.raises(AccessError):
        channel_addowner('', channel['channel_id'], user['u_id'])

    # New owner does not have a valid token
    with pytest.raises(AccessError):
        channel_addowner(owner['token'], channel['channel_id'], 100)

    # Channel ID is not a valid channel
    with pytest.raises(InputError):
        channel_addowner(owner['token'], channel['channel_id'] + 100, user['u_id'])

    # Authorised user is not the owner
    with pytest.raises(AccessError):
        channel_addowner(user['token'], channel['channel_id'], user['u_id'])


def test_channel_removeowner():
    '''
    Testing the channel_removeowner function
    '''
    clear()
    owner = auth_register('bobsmith@gmail.com', 'password', 'Bob', 'Smith')
    channel = channels_create(owner['token'], 'Test channel', True)
    user = auth_register('jesschen@gmail.com', 'password', 'Jess', 'Chen')
    channel_join(user['token'], channel['channel_id'])

    # Checking if someone can be removed (verified if number of owners becomes 1 afterwards)
    channel_addowner(owner['token'], channel['channel_id'], user['u_id'])
    details = channel_details(owner['token'], channel['channel_id'])
    assert len(details['owner_members']) == 2

    channel_removeowner(owner['token'], channel['channel_id'], user['u_id'])
    details = channel_details(owner['token'], channel['channel_id'])
    assert len(details['owner_members']) == 1

    # Removing someone who is already removed (no longer an owner)
    with pytest.raises(InputError):
        channel_removeowner(owner['token'], channel['channel_id'], user['u_id'])

    # Authorised user is not an owner
    with pytest.raises(AccessError):
        channel_removeowner(user['token'], channel['channel_id'], owner['u_id'])

    # Addding someone to be removed
    channel_addowner(owner['token'], channel['channel_id'], user['u_id'])

    # Authorised user does not have a valid token
    with pytest.raises(AccessError):
        channel_removeowner('', channel['channel_id'], user['u_id'])

    # Old owner does not have a valid token
    with pytest.raises(AccessError):
        channel_removeowner(owner['token'], channel['channel_id'], 100)

    # Channel ID is not a valid channel
    with pytest.raises(InputError):
        channel_removeowner(owner['token'], channel['channel_id'] + 100, user['u_id'])

    # Authorised user can remove owner (since they are now another owner)
    channel_removeowner(user['token'], channel['channel_id'], owner['u_id'])


# Extra function
def test_channel_kick():
    '''
    Testing the channel_kick function
    '''
    clear()
    owner = auth_register('bobsmith@gmail.com', 'password', 'Bob', 'Smith')
    channel = channels_create(owner['token'], 'Test channel', True)
    user = auth_register('jesschen@gmail.com', 'password', 'Jess', 'Chen')
    channel_join(user['token'], channel['channel_id'])

    # Authorised user does not have a valid token
    with pytest.raises(AccessError):
        channel_kick('', channel['channel_id'], user['u_id'])

    # Old user does not have a valid token
    with pytest.raises(AccessError):
        channel_kick(owner['token'], channel['channel_id'], 100)

    # Channel ID is not a valid channel
    with pytest.raises(InputError):
        channel_kick(owner['token'], channel['channel_id'] + 100, user['u_id'])

    # Authorised user is not an owner
    with pytest.raises(AccessError):
        channel_kick(user['token'], channel['channel_id'], owner['u_id'])

    # Old user is an owner
    channel_addowner(owner['token'], channel['channel_id'], user['u_id'])
    with pytest.raises(InputError):
        channel_kick(owner['token'], channel['channel_id'], user['u_id'])

    # Remove old user as an owner (so they are now just a member)
    channel_removeowner(owner['token'], channel['channel_id'], user['u_id'])

    details = channel_details(owner['token'], channel['channel_id'])
    assert len(details['all_members']) == 2

    # Authorised user can now remove old user
    channel_kick(owner['token'], channel['channel_id'], user['u_id'])
    
    details = channel_details(owner['token'], channel['channel_id'])
    assert len(details['all_members']) == 1

    # Removing someone who is already removed (no longer a member)
    with pytest.raises(InputError):
        channel_kick(owner['token'], channel['channel_id'], user['u_id'])

    # Removed user cannot kick
    with pytest.raises(AccessError):
        channel_kick(user['token'], channel['channel_id'], owner['u_id'])


def test_flockr_owner():
    '''
    Testing functionality for Flockr owner
    '''
    clear()
    flockr_owner = auth_register('big@man.com', 'password', 'Big', 'Boss')
    admin = auth_register('admin@com.com', 'password', 'Channel', 'Boss')
    user = auth_register('normie@normal.com', 'password', 'Average', 'Jonas')

    # Admin creates channel
    private_channel = channels_create(admin['token'], 'Test Channel', False)

    # Flockr owner has to join as member first, like normal user
    with pytest.raises(AccessError):
        channel_addowner(admin['token'], private_channel['channel_id'], user['u_id'])

    with pytest.raises(AccessError):
        channel_addowner(admin['token'], private_channel['channel_id'], flockr_owner['u_id'])

    # Flockr owner can't invite or add/remove owner if they haven't joined the channel as a member
    with pytest.raises(AccessError):
        channel_invite(flockr_owner['token'], private_channel['channel_id'], user['u_id'])
    channel_invite(admin['token'], private_channel['channel_id'], user['u_id'])
    with pytest.raises(AccessError):
        channel_addowner(flockr_owner['token'], private_channel['channel_id'], user['u_id'])
    channel_addowner(admin['token'], private_channel['channel_id'], user['u_id'])
    with pytest.raises(AccessError):
        channel_removeowner(flockr_owner['token'], private_channel['channel_id'], user['u_id'])
    channel_leave(user['token'], private_channel['channel_id'])

    # Flockr owner can join private channels, but regular users can't
    with pytest.raises(AccessError):
        channel_join(user['token'], private_channel['channel_id'])
    channel_join(flockr_owner['token'], private_channel['channel_id'])

    # Flockr owner can invite/add_owner/remove_owner once joined
    channel_invite(flockr_owner['token'], private_channel['channel_id'], user['u_id'])
    channel_addowner(flockr_owner['token'], private_channel['channel_id'], user['u_id'])
    channel_removeowner(flockr_owner['token'], private_channel['channel_id'], user['u_id'])
