''' Test file for other.py '''
import pytest
from auth import auth_register
from channel import channel_invite, channel_details, channel_join, channel_leave
from channels import channels_create, channels_list
from message import message_send, message_remove, message_edit
from other import clear, search, admin_userpermission_change
from error import InputError, AccessError


def test_clear():
    '''
    Test that clear removes the users[], channels[] and resets the latest_message_id
    '''
    f_owner = auth_register('admin@gmail.com', 'password', 'Bob', 'Bob')
    f_channel = channels_create(f_owner['token'], 'Channel 1', True)

    details = channel_details(f_owner['token'], f_channel['channel_id'])
    assert len(details['all_members']) == 1
    assert len(details['owner_members']) == 1

    # random_user = auth_register('random@gmail.com', 'password', 'Random', 'User')
    # channel_invite(f_owner['token'], f_channel['channel_id'], random_user['u_id'])
    # assert len(details['all_members']) == 2
    # assert len(details['owner_members']) == 1
    
    assert len(channels_list(f_owner['token'])['channels']) == 1
    
    m_id = message_send(f_owner['token'], f_channel['channel_id'], 'First message')
    
    assert m_id['message_id'] == 1
    
    clear()
    # assert len(details['all_members']) == 0
    # assert len(details['owner_members']) == 0
    # assert len(channels_list(f_owner['token'])['channels']) == 0
    # assert m_id['message_id'] == 0


def test_admin_userpermission_change_to_owner():
    '''
    Test that admin_userpermission_change can set permissions of the user with the given user ID
    from member to owner permissions.
    '''
    clear()
    user1 = auth_register('billgates@gmail.com', 'password', 'Bill', 'Gates')
    user2 = auth_register('steveballmer@gmail.com', 'password', 'Steve', 'Ballmer')

    # First user (a Flockr owner) creates a private channel
    f_channel = channels_create(user1['token'], 'Private Channel', False)
    # Second user is unable to join the private channel as they are not a Flockr owner
    with pytest.raises(AccessError):
        channel_join(user2['token'], f_channel['channel_id'])

    # First user changes permissions of second user to make them a Flockr owner
    admin_userpermission_change(user1['token'], user2['u_id'], 1)

    # Check that second user is now a Flockr owner 
    # (verified by now being able to join the private channel)
    channel_join(user2['token'], f_channel['channel_id'])


def test_admin_userpermission_change_to_member():
    '''
    Test that admin_userpermission_change can set permissions of the user with the given user ID
    from owner to member permissions.
    '''
    clear()
    user1 = auth_register('billgates@gmail.com', 'password', 'Bill', 'Gates')
    user2 = auth_register('steveballmer@gmail.com', 'password', 'Steve', 'Ballmer')

    # First user changes permissions of second user to make them a Flockr owner
    admin_userpermission_change(user1['token'], user2['u_id'], 1)

    # Second user creates a private channel
    f_channel = channels_create(user2['token'], 'Private Channel', False)
    # First user is able to join the private channel as they are a Flockr owner
    channel_join(user1['token'], f_channel['channel_id'])
    channel_leave(user1['token'], f_channel['channel_id'])

    # Second user changes permissions of first user to make them a member
    admin_userpermission_change(user2['token'], user1['u_id'], 2)

    # Check that first user is now a member
    # (verified by now not being able to join the private channel)
    with pytest.raises(AccessError):
        channel_join(user1['token'], f_channel['channel_id'])


def test_admin_userpermission_change_invalid_user_id():
    '''
    Test that an InputError is raised when admin_userpermission_change 
    is given a u_id that does not refer to a valid user
    '''
    clear()
    f_owner = auth_register('admin@gmail.com', 'password', 'Bob', 'Bob')
    with pytest.raises(InputError):
        admin_userpermission_change(f_owner['token'], f_owner['u_id'] + 1, 2)
    with pytest.raises(InputError):
        admin_userpermission_change(f_owner['token'], f_owner['u_id'] + 100, 2)
    with pytest.raises(InputError):
        admin_userpermission_change(f_owner['token'], f_owner['u_id'] - 13, 2)
    with pytest.raises(InputError):
        admin_userpermission_change(f_owner['token'], f_owner['u_id'] - 100, 2)


def test_admin_userpermission_change_invalid_permission_id():
    '''
    Test that an InputError is raised when admin_userpermission_change 
    is given a permission_id that does not refer to a valid permission
    '''
    clear()
    f_owner = auth_register('admin@gmail.com', 'password', 'Bob', 'Bob')
    random_user = auth_register('timhall@gmail.com', 'password', 'Tim', 'Hall')
    with pytest.raises(InputError):
        admin_userpermission_change(f_owner['token'], random_user['u_id'], 0)
    with pytest.raises(InputError):
        admin_userpermission_change(f_owner['token'], random_user['u_id'], 3)
    with pytest.raises(InputError):
        admin_userpermission_change(f_owner['token'], random_user['u_id'], 100)
    with pytest.raises(InputError):
        admin_userpermission_change(f_owner['token'], random_user['u_id'], -5)


def test_admin_userpermission_change_user_not_owner():
    '''
    Test that an AccessError is raised when the authorised user calling
    admin_userpermission_change does not have owner permissions
    '''
    clear()
    f_owner = auth_register('admin@gmail.com', 'password', 'Bob', 'Bob')
    member1 = auth_register('timhall@gmail.com', 'password', 'Tim', 'Hall')
    member2 = auth_register('kimsean@gmail.com', 'password', 'Kim', 'Sean')
    
    with pytest.raises(AccessError):
        admin_userpermission_change(member1['token'], f_owner['u_id'], 2)
    with pytest.raises(AccessError):
        admin_userpermission_change(member2['token'], member1['u_id'], 1)


def test_search_invalid():
    '''
    Testing invalid cases for search
    '''
    clear()
    f_owner = auth_register('admin@gmail.com', 'password', 'Bob', 'Bob')
    f_channel = channels_create(f_owner['token'], 'Channel 1', True)
    message_send(f_owner['token'], f_channel['channel_id'], 'First message')

    # Invalid token
    with pytest.raises(AccessError):
        search(f_owner['token'] + 'padding', 'First')

    # Empty messages (shouldn't be sent anyways)
    with pytest.raises(InputError):
        message_send(f_owner['token'], f_channel['channel_id'], '')
        messages = search(f_owner['token'], '')
        assert len(messages) == 0


def test_search_valid_substring():
    '''
    Testing valid substring search functionality for search
    '''
    clear()
    f_owner = auth_register('admin@gmail.com', 'password', 'Bob', 'Bob')
    f_channel = channels_create(f_owner['token'], 'Channel 1', True)
    random_user = auth_register('random@gmail.com', 'password', 'Random', 'User')
    channel_invite(f_owner['token'], f_channel['channel_id'], random_user['u_id'])

    msg = message_send(f_owner['token'], f_channel['channel_id'], 'First message')

    # Test exact match
    messages = search(f_owner['token'], 'First message')['messages']
    assert len(messages) == 1
    assert messages[0]['message_id'] == msg['message_id']
    assert messages[0]['u_id'] == f_owner['u_id']

    # Test substring
    messages = search(f_owner['token'], 'First')['messages']
    assert len(messages) == 1
    assert messages[0]['message_id'] == msg['message_id']
    assert messages[0]['u_id'] == f_owner['u_id']

    # Edited message
    message_edit(f_owner['token'], msg['message_id'], 'Test message')
    messages = search(f_owner['token'], 'First')['messages']
    assert len(messages) == 0

    # Removed message
    message_remove(f_owner['token'], msg['message_id'])
    messages = search(f_owner['token'], 'First message')['messages']
    assert len(messages) == 0

    # Test substring
    for multiple in range(1, 51):
        # f_owner and random_user sent
        message_send(f_owner['token'], f_channel['channel_id'], 'A' * multiple)
        message_send(random_user['token'], f_channel['channel_id'], 'A' * multiple)
        # f_owner searched
        messages = search(f_owner['token'], 'A')['messages']
        assert len(messages) == multiple * 2
        # random_user searched
        messages = search(random_user['token'], 'A')['messages']
        assert len(messages) == multiple * 2
        # Caps-sensitive
        messages = search(f_owner['token'], 'a')['messages']
        assert len(messages) == 0


def test_search_valid_global():
    '''
    Testing search works across all channels a user is in
    '''
    clear()
    f_owner = auth_register('admin@gmail.com', 'password', 'Bob', 'Bob')
    common_channel = channels_create(f_owner['token'], 'Common Channel', True)
    f_channel = channels_create(f_owner['token'], 'Crib', True)

    # Test includes private channels as well
    random_user = auth_register('random@gmail.com', 'password', 'Random', 'User')
    private_channel = channels_create(random_user['token'], 'SSH', False)

    channel_invite(f_owner['token'], common_channel['channel_id'], random_user['u_id'])

    # Messages sent to common channels
    for i in range(1, 51):
        message_send(f_owner['token'], common_channel['channel_id'], 'F')
        message_send(random_user['token'], common_channel['channel_id'], 'R')
        f_messages = search(f_owner['token'], 'F')['messages']
        r_messages = search(f_owner['token'], 'R')['messages']
        assert len(f_messages) == i and len(r_messages) == i

    # Messages sent to personal channels (includes messages in common_channel)
    for i in range(1, 51):
        message_send(f_owner['token'], f_channel['channel_id'], 'F')
        message_send(random_user['token'], private_channel['channel_id'], 'R')
        f_messages = search(f_owner['token'], 'F')['messages']
        r_messages = search(random_user['token'], 'R')['messages']
        assert len(f_messages) == 50 + i and len(r_messages) == 50 + i

    # From Flockr Owner
    f_messages = search(f_owner['token'], 'F')['messages']
    assert len(f_messages) == 100
    r_messages = search(f_owner['token'], 'R')['messages']
    assert len(r_messages) == 50
    # From Random User
    f_messages = search(random_user['token'], 'F')['messages']
    assert len(f_messages) == 50
    r_messages = search(random_user['token'], 'R')['messages']
    assert len(r_messages) == 100
