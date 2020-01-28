#from dynamodb_json import json_util as json 
import os
import boto3
from datetime import datetime
from helpers import setup_logger

logger = setup_logger()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])

def import_user(github_username, slack_id):
    logger.info('Executing import_user: %s:%s...') % (github_username, slack_id)
    user_json = { 
        'ghusername' :github_username, 
        'slack_id' : slack_id,
        'events_enabled' : {
            'pull_request' : True,
            'issue_comment' : True,
            'pull_request_review' : True,
            'pr_reminders' : True
        },
        'reminder_window_hour' : 14,
        'repo_blacklist' : []
    }

    table.put_item(
        Item=user_json
    )

def delete_user(slack_id):
    logger.info('Executing delete_user for ID :%s ...') % slack_id
    userdata = retrieve_user_by_slack_id(slack_id)
    logger.debug('Retrieved userdata by slack ID:\n%s') % userdata

    if userdata['user_exists']:
        table.delete_item( Key={ 'ghusername': userdata['userdata']['ghusername'] } )
        logger.debug('GitHub user %s deleted from DB! ') % userdata['userdata']['ghusername']

def retrieve_user_by_github_name(github_username):
    logger.info('Executing retrieve_user_by_github_name: %s ...') % github_username
    response = table.get_item( Key={ 'ghusername': github_username } )
    if 'Item' in response:
        logger.debug('User %s exists in DB!') % github_username
        user_exists = True
        userdata = response['Item']
    else:
        logger.debug('User %s does not exist in DB') % github_username
        user_exists=False
        userdata = {}
    
    logger.debug('Retrieved userdata by GitHub ID:\n%s') % userdata

    return { 'user_exists': user_exists, 'userdata': userdata }

def retrieve_user_by_slack_id(slack_id):
    logger.info('Executing retrieve_user_by_slack_id %s ...') % slack_id
    response = table.query(IndexName='slack_id', KeyConditionExpression=boto3.dynamodb.conditions.Key('slack_id').eq(slack_id))
    if 'Items' in response:
        logger.debug('User %s exists in DB!') % slack_id
        user_exists = True
        userdata = response['Items'][0]
    else:
        logger.debug('User %s does not exist in DB') % slack_id
        user_exists=False
        userdata = {}
    

    logger.debug('Retrieved userdata by Slack ID:\n%s') % userdata
    return { 'user_exists': user_exists, 'userdata': userdata }    

def modify_event(slack_id, state, event):
    logger.info('Executing modify_event %s to %s for slack ID %s...') % (event, state, slack_id)
    userdata = retrieve_user_by_slack_id(slack_id)

    if userdata['user_exists']:
        table.update_item( 
            Key={ 
                'ghusername': userdata['userdata']['ghusername']
            },
            UpdateExpression='SET events_enabled.%s = :state' % event,
            ExpressionAttributeValues = {
                ':state': state,
            }
        )

def modify_reminder_window(slack_id, notification_hour):
    logger.info('Executing modify_reminder_window for %s to hour %s...') % (slack_id, notification_hour)
    userdata = retrieve_user_by_slack_id(slack_id)

    if userdata['user_exists']:
        table.update_item( 
            Key={ 
                'ghusername': userdata['userdata']['ghusername']
            },
            UpdateExpression='SET reminder_window_hour = :state',
            ExpressionAttributeValues = {
                ':state': int(notification_hour),
            }
        )

def modify_blacklist(slack_id, state, repo):
    logger.info('Executing modify_blacklist for repo %s to %s for slack ID %s...') % (repo, state, slack_id)
    userdata = retrieve_user_by_slack_id(slack_id)

    if userdata['user_exists']:
        logger.debug('User already exists in DB, updating.....')
        if state:
            table.update_item( 
                Key={ 
                    'ghusername': userdata['userdata']['ghusername']
                },
                UpdateExpression = 'SET repo_blacklist = list_append(repo_blacklist, :repo)',
                ExpressionAttributeValues = {
                    ':repo': [repo]
                }
            )
        else:
            table.update_item( 
                Key={ 
                    'ghusername': userdata['userdata']['ghusername']
                },
                UpdateExpression = 'REMOVE repo_blacklist[%s]' % userdata['userdata']['repo_blacklist'].index(repo),
            )
    else:
        logger.debug('User doesnt seem to exist in DB already, doing nothing..')

def get_notifiable_users(users, github_event, repository):
    logger.info('Executing get_notifiable_users for users (%s) for the event %s on repository %s ...') % (users, github_event, repository)
    return_users = []

    for user in users:

        response = table.get_item( Key={ 'ghusername': user } )
        if 'Item' in response:
            logger.info('User %s exists in DB!') % user
            user_exists = True
            userdata = response['Item']
        else:
            logger.info('User %s does not exists in db, skipping...') % user
            user_exists=False
            userdata = {}

        if user_exists:
            if userdata['events_enabled'][github_event] and (repository not in userdata['repo_blacklist']):
                logger.debug('User has event %s enabled for the repo %s!') % (github_event, repository)
                if github_event == 'pr_reminders':
                    if userdata['reminder_window_hour'] == datetime.utcnow().hour:
                        logger.debug('Adding user %s to the notifiable users list!') % user
                        return_users.append(userdata['slack_id'])
                else:
                    logger.debug('Adding user %s to the notifiable users list!') % user
                    return_users.append(userdata['slack_id'])
            else:
                logger.debug('User is in database, but has opted out of either the event %s or the repo %s.') % (github_event, repository)
    

    logger.info('Users to be notified:\n%s') % return_users
    return return_users
