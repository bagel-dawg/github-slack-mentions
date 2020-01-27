#from dynamodb_json import json_util as json 
import os
import boto3
from datetime import datetime
from helpers import setup_logger

logger = setup_logger()

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ["DYNAMODB_TABLE"])

def import_user(github_username, slack_id):
    print('Executing import_user ...')
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
    print('Executing delete_user ...')
    userdata = retrieve_user_by_slack_id(slack_id)

    if userdata['user_exists']:
        table.delete_item( Key={ 'ghusername': userdata['userdata']['ghusername'] } )

def retrieve_user_by_github_name(github_username):
    print('Executing retrieve_user_by_github_name ...')
    response = table.get_item( Key={ 'ghusername': github_username } )
    if 'Item' in response:
        user_exists = True
        userdata = response['Item']
    else:
        user_exists=False
        userdata = {}
    
    return { 'user_exists': user_exists, 'userdata': userdata }

def retrieve_user_by_slack_id(slack_id):
    print('Executing retrieve_user_by_slack_id ...')
    response = table.query(IndexName='slack_id', KeyConditionExpression=boto3.dynamodb.conditions.Key('slack_id').eq(slack_id))
    if 'Items' in response:
        user_exists = True
        userdata = response['Items'][0]
    else:
        user_exists=False
        userdata = {}
    
    return { 'user_exists': user_exists, 'userdata': userdata }    

def modify_event(slack_id, state, event):
    print('Executing modify_event ...')
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
    print('Executing modify_reminder_window ...')
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
    print('Executing modify_blacklist...')
    userdata = retrieve_user_by_slack_id(slack_id)

    if userdata['user_exists']:

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

def get_notifiable_users(users, github_event, repository):
    print('Executing get_notifiable_users...')
    return_users = []

    for user in users:

        response = table.get_item( Key={ 'ghusername': user } )
        if 'Item' in response:
            user_exists = True
            userdata = response['Item']
        else:
            user_exists=False
            userdata = {}

        if user_exists:
            if userdata['events_enabled'][github_event] and (repository not in userdata['repo_blacklist']):
                if github_event == 'pr_reminders':
                    if userdata['reminder_window_hour'] == datetime.utcnow().hour:
                        return_users.append(userdata['slack_id'])
                else:
                    return_users.append(userdata['slack_id'])
    
    return return_users
