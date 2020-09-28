# Assumptions

## Iteration 1
### General:
- Parameters cannot have None type (assumed to be string retrieved from user input)

### auth.py:
- Valid emails: emails are case sensitive (i.e. TEST@GMAIL.COM won't work)
- User is automatically logged in once registered (hence token generated)
- A user can access auth_login() even if they are already logged in (token generated for them)
- An invalid token is given by an empty string ''

### channel.py:

### channels.py:
