from datetime import datetime
from data import data, User, Message, current_time, user_with_token, user_with_id, user_with_handle, channel_with_id
from channel import channel_kick
from error import InputError

bot_status = {
    'active': False,
    'u_id': -1,
}

# change default prefix
def bot_init():
    global bot_status
    # Bot not technically registered
    if bot_status['active']:
        return user_with_id(bot_status['u_id'])
    else:
        # Create new bot
        bot_user = User('flockbot@gmail.com', 'c0mpLicAt3d', 'Flockr', 'Bot')
        bot_user.profile_img_url = 'https://www.pinclipart.com/picdir/big/493-4936596_team-communication-app-on-the-mac-app-store.png'
        data['users'].append(bot_user)
        # Change status
        bot_status = {
            'active': True,
            'u_id': bot_user.u_id,
        }
        return bot_user


def bot_send_message(channel, message):
    '''
    Channel object message string
    '''
    bot_user = bot_init()
    # Bot sends message to channel
    msg = Message(sender=bot_user, message=message, time_created=current_time())
    channel.messages.append(msg)

def bot_help(channel_id):
    ''' Displays help message '''
    bot_msg = '''
    Available commands:
        - /help (displays this message)
        - /kick user_handle (kicks a user from this channel - requires admin permissions)
        - /hangman start
        - /guess char (hangman guess)
        - /poll
        - random dice roll
        - something that reads reacts on its own message
        - bot or channel status (number of members etc)
        - remind function (too many threads?)
    '''
    bot_send_message(channel_with_id(channel_id), bot_msg)

def bot_kick(token, channel_id, message):
    user = user_with_token(token)
    channel = channel_with_id(channel_id)
    try:
        handle = message[6:]
        kick_user = user_with_handle(handle)
        if kick_user is None:
            raise InputError('Please provide a valid user handle!')
        channel_kick(token, channel_id, kick_user.u_id)
        bot_msg = f'⚽️ {kick_user.handle} has been kicked by {user.handle}!'
        bot_send_message(channel, bot_msg)
    except Exception as e:
        bot_msg = f'Failed to kick: {e}'
        bot_send_message(channel, bot_msg)

def bot_time(channel_id):
    bot_user = bot_init()
    channel = channel_with_id(channel_id)
    date_time = datetime.fromtimestamp(current_time())
    bot_msg = f'The current time is {date_time.strftime(r"%A %-d %B %Y, %-I:%M %p")}.'
    bot_send_message(channel, bot_msg)

# For both message_send and message_sendlater
def bot_message_parser(token, channel_id, message):
    if message == '/help':
        bot_help(channel_id)
    elif message == '/time':
        bot_time(channel_id)
    elif message.startswith('/kick'):
        bot_kick(token, channel_id, message)
    elif message.startswith('/guess'):
        pass
        
