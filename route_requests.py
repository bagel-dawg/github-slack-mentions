import json
from urllib.parse import parse_qs
from helpers.pull_request_handler import pull_request_handler
from helpers.issue_comment_handler import issue_comment_handler
from helpers.pr_review_handler import pr_review_handler
from helpers.slack_notify import notify_slack
from helpers.verify_webhook_secret import verify_webhook_secret
from helpers.slack_webhook_handler import slack_webhook_handler
from helpers.user_management import get_notifiable_users

def response_formated(statusCode, body):
    print('Executing response_formated...')
    response = {}
    headers = {}
    response['statusCode'] = statusCode

    if type(body) is dict:
        headers['Content-Type'] = 'application/json'
        response['body'] = json.dumps(body)
    else:
        headers['Content-Type'] = 'tex/plain' 
        response['body'] = body    

    response['headers'] = headers

    print('Reponse to return:')
    print(response)

    return response


def lambda_handler(event, context):
    print('Executing lamda_handler...')
    headers = event['headers']

    if 'X-Slack-Signature' in headers:
        body = parse_qs(event['body'])
        webhook_response = slack_webhook_handler(body)

        return response_formated(200, { "response_type": "ephemeral", "text": webhook_response['response'] } )
    else:
        body = json.loads(event['body'])

    if not verify_webhook_secret(headers['X-Hub-Signature'], body):
        return response_formated(403, { 'message' : 'X-Hub-Signature invalid.' } )

    if headers['X-GitHub-Event'] == 'pull_request':
        handler_response = pull_request_handler(body)

    elif headers['X-GitHub-Event'] == 'issue_comment':
        handler_response = issue_comment_handler(body)
    
    elif headers['X-GitHub-Event'] == 'pull_request_review':
        handler_response = pr_review_handler(body)
    else:
        return response_formated(200, { 'message' : 'Invalid event, no notifications sent.' } )


    if handler_response['notify_users']:
        notifiable_users = get_notifiable_users(handler_response['notification_users'], headers['X-GitHub-Event'], body['repository']['full_name'])

        if len(notifiable_users) > 0:
            status_code = 200
            post_response = 'Users have been notified!'
            notify_slack(notifiable_users, handler_response['message'])      
        else:
            status_code = 200
            post_response = 'No users to notify'
    else:
        status_code = 200
        post_response = 'No users to notify'

    return response_formated(status_code, post_response)