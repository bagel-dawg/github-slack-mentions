import re
from helpers import setup_logger

logger = setup_logger()

def get_usernames_from_string(mention_string):
    print('Executing get_usernames_from_string ...')
    return re.findall(r'\B@([a-z0-9](?:-?[a-z0-9]){0,38})', mention_string)