# Assumptions

## General:
- Parameters are consistent - of one type (and cannot be None)
- Other than auth_register and auth_login, a valid token is required to use every feature

## auth.py:
- Valid emails: emails are case sensitive (i.e. TEST@GMAIL.COM won't work), and only one period is allowed for the domain (no .gov.au)
- Names cannot be whitespace (even if more than 3 characters in length) - handle might break otherwise
- User is automatically logged in once registered (hence token generated)
- A user can access auth_login() even if they are already logged in (new token generated for them)
- An invalid or revoked token is indicated by an empty string ''
- User accounts cannot be deleted (as in data entries deleted) in order to maintain sequential unique id ordering - could add a deactivation status in the future if necessary
- Tokens are JWT encoded (special pytest to test for anti-tampering)
- Tokens become invalidated once user logs out
- Password reset codes are single-use only (invalidated once used)

## channel.py:
- Flockr owner (person with permission_id == 1) has owner permissions for channel_join, channel_addowner, channel_removeowner (they can only add and remove owners while they are members of the channel)
- All members can invite (not restricted to owners) - keyword members excludes Flockr owners who haven't joined yet
- Inviting someone who has already been invited does nothing (no exceptions thrown, no duplicate entries added)
- Joining a channel that a user is already in does nothing (no exceptions thrown, no duplicate entries added)
- channel_messages start index only valid if <= total number of messages
- channel_messages tries to return a maximum of 50 messages (from start to start + 50), and returns an end = -1 if the first message is reached
- channel_messages able to be returned are all messages in a channel, and not only the messages sent after the user has joined
- messages are ordered in original sent order - editing won't change order, but only update content
- The creator of a channel can be removed as an owner if they add an owner who removes them
- channel_leave also removes a user as owner if they are an owner
- A channel (public or private) can have no members if everyone leaves (including owners), but won't be deleted (to maintain sequential unique id ordering), but could add a deactivation status in the future if necessary
- An owner can use channel_removeowner on themselves
- Invalid u_id's for channel_addowner and channel_remove owner raises an AccessError (so a future user with the u_id won't be unintentionally given owner permissions when they register)

## channels.py:
- Users without tokens (or have invalid tokens) are unable to access channels_listall
- Channel names full of whitespace characters are invalid
- Empty channel names are also invalid
- All members include owners

## message.py
- message_id's are unique across all channels
- Not allowed to send empty messages (message_edit removes a message if new message is '')
- White space is allowed for messages
- Message length has to be less than or equal to 1000 characters
- channel_id as parameter must be valid, or else an InputError is raised
- message_id as parameter must be valid, or else an InputError is raised
- Flockr owners not in channel as a member cannot send messages, but can edit/delete messages
- Message remove/edit must be called by original message sender, channel owner or Flockr owner
- Flockr owners not in a channel cannot search messages from that channel (matches reference implementation)
- Substring for search is caps-sensitive
- auth_user has to be a reactor in order to be removed
- Only owners can pin and unpin messages

## user.py:
- User's email length can be 3-20 **inclusive** (i.e 1234567890@123456.com [20 characters])
- User cannot use set\_profile\_name to change the name to itself (i.e changing Rebecca to Rebecca)
- User cannot use set\_email\_name to change the email to itself (i.e changing Andrew@google.com to Andrew@google.com)
- Emails and names with only whitespace count as 'empty' emails/names (i.e '    ' is empty)
- Valid crop dimensions for uploading photo: x coordinates need to be from 0 to width - 1; y coordinates need to be from 0 to height - 1

## other.py:
- Search searches for substring, but the query string is case sensitive

## standup.py:
- Standup length must be greater than 0 seconds.
- Even if user who started the standup has left the channel, the packaged message will still be sent.
- User cannot call standup\_start nor standup\_active in channels they are not a member of.
- If no messages are sent during a standup, the packaged message is not sent at the end of the standup.
- Not allowed to send empty messages during standup.
- The packaged message includes the handles of users.
