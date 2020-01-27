from helpers.parse_usernames import get_usernames_from_string
from helpers.remove_duplicated_users import remove_duplicated_users
from helpers import setup_logger

logger = setup_logger()

def issue_comment_handler(body):
    print('Executing issue_comment_handler...')
    notification_users = []
    msg = ''

    comment_poster = body['comment']['user']['login']
    html_link = body['issue']['html_url']
    link_title = body['issue']['title']       
    
    if body['action'] == 'created':
        # A PR or Issue has a new comment
        notification_users = get_usernames_from_string(body['comment']['body'])
        msg = 'You were mentioned in a PR by %s: <%s|%s>' % (comment_poster, html_link, link_title)
    if body['action'] == 'edited' and 'body' in body['changes']:
        # A PR or Issue has an edited comment
        notification_users = remove_duplicated_users(body['changes']['body']['from'], body['comment']['body'])
        msg = 'You were mentioned in a PR by %s: <%s|%s>' % (comment_poster, html_link, link_title)
    
    if len(notification_users) > 0:
        notify_users = True
    else:
        notify_users = False

    return { 'notify_users': notify_users, 'notification_users' : notification_users, 'message' : msg }