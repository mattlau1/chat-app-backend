# Assumptions

## Iteration 1
### General:
- Parameters are consistent - of one type (and cannot be None)

### auth.py:
- Valid emails: emails are case sensitive (i.e. TEST@GMAIL.COM won't work), and only one period is allowed for the domain (no .gov.au)
- Names cannot be whitespace (even if more than 3 characters in length) - handle might break otherwise
- User is automatically logged in once registered (hence token generated)
- A user can access auth_login() even if they are already logged in (new token generated for them)
- An invalid or revoked token is indicated by an empty string ''
- User accounts cannot be deleted (as in data entries deleted) in order to maintain sequential unique id ordering - could add a deactivation status in the future if necessary

### channel.py:
- Flockr owner (person with u_id == 1) has owner permissions for channel_join, channel_addowner, channel_removeowner (they can only add and remove owners while they are members of the channel)
- All members can invite (not restricted to owners) - keyword members excludes Flockr owners who haven't joined yet
- Inviting someone who has already been invited does nothing (no exceptions thrown, no duplicate entries added)
- Joining a channel that a user is already in does nothing (no exceptions thrown, no duplicate entries added)
- channel_messages start index only allows valid indices: i.e. index 0 and 1 but not 2 if there are two messages in channel (start index < number of messages)
- channel_messages tries to return a maximum of 50 messages (from start to start + 50), and returns an end = -1 if the first message is reached
- The creator of a channel can be removed as an owner if they add an owner who removes them
- channel_leave also removes a user as owner if they are an owner
- A channel (public or private) can have no members if everyone leaves (including owners), but won't be deleted (to maintain sequential unique id ordering), but could add a deactivation status in the future if necessary
- For storing member/owner data, only their unique id is stored - for ease of retrieving future name updates
- An owner can use channel_removeowner on themselves
- Invalid u_id's for channel_addowner and channel_remove owner raises an AccessError (so a future user with the u_id won't be unintentionally given owner permissions when they register)

### channels.py:
- Users without tokens (or have invalid tokens) are unable to access channels_listall
- Channel names full of whitespace characters are invalid
- Empty channel names are also invalid
- All members include owners

### user.py:
- User cannot use set_profile_name to change the name to itself (for example changing Rebecca to Rebecca)
- User cannot use set_email_name to change the email to itself
