''' Import required modules '''
import urllib.request
from PIL import Image
from data import valid_email, user_with_id, user_with_token, user_email_list, user_handle_list
from error import InputError, AccessError

def user_profile(token, u_id):
    '''
    Returns information about a specified user.
    Input: token (str), u_id (int)
    Output: dict containing user's id, email, first name, last name, and handle
    '''
    # Retrieve data
    auth_user = user_with_token(token)
    target_user = user_with_id(u_id)

    # Error check
    if auth_user is None:
        # Invalid token
        raise AccessError('Invalid token')
    elif target_user is None:
        # Invalid u_id
        raise InputError('Invalid user')

    return {
        'user': {
            'u_id': target_user.u_id,
            'email': target_user.email,
            'name_first': target_user.name_first,
            'name_last': target_user.name_last,
            'handle_str': target_user.handle,
            'profile_img_url': target_user.profile_img_url,
        }
    }

def user_profile_setname(token, name_first, name_last):
    '''
    Update the authorised user's first and last name
    Input: token (str), name_first (str), name_last (str)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)

    # Error check
    if auth_user is None:
        # Invalid token
        raise AccessError('Invalid token')
    elif len(name_first) not in range(1, 51):
        # name_first length
        raise InputError('First name should be between 1 and 50 characters inclusive')
    elif name_first.isspace():
        # name_first invalid
        raise InputError('First name cannot be empty')
    elif len(name_last) not in range(1, 51):
        # name_last length
        raise InputError('Last name should be between 1 and 50 characters inclusive')
    elif name_last.isspace():
        # name_last invalid
        raise InputError('Last name cannot be empty')

    # Update name
    auth_user.name_first = name_first
    auth_user.name_last = name_last

    return {
    }


def user_profile_setemail(token, email):
    '''
    Update the authorised user's email address
    Input: token (str), email (str)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)

    # Error check
    if auth_user is None:
        # Invalid token
        raise AccessError('Invalid token')
    elif not valid_email(email):
        # Invalid email format
        raise InputError('Invalid email')
    elif email in user_email_list():
        # Email in use
        raise InputError('Email already taken')

    # Update email
    auth_user.email = email

    return {
    }


def user_profile_sethandle(token, handle_str):
    '''
    Update the authorised user's handle (i.e. display name)
    Input: token (str), handle_str (str)
    Output: empty dict
    '''
    # Retrieve data
    auth_user = user_with_token(token)

    # Error check
    if auth_user is None:
        # Invalid token
        raise AccessError('Invalid token')
    elif len(handle_str) not in range(3, 21):
        # Handle length
        raise InputError('Handle must be between 3 and 20 characters')
    elif handle_str.isspace():
        # Invalid handle
        raise InputError('Invalid handle')
    elif handle_str in user_handle_list():
        # Handle in use
        raise InputError('Handle already taken')

    # Update handle
    auth_user.handle = handle_str

    return {
    }


def user_profile_uploadphoto(token, url_root, img_url, x_start, y_start, x_end, y_end):
    '''
    Helper function for cropping the image with url within provided bounds,
    and setting this image as their profile picture.
    Input: token (str), url_root (root of url - str), img_url (str),
           x_start (int), y_start (int), x_end (int), y_end (int)
    Output: empty dict
    '''
    auth_user = user_with_token(token)
    if auth_user is None:
        raise AccessError('Invalid token')
    
    # Retrieve image
    image_name = f'static/{auth_user.handle}.jpg'
    try:
        urllib.request.urlretrieve(img_url, image_name)
    except urllib.request.URLError:
        raise InputError('Invalid image url')
    
    # Crop and save image
    try:
        img = Image.open(image_name)
        width, height = img.size
    except:
        raise InputError('Invalid image url')
    if not valid_crop_dimensions(width, height, x_start, y_start, x_end, y_end):
        raise InputError(f'Invalid image dimensions provided. \
            Original image has width {width} and height {height}.')
    img = img.crop((x_start, y_start, x_end, y_end))
    img.save(image_name)
    
    # Update profile pic
    auth_user.profile_img_url = url_root + image_name
    
    return {
    }

def valid_crop_dimensions(width, height, x_start, y_start, x_end, y_end):
    '''
    Helper function for user_profile_uploadphoto to check for valid crop dimensions
    '''
    # x coordinates must be from 0 to width
    if x_start not in range(width + 1) or x_end not in range(width + 1):
        return False
    # y coordinates must be from 0 to height
    if y_start not in range(height + 1) or y_end not in range(height + 1):
        return False
    # Width/height can't be 0 pixels in length
    if x_start == x_end or y_start == y_end:
        return False
    return True
