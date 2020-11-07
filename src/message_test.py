''' Test file for message.py '''
import pytest
import time
from datetime import datetime, timedelta
from auth import auth_register
from channel import channel_messages, channel_invite
from channels import channels_create
from message import (
    message_send, message_remove, message_edit, message_sendlater,
    message_react, message_unreact, message_pin, message_unpin,
)
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

    m_id1 = message_send(f_owner['token'], f_channel['channel_id'], 'First message')['message_id']

    # Invalid message_id
    with pytest.raises(InputError):
        message_remove(f_owner['token'], m_id1 + 1)

    m_id2 = message_send(random_user['token'], f_channel['channel_id'], 'Second message')['message_id']
    m_id3 = message_send(random_user2['token'], f_channel['channel_id'], 'Third message')['message_id']

    # Invalid token
    with pytest.raises(AccessError):
        message_remove('', m_id1)

    # Authorised user did not send the message and is not channel or Flockr owner
    with pytest.raises(AccessError):
        message_remove(random_user['token'], m_id1)
    with pytest.raises(AccessError):
        message_remove(random_user2['token'], m_id2)

    messages = channel_messages(f_owner['token'], f_channel['channel_id'], 0)['messages']
    assert len(messages) == 3
    # Message sender can remove their own message
    message_remove(random_user2['token'], m_id3)
    messages = channel_messages(f_owner['token'], f_channel['channel_id'], 0)['messages']
    assert len(messages) == 2
    # Flockr owner can remove anyone's message
    message_remove(f_owner['token'], m_id2)
    messages = channel_messages(f_owner['token'], f_channel['channel_id'], 0)['messages']
    assert len(messages) == 1
    # Flockr owner can remove their own message
    message_remove(f_owner['token'], m_id1)
    messages = channel_messages(f_owner['token'], f_channel['channel_id'], 0)['messages']
    assert len(messages) == 0

    # Message_id no longer exists
    with pytest.raises(InputError):
        message_remove(f_owner['token'], m_id1)


def test_message_edit():
    '''
    Test message edit
    '''
    clear()
    f_owner = auth_register('owner@gmail.com', 'password', 'Flockr', 'Boss')
    f_channel = channels_create(f_owner['token'], 'Main Channel', True)
    random_user = auth_register('random@gmail.com', 'password', 'Random', 'User')
    channel_invite(f_owner['token'], f_channel['channel_id'], random_user['u_id'])
    random_user2 = auth_register('randomguy@gmail.com', 'password', 'Random2', 'Guy2')
    channel_invite(f_owner['token'], f_channel['channel_id'], random_user2['u_id'])

    m_id1 = message_send(f_owner['token'], f_channel['channel_id'], 'First message')['message_id']

    # Invalid message_id
    with pytest.raises(InputError):
        message_edit(f_owner['token'], m_id1 + 1, 'Edited first message')

    m_id2 = message_send(random_user['token'], f_channel['channel_id'], 'Second message')['message_id']
    m_id3 = message_send(random_user2['token'], f_channel['channel_id'], 'Third message')['message_id']

    # Invalid token
    with pytest.raises(AccessError):
        message_edit('', m_id1, 'Edited first message')

    # Check messages content
    messages = channel_messages(f_owner['token'], f_channel['channel_id'], 0)['messages']
    messages = [message['message'] for message in messages]
    assert messages == ['Third message', 'Second message', 'First message']

    # Authorised user did not send the message and is not channel or Flockr owner
    with pytest.raises(AccessError):
        message_edit(random_user['token'], m_id1, 'Edited first message')
    with pytest.raises(AccessError):
        message_edit(random_user2['token'], m_id2, 'Edited second message')

    # Message sender can edit their own message
    message_edit(random_user2['token'], m_id3, 'Edited third message')
    # Flockr owner can edit anyone's message
    message_edit(f_owner['token'], m_id2, 'Edited second message')
    # Flockr owner can edit their own message
    message_edit(f_owner['token'], m_id1, 'Edited first message')

    # Check messages content
    messages = channel_messages(f_owner['token'], f_channel['channel_id'], 0)['messages']
    messages = [message['message'] for message in messages]
    assert messages == ['Edited third message', 'Edited second message', 'Edited first message']

    # If the edited message becomes an empty string, it should be deleted
    m_id4 = message_send(f_owner['token'], f_channel['channel_id'], 'Fourth message')['message_id']
    m_id5 = message_send(random_user['token'], f_channel['channel_id'], 'Fifth message')['message_id']
    m_id6 = message_send(random_user2['token'], f_channel['channel_id'], 'Sixth message')['message_id']

    messages = channel_messages(f_owner['token'], f_channel['channel_id'], 0)['messages']
    assert len(messages) == 6

    # Authorised user did not send the message is not channel or Flockr owner
    with pytest.raises(AccessError):
        message_edit(random_user['token'], m_id4, '')
    with pytest.raises(AccessError):
        message_edit(random_user2['token'], m_id5, '')

    # Message sender can delete their own message by editing it to an empty message
    message_edit(random_user2['token'], m_id6, '')
    # Flockr owner can delete anyone's message by editing it to an empty message
    message_edit(f_owner['token'], m_id5, '')
    # Flockr owner can delete their own message by editing it to an empty message
    message_edit(f_owner['token'], m_id4, '')

    messages = channel_messages(f_owner['token'], f_channel['channel_id'], 0)['messages']
    assert len(messages) == 3


def test_message_sendlater_invalid():
    '''
    Test invalidly sending a message later
    '''
    clear()
    f_owner = auth_register('owner@gmail.com', 'password', 'Flockr', 'Boss')
    f_channel = channels_create(f_owner['token'], 'Main Channel', True)

    time_sent = datetime.timestamp(datetime.now()) - 2

    # Time is in the past
    with pytest.raises(InputError):
        message_sendlater(f_owner['token'], f_channel['channel_id'], 'Test message', time_sent)

    time_sent = datetime.timestamp(datetime.now()) + 2

    # Invalid token
    with pytest.raises(AccessError):
        message_sendlater('', f_channel['channel_id'], 'Test Message', time_sent)
    # Invalid channel
    with pytest.raises(InputError):
        message_sendlater(f_owner['token'], f_channel['channel_id'] + 100, 'Test message', time_sent)

    random_user = auth_register('random@gmail.com', 'password', 'Random', 'User')
    r_channel = channels_create(random_user['token'], 'Random Channel', True)

    # User not in channel as member
    with pytest.raises(AccessError):
        message_sendlater(f_owner['token'], r_channel['channel_id'], 'f_owner in r_channel', time_sent)
    with pytest.raises(AccessError):
        message_sendlater(random_user['token'], f_channel['channel_id'], 'random_user in f_channel', time_sent)

    # Message lengths
    with pytest.raises(InputError):
        message_sendlater(f_owner['token'], f_channel['channel_id'], '', time_sent)
    message = 'A' * 1001
    with pytest.raises(InputError):
        message_sendlater(f_owner['token'], f_channel['channel_id'], message, time_sent)
    with pytest.raises(InputError):
        message_sendlater(f_owner['token'], f_channel['channel_id'], message + 'x', time_sent)    


def test_message_sendlater_valid():
    '''
    Test validly sending a message later
    '''
    clear()
    f_owner = auth_register('owner@gmail.com', 'password', 'Flockr', 'Boss')
    f_channel = channels_create(f_owner['token'], 'Main Channel', True)
    random_user = auth_register('random@gmail.com', 'password', 'Random', 'User')
    channel_invite(f_owner['token'], f_channel['channel_id'], random_user['u_id'])

    time_sent = datetime.timestamp(datetime.now()) + 2

    # Message lengths
    message_sendlater(f_owner['token'], f_channel['channel_id'], 'First message', time_sent)
    output = channel_messages(f_owner['token'], f_channel['channel_id'], 0)
    assert len(output['messages']) == 0

    time.sleep(3)
    output = channel_messages(f_owner['token'], f_channel['channel_id'], 0)
    assert len(output['messages']) == 1


def test_message_valid_react():
    '''
    Test user valid react to the message
    '''
    clear()
    # the react_id is given in the spec
    react_id = 1

    # making a normal channel
    f_owner = auth_register('fox@gmail.com', 'password', 'Fox', 'Foxson')
    f_channel = channels_create(f_owner['token'], 'Main HUB', True)

    # invite a random user to the channel
    random_user = auth_register('random@gmail.com', 'password', 'Random', 'User')
    channel_invite(f_owner['token'], f_channel['channel_id'], random_user['u_id'])

    # invite a second user
    random_user2 = auth_register('randomguy@gmail.com', 'password', 'Random2', 'Guy2')
    channel_invite(f_owner['token'], f_channel['channel_id'], random_user2['u_id'])

    # owner sends message
    m_id1 = message_send(f_owner['token'], f_channel['channel_id'], 'I came first!')['message_id']

    # random user reacts to the message
    # the given react id from the spec is 1
    message_react(random_user['token'], m_id1, react_id)

    messages = channel_messages(f_owner['token'], f_channel['channel_id'], 0)['messages']
    
    # check if the user has reacted and check if the owner itself has reacted
    for message in messages:
        if message['message_id'] == m_id1:
            assert message['reacts']['react_id'] == react_id
            assert len(message['reacts']['u_ids']) == [random_user['u_id']]
            assert message['reacts']['is_this_user_reacted'] == False 

    # the second user reacts to the same message 
    message_react(random_user2['token'], m_id1, 1)

    # check if another user has reacted and check if a random user itself has reacted
    messages = channel_messages(random_user['token'], f_channel['channel_id'], 0)['messages']
    
    for message in messages:
        if message['message_id'] == m_id1:
            assert message['reacts']['react_id'] == react_id
            assert message['reacts']['u_ids'] == [random_user['u_id'], random_user2['u_id']]
            assert message['reacts']['is_this_user_reacted'] == True 

def test_message_invalid_react():
    pass

def test_message_already_unreact():
    pass

def test_message_unreact_unreacted():
    pass

def test_message_valid_unreact():
    pass

def test_message_invalid_unreact():
    pass

def test_message_pin_invalid():
    '''
    Test:
    - Pinning with invalid Token
    - Pinning messages whilst not being in channel
    - Pinning with invalid message id

    Scenario:
    - Two users register (owner and user)
    - owner creates a private channel and sends a message
    - Test attempts to pin this message with invalid token and message id
    - User tries to pin the message without being in the channel
    - Test checks that the message is not pinned
    '''
    clear()

    # Owner and User register
    f_owner = auth_register('johnmonkeyson@gmail.com', 'bananayummy', 'John', 'Monkeyson')
    f_user = auth_register('stevenson@gmail.com', 'ihatebananas', 'Steven', 'Stevenson')

    # Owner creates private channel
    f_channel = channels_create(f_owner['token'], 'Private Channel', False)

    # Owner sends message in f_channel (Private Channel)
    m_id1 = message_send(f_owner['token'], f_channel['channel_id'], 'hELLO wOORLD!')['message_id']

    # Invalid token
    with pytest.raises(AccessError):
        message_pin('thisisaninvalidtoken!', m_id1)

    # Invalid message id
    with pytest.raises(InputError):
        message_pin(f_owner['token'], -29424)

    # Pinning message without being in the channel
    with pytest.raises(AccessError):
        message_pin(f_user['token'], m_id1)

    # Get messages in channel
    messages = channel_messages(f_owner['token'], f_channel['channel_id'], 0)['messages']

    # Check that the message is not pinned
    for message in messages:
        if message['message_id'] == m_id1:
            assert message['is_pinned'] == False

def test_message_pin_permission():
    '''
    Test:
    - Pinning a message without being an owner of the channel

    Scenario:
    - Two users register (owner and user), owner creates a private channel and 
    invites user to channel
    - Owner sends a message
    - User tries to pin message(should not work)
    - Test checks that the message is not pinned
    - Owner pins the message (should work) 
    - Test checks that the message is actually pinned
    '''
    clear()

    # Owner and User register
    f_owner = auth_register('peter@com.com', 'djiffgjigi22', 'Peter', 'Peterson')
    f_user = auth_register('useruserson@gmail.com', 'helloworld', 'User', 'Userson')

    # Owner creates private channel
    f_channel = channels_create(f_owner['token'], 'Private Channel', False)

    # Owner invites f_user to channel
    channel_invite(f_owner['token'], f_channel['channel_id'], f_user['u_id'])

    # Owner sends message in f_channel (Private Channel)
    m_id1 = message_send(f_owner['token'], f_channel['channel_id'], 'hELLO wOORLD!')['message_id']

    # User tries to pin the message but is not an owner (no permission)
    with pytest.raises(AccessError)
        message_pin(f_user['token'], m_id1)

    # Get messages in channel
    messages = channel_messages(f_owner['token'], f_channel['channel_id'], 0)['messages']

    # Check that the message is not pinned
    for message in messages:
        if message['message_id'] == m_id1:
            assert message['is_pinned'] == False

    # Owner pins the message
    message_pin(f_owner['token'], m_id1)

    # Check that the message is pinned
    for message in messages:
        if message['message_id'] == m_id1:
            assert message['is_pinned'] == True


def test_message_pin_already_pinned():
    '''

    ''' 
    clear()


def test_message_unpin_invalid():
    '''

    '''
    clear()


def test_message_unpin_permission():
    '''
    User not flockr owner
    '''
    clear()


def test_message_unpin_already_unpinned():
    '''

    '''
    clear()


            