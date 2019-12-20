import json
from helpers.pull_request_handler import pull_request_handler
from helpers.issue_comment_handler import issue_comment_handler
from helpers.pr_review_handler import pr_review_handler
from helpers.slack_notify import notify_slack
from helpers.get_notifiable_users import get_notifiable_users
from helpers.verify_webhook_secret import verify_webhook_secret

def lambda_handler(event, context):
    headers = event['headers']
    body = event['body']

    if not verify_webhook_secret(headers['X-Hub-Signature'], body):
        return {
            'statusCode': 403,
            'body': 'Unauthorized'
        }

    if headers['X-GitHub-Event'] == 'pull_request':
        handler_response = pull_request_handler(body)

    elif headers['X-GitHub-Event'] == 'issue_comment':
        handler_response = issue_comment_handler(body)
    
    elif headers['X-GitHub-Event'] == 'pull_request_review':
        handler_response = pr_review_handler(body)
    else:

        return {
          'statusCode': 400,
          'body': 'X-GitHub-Event header is not supported: %s' % headers['X-GitHub-Event']
        }

    if handler_response['notify_users']:
        notifiable_users = get_notifiable_users(handler_response['notification_users'], headers['X-GitHub-Event'], body['repository']['full_name'])

        notify_slack(notifiable_users, handler_response['message'])
        status_code = 200
        post_response = 'Users have been notified!'
    else:
        status_code = 200
        post_response = 'No users to notify'

    return {
        'statusCode': status_code,
        'body': post_response
    }
