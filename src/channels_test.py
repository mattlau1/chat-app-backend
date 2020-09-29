# Test file for channels.py

import pytest
from error import InputError, AccessError
from channels import channels_list, channels_listall, channels_create
from other import clear

def test_create_valid_names():
    # create channel and set public to true
    channels_create("token", "FirstChannel", True)
    channels_create("token", "UNSW discussion",  True)
    channels_create("token", "Private", False)
    clear()

def test_create_long_names():
    # create a channel that has more than 20 characters (max length) in name
    long_name = "abcdefghijklmnopqrstuvwxyz"
    with pytest.raises(InputError):
        channels_create("token", long_name, True)
    long_name = "thisnameisverylong000"
    with pytest.raises(InputError):
        channels_create("token", long_name, True)
    long_name = "ijxiqwji9xq9iqdjim9dwq89n189819me781neuensa9xaj9xd"
    with pytest.raises(InputError):
        channels_create("token", long_name, False)
    clear()

def test_create_empty_name():
    with pytest.raises(InputError):
        channels_create("token", '', True)
    with pytest.raises(InputError):
        channels_create("token", '', False)
    clear()

def test_create_whitespace_name():
    with pytest.raises(InputError):
        channels_create("token", ' ', True)
    with pytest.raises(InputError):
        channels_create("token", '          ', True)
    with pytest.raises(InputError):
        channels_create("token", '      ', False)
    clear()