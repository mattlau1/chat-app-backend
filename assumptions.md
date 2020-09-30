# Assumptions

## Iteration 1
### General:
- Parameters cannot have None type (assumed to be string retrieved from user input)

### auth.py:
- Valid emails: emails are case sensitive (i.e. TEST@GMAIL.COM won't work), and only one period is allowed for the domain (no .gov.au)
- User is automatically logged in once registered (hence token generated)
- A user can access auth_login() even if they are already logged in (token generated for them)
- An invalid token is given by an empty string ''
- User accounts cannot be deactivated

### channel.py:
- All members can invite (not restricted to owners)
- What if invited user is already in the channel? - No
- Owner can't leave channel if they're the only member?

### channels.py:
- Channel names full of whitespace characters are invalid
- Empty channel names are also invalid
- All members include owners

