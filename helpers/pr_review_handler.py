from helpers.parse_usernames import get_usernames_from_string
from helpers.remove_duplicated_users import remove_duplicated_users

def pr_review_handler(body):

    notification_users = []
    msg = ''

    if body['action'] == 'submitted':
        
        reviewer = body['review']['user']['login']
        html_link = body['pull_request']['_links']['html']['href']
        link_title = body['pull_request']['title']
        
        notification_users.append(body['pull_request']['user']['login'])
        if body['review']['state'] == 'approved':
            msg = 'Your PR has been approved by %s: <%s|%s>' % (reviewer, html_link, link_title)
        elif body['review']['state'] == 'changes_requested':
            msg = '%s has requested changes on your PR: <%s|%s>' % (reviewer, html_link, link_title)
        elif body['review']['state'] == 'commented':
            msg = '%s has commented on your PR: <%s|%s>' % (reviewer, html_link, link_title) 

    if len(notification_users) > 0:
        notify_users = True
    else:
        notify_users = False

    return { 'notify_users': notify_users, 'notification_users' : notification_users, 'message' : msg }