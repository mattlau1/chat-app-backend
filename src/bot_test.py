import pytest
import time
from auth import auth_register
from channel import channel_join, channel_messages, channel_details
from channels import channels_create
from message import message_send
from bot import bot_message_parser, message_prune
from user import user_profile_sethandle
from error import InputError, AccessError
from other import clear

''' Message prune tests '''
def test_bot_message_parser_prune():
    # Check messages have been deleted - and bot sends a temporary message (10s)
    f_owner = auth_register('admin@gmail.com', 'password', 'Admin', 'User')
    channel = channels_create(f_owner['token'], 'Channel', True)
    message_send(f_owner['token'], channel['channel_id'], 'Hello, World!')
    # Invalid commands should just display error, not raise exceptions
    message_send(f_owner['token'], channel['channel_id'], '/prune 5x')
    # Flockr owner sends two messages, bot adds one
    messages = channel_messages(f_owner['token'], channel['channel_id'], 0)['messages']
    assert len(messages) == 3
    # Invalid prune amount (4 maximum including /prune command message)
    message_send(f_owner['token'], channel['channel_id'], '/prune 5')
    # Bot displays error message
    messages = channel_messages(f_owner['token'], channel['channel_id'], 0)['messages']
    assert len(messages) == 5
    # Successful prune
    message_send(f_owner['token'], channel['channel_id'], '/prune 6')
    messages = channel_messages(f_owner['token'], channel['channel_id'], 0)['messages']
    assert len(messages) == 1
    # Bot message should be automatically removed after 10 seconds
    time.sleep(13)
    messages = channel_messages(f_owner['token'], channel['channel_id'], 0)['messages']
    assert len(messages) == 0


def test_message_prune_invalid():
    clear()
    # Register users, create channel and users join
    f_owner = auth_register('admin@gmail.com', 'password', 'Admin', 'User')
    c_owner = auth_register('owner@chanel.com', 'password', 'Chantelle', 'Owner')
    r_user = auth_register('random@user.com', 'password', 'Random', 'User')
    w_user = auth_register('weird@user.com', 'password', 'Weird', 'User')
    
    channel = channels_create(c_owner['token'], 'Channel', True)
    channel_join(r_user['token'], channel['channel_id'])
    channel_join(f_owner['token'], channel['channel_id'])
    
    # Send 3 dummy messages
    message_send(f_owner['token'], channel['channel_id'], 'Message 1')
    message_send(c_owner['token'], channel['channel_id'], 'Message 2')
    message_send(r_user['token'], channel['channel_id'], 'Message 3')
    messages = channel_messages(r_user['token'], channel['channel_id'], 0)['messages']
    assert len(messages) == 3
    
    # Invalid
    with pytest.raises(AccessError):
        message_prune(c_owner['token'] + 'rAnd0M_p@dd1nG', channel['channel_id'], 3)
    with pytest.raises(InputError):
        message_prune(c_owner['token'], channel['channel_id'] + 1000, 3)
    with pytest.raises(AccessError):
        # w_user not in channel
        message_prune(w_user['token'], channel['channel_id'], 3)
    with pytest.raises(AccessError):
        message_prune(r_user['token'], channel['channel_id'], 3)
    with pytest.raises(InputError):
        # Note that normally, requesting the '/prune' command adds another message
        # but in this isolated test case, it doesn't
        message_prune(c_owner['token'], channel['channel_id'], 4)

def test_message_prune_valid():
    clear()
    # Register users, create channel and users join
    f_owner = auth_register('admin@gmail.com', 'password', 'Admin', 'User')
    c_owner = auth_register('owner@chanel.com', 'password', 'Chantelle', 'Owner')
    r_user = auth_register('random@user.com', 'password', 'Random', 'User')

    channel = channels_create(c_owner['token'], 'Channel', True)
    channel_join(r_user['token'], channel['channel_id'])
    channel_join(f_owner['token'], channel['channel_id'])

    # Send 3 dummy messages
    message_send(f_owner['token'], channel['channel_id'], 'Message 1')
    message_send(c_owner['token'], channel['channel_id'], 'Message 2')
    message_send(r_user['token'], channel['channel_id'], 'Message 3')
    messages = channel_messages(r_user['token'], channel['channel_id'], 0)['messages']
    assert len(messages) == 3

    # Valid pruning from Flockr owner
    message_prune(f_owner['token'], channel['channel_id'], 3)
    messages = channel_messages(r_user['token'], channel['channel_id'], 0)['messages']
    assert len(messages) == 0

    # Send 3 dummy messages
    message_send(f_owner['token'], channel['channel_id'], 'Message 1')
    message_send(c_owner['token'], channel['channel_id'], 'Message 2')
    message_send(r_user['token'], channel['channel_id'], 'Message 3')
    messages = channel_messages(r_user['token'], channel['channel_id'], 0)['messages']
    assert len(messages) == 3

    # Valid pruning from Channel owner
    message_prune(c_owner['token'], channel['channel_id'], 3)
    messages = channel_messages(c_owner['token'], channel['channel_id'], 0)['messages']
    assert len(messages) == 0

def test_bot_channel_kick():
    ''' General test for handle since already tested in channel.py '''
    clear()
    # Register users and join channel
    owner = auth_register('admin@gmail.com', 'password', 'Admin', 'User')
    user_profile_sethandle(owner['token'], 'overlord')
    user = auth_register('user@gmail.com', 'password', 'Random', 'User')
    user_profile_sethandle(user['token'], 'naughty_user')
    channel = channels_create(owner['token'], 'My Channel', True)
    channel_join(user['token'], channel['channel_id'])

    # Test for kicking via handle
    # No owner permission - cannot kick owner
    message_send(user['token'], channel['channel_id'], '/kick overlord')
    assert len(channel_details(user['token'], channel['channel_id'])['all_members']) == 2
    # Has owner permission - can kick random user
    message_send(owner['token'], channel['channel_id'], '/kick naughty_user')
    assert len(channel_details(owner['token'], channel['channel_id'])['all_members']) == 1
