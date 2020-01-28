import json
from urllib.parse import parse_qs
from helpers.pull_request_handler import pull_request_handler
from helpers.issue_comment_handler import issue_comment_handler
from helpers.pr_review_handler import pr_review_handler
from helpers.slack_notify import notify_slack
from helpers.verify_webhook_secret import verify_webhook_secret, verify_slack_secret
from helpers.slack_webhook_handler import slack_webhook_handler
from helpers.user_management import get_notifiable_users
from helpers import setup_logger

logger = setup_logger()

def response_formated(statusCode, body):
    logger.info('Executing response_formated...')
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

    logger.debug('HTTP Response Headres:\n%s') % headers
    logger.debug('HTTP Reponse:\n%s') % response

    return response


def lambda_handler(event, context):
    logger.info('Executing lamda_handler...')
    headers = event['headers']

    logger.debug('Incomming HTTP Headers:\n%s') % headers
    logger.debug('Incomming HTTP Body (RAW):\n%s') % event['body']

    if 'X-Slack-Signature' in headers:
        logger.debug('Incoming HTTP header contains X-Slack-Signature, must be from slack..')

        body = parse_qs(event['body'])
        logger.debug('URL Encoded body:\n%s') % body

        if verify_slack_secret(headers['X-Slack-Signature'], headers['X-Slack-Request-Timestamp'],event['body']):
            logger.debug('Slack secret verified! ')
            webhook_response = slack_webhook_handler(body)
            return response_formated(200, { "response_type": "ephemeral", "text": webhook_response['response'] } )
        else:
            logger.debug('Slack secret invalid, exiting...')
            return response_formated(200, { 'message' : 'X-Slack-Signature invalid.' } )
    else:
        body = json.loads(event['body'])
        logger.debug('Incomming HTTP Body (JSON):\n%s') % body

    if not verify_webhook_secret(headers['X-Hub-Signature'], body):
        logger.debug('Github signature invalid, exiting...') 
        return response_formated(403, { 'message' : 'X-Hub-Signature invalid.' } )

    if headers['X-GitHub-Event'] == 'pull_request':
        handler_response = pull_request_handler(body)

    elif headers['X-GitHub-Event'] == 'issue_comment':
        handler_response = issue_comment_handler(body)
    
    elif headers['X-GitHub-Event'] == 'pull_request_review':
        handler_response = pr_review_handler(body)
    else:
        logger.debug('X-GitHub-Event doesnt contain an actionable event, exiting...')
        return response_formated(200, { 'message' : 'Invalid event, no notifications sent.' } )


    if handler_response['notify_users']:
        logger.debug('Users mentioned in event:\n%s') % handler_response['notification_users']
        notifiable_users = get_notifiable_users(handler_response['notification_users'], headers['X-GitHub-Event'], body['repository']['full_name'])

        if len(notifiable_users) > 0:
            status_code = 200
            post_response = 'Users have been notified!'
            notify_slack(notifiable_users, handler_response['message'])      
        else:
            status_code = 200
            post_response = 'No users to notify'
            logger.debug('No users to notify from this event, exiting..')
    else:
        status_code = 200
        post_response = 'No users to notify'
        logger.debug('No users to notify from this event, exiting..')

    return response_formated(status_code, post_response)