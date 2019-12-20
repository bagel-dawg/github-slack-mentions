from helpers.parse_usernames import get_usernames_from_string
from helpers.remove_duplicated_users import remove_duplicated_users

def pull_request_handler(body):

    notification_users = []
    msg = ''

    requester = body['pull_request']['user']['login']
    html_link = body['pull_request']['_links']['html']['href']
    link_title = body['pull_request']['title']
    
    if 'requested_reviewer' in body:
        # A review has been requested <http://www.hyperlinkcode.com/|Hyperlink Code>
        notification_users.append(body['requested_reviewer']['login'])
        msg = 'Your review has been requested by %s: <%s|%s>' % ( requester, html_link, link_title )
    if body['action'] == 'opened':
        # A PR has been opened with a body
        notification_users = get_usernames_from_string(body['pull_request']['body'])
        msg = 'You were mentioned in a PR by: %s: <%s|%s>' % ( requester, html_link, link_title )
    if body['action'] == 'edited' and 'body' in body['changes']:
        # An already-opened PR has a change in its body
        notification_users = remove_duplicated_users(body['changes']['body']['from'], body['pull_request']['body'])
        msg = 'You were mentioned in a PR by: %s: <%s|%s>' % ( requester, html_link, link_title )
    
    if len(notification_users) > 0:
        notify_users = True
    else:
        notify_users = False

    return { 'notify_users': notify_users, 'notification_users' : notification_users, 'message' : msg }