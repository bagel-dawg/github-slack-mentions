import re
import os
import slack
from helpers.user_management import import_user, delete_user, modify_blacklist, modify_event, modify_reminder_window

def print_help(help_type):
    print('Executing print_help ...')

    generic_message = "Uh oh! You seem to have mis-typed a command, Here's some help:"

    subscribe_message = """
    Subscribing to Notifications:
    > `/github-notify subscribe <GitHub Username>`
    """

    unsubscribe_message = """
    Un-subscribing to Notifications:
    > `/github-notify unsubscribe`
    """

    settings_events_message = """
    Opt-out of event types:
    > `/github-notify settings events (enable|disable) (pull_request|issue_comment|pull_request_review|pr_reminders)`
    
    Event Types:
    > `pull_request`: Your username is mentioned in the body of a PR.
    > `issue_comment`: Your username is mentioned in an issue or PR comment.
    > `pull_request_review`: You are added as a PR Approver. You will also be notified 
    if your username is mentioned in a review comment.
    > `pr_reminders`: Daily notifications of PRs that have requested your review.

    """
    settings_blacklist = """
    Mute a specific repository:
    > `/github-notify settings blacklist (add|remove) < organization/repository-name >`
    """

    settings_notification_hour = """
    Set the hour (24-hour, in UTC) of reminder notifications:
    > `/github-notify settings reminder_time <0-24>`
    """

    if help_type == 'subscribe':
        help_message = generic_message + subscribe_message
    elif help_type == 'settings':
        help_message = generic_message + settings_events_message + settings_blacklist + settings_notification_hour
    elif help_type == 'settings_events':
        help_message = generic_message + settings_events_message
    elif help_type == 'settings_blacklist':
        help_message = generic_message + settings_blacklist
    elif help_type == 'settings_reminders':
        help_message = generic_message + settings_notification_hour
    else:
        help_message = subscribe_message + unsubscribe_message + settings_events_message + settings_blacklist + settings_notification_hour

    return help_message

def slack_webhook_handler(payload):
    print('Executing slack_webhook_handler ...')
    valid_payloads = [
        'subscribe',
        'unsubscribe',
        'settings',
        'help'
    ]

    if 'text' not in payload:
        response = print_help('')
        return { 'user': payload['user_id'][0], 'response': response }

    if any( item in payload['text'][0]  for item in valid_payloads ):

        # If subscribe command is called, try to register the user
        if re.match(r'^subscribe', payload['text'][0]):
            
            # Split the payload text by space should result 
            # in ['subscribe', 'githubusername']
            # If it doesn't error out.
            gh_username = payload['text'][0].split(' ')
            if len(gh_username) == 2:
                import_user(gh_username[1], payload['user_id'][0])
                response = "%s subscribed to github mentions!" % payload['user_id'][0]
            else:
                response = print_help('subscribe')

        # If unsubscribe command is called, remove the user from the DB
        elif re.match(r'^unsubscribe', payload['text'][0]):
            delete_user(payload['user_id'][0])
            response = 'The github account associated with your Slack ID has been unsubscribed from mentions.'

        # If settings is called, farm out to usermanagement functions based on what you want
        elif re.match(r'settings events (enable|disable) (pull_request|issue_comment|pull_request_review|pr_reminders)$', payload['text'][0]):
            
            payload_items = payload['text'][0].split(' ')
        
            if len(payload_items) == 4:
                state = True if payload_items[2] == 'enable' else False
                event = payload_items[3]
                modify_event(payload['user_id'][0], state, event)
                response = 'Settings updated!'
            else:
                response = print_help('settings_events')                
            

        elif re.match(r'settings blacklist (add|remove)', payload['text'][0]):            
            payload_items = payload['text'][0].split(' ')

            if len(payload_items) == 4:
                state = True if payload_items[2] == 'add' else False
                repo = payload_items[3] 
                modify_blacklist(payload['user_id'][0], state, repo)
                response = 'Blacklist updated!'
            else:
                response = print_help('settings_blacklist')

        elif re.match(r'settings reminder_time', payload['text'][0]):            
            payload_items = payload['text'][0].split(' ')

            if len(payload_items) == 3:
                state = payload_items[2]
                modify_reminder_window(payload['user_id'][0], state)
                response = 'Reminder hour updated!'
            else:
                response = print_help('settings_reminders')

        else:
            response = print_help('settings')
    else:
        response = print_help('generic')


    return { 'user': payload['user_id'][0], 'response': response }