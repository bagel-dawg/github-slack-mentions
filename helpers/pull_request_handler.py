from helpers.parse_usernames import get_usernames_from_string
from helpers.remove_duplicated_users import remove_duplicated_users
from helpers import setup_logger

logger = setup_logger()

def pull_request_handler(body):
    logger.info('Executing pull_request_handler...')
    notification_users = []
    msg = ''

    requester = body['pull_request']['user']['login']
    html_link = body['pull_request']['_links']['html']['href']
    link_title = body['pull_request']['title']
    
    logger.debug('Requester: %s - html_link: %s - Title: %s') ( requester, html_link, link_title )

    if 'requested_reviewer' in body:
        # A review has been requested <http://www.hyperlinkcode.com/|Hyperlink Code>
        logger.debug('A review has been requested for %s') % body['requested_reviewer']['login']
        notification_users.append(body['requested_reviewer']['login'])
        msg = 'Your review has been requested by %s: <%s|%s>' % ( requester, html_link, link_title )
    if body['action'] == 'opened':
        # A PR has been opened with a body
        logger.debug('A PR has been opened')
        notification_users = get_usernames_from_string(body['pull_request']['body'])
        msg = 'You were mentioned in a PR by: %s: <%s|%s>' % ( requester, html_link, link_title )
    if body['action'] == 'edited' and 'body' in body['changes']:
        # An already-opened PR has a change in its body
        logger.debug('A PR body has been edited')
        notification_users = remove_duplicated_users(body['changes']['body']['from'], body['pull_request']['body'])
        msg = 'You were mentioned in a PR by: %s: <%s|%s>' % ( requester, html_link, link_title )
    
    if len(notification_users) > 0:
        notify_users = True
    else:
        notify_users = False

    return { 'notify_users': notify_users, 'notification_users' : notification_users, 'message' : msg }