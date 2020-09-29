# Test file for channels.py

import pytest
from channels import *
from error import InputError

def test_create_valid_names():
    # create channel and set public to true
    channels_create("token", "FirstChannel", True)
    channels_create("token", "UNSW discussion",  True)
    channels_create("token", "Private", False)
    clear()

def test_create_invalid_names():
    # # create a channel that has more than 20 chracters in name
    # with pytest.raises(InputError):
    #     channels_create("token", "", True)
