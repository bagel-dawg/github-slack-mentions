from helpers.parse_usernames import get_usernames_from_string
from helpers.remove_duplicated_users import remove_duplicated_users
from helpers import setup_logger

logger = setup_logger()

def pr_review_handler(body):
    logger.info('Executing pr_review_handler ...')
    notification_users = []
    msg = ''

    if body['action'] == 'submitted':
        logger.debug('A PR review has been submitted! ')
        reviewer = body['review']['user']['login']
        html_link = body['pull_request']['_links']['html']['href']
        link_title = body['pull_request']['title']
        pr_author = body['pull_request']['user']['login']
        
        logger.debug('Reviewer: %s - PR Author: %s - html_link: %s - Title: %s') ( reviewer, pr_author,  html_link, link_title )

        notification_users.append(body['pull_request']['user']['login'])
        if body['review']['state'] == 'approved':
            logger.debug('PR has been approved')
            msg = 'Your PR has been approved by %s: <%s|%s>' % (reviewer, html_link, link_title)
        elif body['review']['state'] == 'changes_requested':
            logger.debug('PR has changes requested')
            msg = '%s has requested changes on your PR: <%s|%s>' % (reviewer, html_link, link_title)
        elif body['review']['state'] == 'commented':
            logger.debug('PR not approved or change requested, but be commented on...')
            # If the user commenting (reviewer) is also the owned of the PR, do not notify user
            if reviewer == pr_author:
                logger.debug('Reviewer (%s) and PR author (%s) are the same, removing from notification_users') % ( reviewer, pr_author )
                notification_users.remove(pr_author)
            else:
              msg = '%s has commented on your PR: <%s|%s>' % (reviewer, html_link, link_title) 

    if len(notification_users) > 0:
        notify_users = True
    else:
        notify_users = False

    return { 'notify_users': notify_users, 'notification_users' : notification_users, 'message' : msg }