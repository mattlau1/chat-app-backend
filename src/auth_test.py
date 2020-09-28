# Test file for auth.py
from auth import auth_login, auth_logout, auth_register

def test_valid_auth():
    # User 1
    user1_email = "test@gmail.com"
    user1_password = "password"
    auth_register(user1_email, user1_password, "Ben", "Bill")
    user1 = auth_login(user1_email, user1_password)
    assert auth_logout(user1['token']) == {'is_success': True}
