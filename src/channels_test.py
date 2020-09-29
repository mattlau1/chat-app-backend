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

def test_create_invalid_names():
    # create a channel that has more than 20 chracters in name
    long_name = "abcdefghijklmnopqrstuvwxyz"
    with pytest.raises(InputError):
        channels_create("token", long_name, True)
    # edge case
    long_name = "thisnameisverylong00"
    with pytest.raises(InputError):
        channels_create("token", long_name, True)
    clear()
