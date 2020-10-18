''' Test file for message.py '''
import pytest
from auth import auth_register
from channel import channel_messages, channel_invite
from channels import channels_create
from message import message_send
from error import InputError, AccessError
from other import clear

def test_message_send_invalid():
    '''
    Test invalid message sending
    '''
    clear()
    f_owner = auth_register('owner@gmail.com', 'password', 'Flockr', 'Boss')
    f_channel = channels_create(f_owner['token'], 'Main Channel', True)
    
    # Invalid token
    with pytest.raises(AccessError):
        message_send('', f_channel['channel_id'], 'Test Message')
    # Invalid channel
    with pytest.raises(InputError):
        message_send(f_owner['token'], f_channel['channel_id'] + 100, 'Test message')

    random_user = auth_register('random@gmail.com', 'password', 'Random', 'User')
    r_channel = channels_create(random_user['token'], 'Random Channel', True)

    # User not in channel as member
    with pytest.raises(AccessError):
        message_send(f_owner['token'], r_channel['channel_id'], 'f_owner in r_channel')
    with pytest.raises(AccessError):
        message_send(random_user['token'], f_channel['channel_id'], 'random_user in f_channel')

    # Message lengths
    with pytest.raises(InputError):
        message_send(f_owner['token'], f_channel['channel_id'], '')
    message = 'A' * 1001
    with pytest.raises(InputError):
        message_send(f_owner['token'], f_channel['channel_id'], message)
    with pytest.raises(InputError):
        message_send(f_owner['token'], f_channel['channel_id'], message + 'x')

def test_message_send_valid():
    '''
    Valid message sending
    '''
    clear()
    f_owner = auth_register('owner@gmail.com', 'password', 'Flockr', 'Boss')
    f_channel = channels_create(f_owner['token'], 'Main Channel', True)
    random_user = auth_register('random@gmail.com', 'password', 'Random', 'User')
    channel_invite(f_owner['token'], f_channel['channel_id'], random_user['u_id'])

    # Message lengths
    message_send(f_owner['token'], f_channel['channel_id'], 'First message')
    output = channel_messages(f_owner['token'], f_channel['channel_id'], 0)
    assert len(output['messages']) == 1
    
    message = 'A'
    for multiple in range(1, 1001):
        message_send(f_owner['token'], f_channel['channel_id'], multiple * message)
        message_send(random_user['token'], f_channel['channel_id'], multiple * message)

def test_message_remove():
    '''
    Test message removal
    '''
    clear()
    f_owner = auth_register('owner@gmail.com', 'password', 'Flockr', 'Boss')
    f_channel = channels_create(f_owner['token'], 'Main Channel', True)
    random_user = auth_register('random@gmail.com', 'password', 'Random', 'User')
    channel_invite(f_owner['token'], f_channel['channel_id'], random_user['u_id'])
    random_user2 = auth_register('randomguy@gmail.com', 'password', 'Random2', 'Guy2')
    channel_invite(f_owner['token'], f_channel['channel_id'], random_user2['u_id'])
    
    m_id1 = message_send(f_owner['token'], f_channel['channel_id'], 'First message')
    m_id2 = message_send(random_user['token'], f_channel['channel_id'], 'Second message')
    m_id2 = message_send(random_user2['token'], f_channel['channel_id'], 'Third message')

    # Invalid token
    with pytest.raises(AccessError):
        message_remove('', f_channel['messages']['message_id'])
    # Invalid message_id
    with pytest.raises(InputError):
        message_remove(f_owner['token'], '')

    # Authorised user did not send the message and is not channel or Flockr owner
    with pytest.raises(AccessError):
        message_remove(random_user['token'], m_id1)
    with pytest.raises(AccessError):
        message_remove(random_user2['token'], m_id2)

    assert count(f_channel['messages']) == 3
    # Message sender can remove their own message
    message_remove(random_user2['token'], m_id3)
    assert count(f_channel['messages']) == 2
    # Flockr owner can remove anyone's message
    message_remove(f_owner['token'], m_id2)
    assert count(f_channel['messages']) == 1
    # Flockr owner can remove their own message
    message_remove(f_owner['token'], m_id1)
    assert count(f_channel['messages']) == 0

