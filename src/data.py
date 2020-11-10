''' Import required modules '''
from threading import Timer
from datetime import datetime
import re
import hashlib
import jwt

# Private key for jwt encoding and decoding
PRIVATE_KEY = 'aHR0cHM6Ly95b3V0dS5iZS9kUXc0dzlXZ1hjUQ=='


################
### Database ###
################
data = {
    # users - array of User objects
    'users': [],
    # channels - array of Channel objects
    'channels': [],
    # Stores the latest message_id used across all channels
    'latest_message_id': 0,
    # Valid reset codes
    'valid_reset_codes': [],
}


################################
### General helper functions ###
################################
def valid_email(email):
    '''
    Checks to see if an email is in a valid email format
    Returns match object for input email (str)
    '''
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    return re.search(regex, email)

def current_time():
    '''
    Returns the current time as a UNIX timestamp (int)
    '''
    return int(datetime.timestamp(datetime.now()))


##################################
### Helper functions for users ###
##################################
class User:
    '''
    Class for a User
    '''
    # pylint: disable=too-many-instance-attributes
    # 8 attributes reasonable

    def __init__(self, email, password, name_first, name_last):
        '''
        Constructor method for a User
            u_id - unique integer (stored sequentially starting from index 0)
            email - string
            password - string
            name_first - string
            name_last - string
            handle - string
            permission_id - int
            token - string
        '''
        # Save passed parameters
        self.email = email
        self.password = encrypt_string(password)
        self.name_first = name_first
        self.name_last = name_last
        # Generate extra parameters
        self.profile_img_url = ''
        self.u_id = len(data['users'])
        self.handle = self.generate_handle()
        self.token = self.generate_token()
        self.permission_id = 1 if len(data['users']) == 0 else 2

    def generate_handle(self):
        '''
        Generates a unique handle for a given user
        Input: User object
        Output: handle_string (str)
        '''
        # First 20 characters of concatenation of name_first and name_last
        handle_string = (self.name_first.lower() + self.name_last.lower())[:20]
        # Ensure unique by appending u_id to front
        while handle_string in user_handle_list():
            handle_string = (str(self.u_id) + handle_string)[:20]
        return handle_string

    def generate_token(self):
        '''
        Generates a JSON Web Token (JWT) encoded token for a given user
        Input: User object
        Output: JWT-encoded token (str)
        '''
        return jwt_encode_payload({'u_id': self.u_id})

    def update_password(self, new_password):
        '''
        Updates the password for a User object
        Input: User object, new_password (string)
        No output
        '''
        self.password = encrypt_string(new_password)

    def verify_password(self, check_password):
        '''
        Returns whether a password is correct
        Input: User object, check_password (string)
        Output: True or False (bool)
        '''
        return self.password == encrypt_string(check_password)

def jwt_encode_payload(payload):
    '''
    JWT encodes a given payload
    Input: payload (dict)
    Output: JWT-encoded string (str)
    '''
    return jwt.encode(payload, PRIVATE_KEY, algorithm='HS256').decode('utf-8')

def jwt_decode_string(string):
    '''
    Attempts to decode a given JWT-encoded string
    Input: JWT-encoded string (str)
    Output: payload (dict)
    '''
    return jwt.decode(string.encode('utf-8'), PRIVATE_KEY, algorithms=['HS256'])

def encrypt_string(string):
    '''
    Encrypts a given string
    Input: String (str)
    Output: Encrypted string (str)
    '''
    return hashlib.sha256(string.encode()).hexdigest()

def user_email_list():
    '''
    Returns a list containing all the user emails (str)
    '''
    return [user.email for user in data['users']]

def user_handle_list():
    '''
    Returns a list containing all the user handles (str)
    '''
    return [user.handle for user in data['users']]

def user_with_email(email):
    '''
    Tries to return User object with specified email address (str), returning None if not found
    '''
    for user in data['users']:
        if user.email == email:
            return user
    return None

def user_with_id(u_id):
    '''
    Tries to return User object with specified user id (int), returning None if not found
    '''
    if 0 <= u_id < len(data['users']):
        return data['users'][u_id]
    return None

def user_with_token(token):
    '''
    Tries to return User object with specified token (str), returning None if not found
    '''
    try:
        # Decode token and pass user id to user_with_id()
        payload = jwt_decode_string(token)
        u_id = payload['u_id']
        # Check for valid session
        if data['users'][u_id].token != '':
            return user_with_id(payload['u_id'])
        return None
    except:
        return None

def user_with_handle(handle):
    '''
    Tries to return User object with specified handle (str), returning None if not found
    '''
    for user in data['users']:
        if user.handle == handle:
            return user
    return None


##################################################
### Helper functions for channels and messages ###
##################################################
class Channel:
    '''
    Class for a channel
    '''
    def __init__(self, channel_creator, name, is_public):
        '''
        Constructor method for a Channel
            channel_id - unique integer (stored sequentially starting from index 0)
            name - string
            is_public - boolean
            owner_members - array of User objects
            all_members - array of User objects
            messages - array of Message objects
            standup_status - dictionary containing is_active (bool),
                             time_finish (UNIX timestamp int), initiator (User object),
                             queued_messages (list of Message objects)
        '''
        # Save passed parameters
        self.name = name
        self.is_public = is_public
        # Generate extra parameters
        self.channel_id = len(data['channels'])
        self.owner_members = [channel_creator,]
        self.all_members = [channel_creator,]
        self.messages = []
        self.standup_status = {
            'is_active': False,
            'time_finish': None,
            'initiator': None,
            'queued_messages': [],
        }

    def start_standup(self, initiator, length):
        end_time = current_time() + length
        self.standup_status = {
            'is_active': True,
            'time_finish': end_time,
            'initiator': initiator,
            'queued_messages': [],
        }
        # Threading to end standup after 'length' seconds has passed
        t = Timer(length, self.end_standup)
        t.start()
        return end_time

    def end_standup(self):
        # Send packaged message if there are any messages
        initiator = self.standup_status['initiator']
        standup_messages = self.standup_status['queued_messages']
        if standup_messages:
            message = '\n'.join(f'{msg.sender.handle}: {msg.message}' for msg in standup_messages)
            packaged_msg = Message(sender=initiator, message=message, time_created=current_time())
            self.messages.append(packaged_msg)
        # Reset standup_status
        self.standup_status = {
            'is_active': False,
            'time_finish': None,
            'initiator': None,
            'queued_messages': [],
        }


class Message:
    '''
    Class for a message
    '''
    def __init__(self, sender, message, time_created):
        '''
        Constructor method for a Message
            message_id - unique integer
            sender - User object
            time_created - UNIX timestamp (int)
            message - string
            reacts - array of React objects
            is_pinned - boolean
        '''
        # Save passed parameters
        self.sender = sender
        self.message = message
        # Generate extra parameters
        self.message_id = data['latest_message_id']
        data['latest_message_id'] += 1
        self.time_created = time_created
        self.reacts = []
        self.is_pinned = False

class React:
    '''
    Class for a message react
    '''
    def __init__(self, react_id, reactor):
        '''
        Constructor method for a React
            react_id - unique integer
            reactors - array of User objects
        '''
        self.react_id = react_id
        self.reactors = [reactor,]


def channel_with_id(channel_id):
    '''
    Extracts information about a specified channel (by id)
    Tries to return channel (dict) with specified channel id (int), returning None if not found
    '''
    if 0 <= channel_id < len(data['channels']):
        return data['channels'][channel_id]
    return None

def channel_with_message_id(message_id):
    '''
    Tries to return the channel (Channel object) containing the
    message with specified message_id (int), returning None if not found
    '''
    for channel in data['channels']:
        for message in channel.messages:
            if message.message_id == message_id:
                return channel
    return None

def message_with_message_id(message_id):
    '''
    Tries to return the Message object corresponding to a given message_id (int),
    returning None if not found
    '''
    channel = channel_with_message_id(message_id)
    if channel is not None:
        for message in channel.messages:
            if message.message_id == message_id:
                return message
    return None
