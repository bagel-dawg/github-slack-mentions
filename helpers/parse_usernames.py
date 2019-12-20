import re

def get_usernames_from_string(mention_string):
    return re.findall(r'\B@([a-z0-9](?:-?[a-z0-9]){0,38})', mention_string)