''' Import required modules '''
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
        self.password = encrypt_password(password)
        self.name_first = name_first
        self.name_last = name_last
        # Generate extra parameters
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
        return jwt.encode({'u_id': self.u_id}, PRIVATE_KEY, algorithm='HS256').decode('utf-8')

    def verify_password(self, check_password):
        '''
        Returns whether a password is correct
        Input: User object, check_password (string)
        Output: True or False (bool)
        '''
        return self.password == encrypt_password(check_password)


def encrypt_password(password):
    '''
    Encrypts a given password
    Input: password (str)
    Output: Encrypted password (str)
    '''
    return hashlib.sha256(password.encode()).hexdigest()

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
        payload = jwt.decode(token.encode('utf-8'), PRIVATE_KEY, algorithms=['HS256'])
        u_id = payload['u_id']
        # Check for valid session (future iterations?)
        if data['users'][u_id].token != '':
            return user_with_id(payload['u_id'])
        return None
    except:
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
        '''
        # Save passed parameters
        self.name = name
        self.is_public = is_public
        # Generate extra parameters
        self.channel_id = len(data['channels'])
        self.owner_members = [channel_creator,]
        self.all_members = [channel_creator,]
        self.messages = []


class Message:
    '''
    Class for a message
    '''
    def __init__(self, sender, message):
        '''
        Constructor method for a Message
            message_id - unique integer
            sender - User object
            time_created - UNIX timestamp (float)
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
        self.time_created = datetime.timestamp(datetime.now())
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
