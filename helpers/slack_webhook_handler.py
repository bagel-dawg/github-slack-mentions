import re
import os
import slack
from helpers.user_management import import_user, delete_user, modify_blacklist, modify_event

def print_help(help_type):
    print('Executing print_help ...')

    generic_message = "Uh oh! You seem to have mis-typed a command, Here's some help:"

    subscribe_message = """
    ### Subscribing to Notifications ###
    In order to subscribe to your GitHub mentions:
    `/github-notify subscribe <GitHub Username>`

    Example:
    `/github-notify subscribe bagel-dawg`

    """

    unsubscribe_message = """
    ### Un-subscribing to Notifications ###
    In order to unsubscribe to your GitHub mentions:
    `/github-notify unsubscribe`

    You will be identified by your Slack ID.

    """

    settings_events_message = """
    ### Choosing which events to be notified for ###
    Settings for events include:
    `/github-notify settings event (enable|disable) (pull_request|issue_comment|pull_request_review)`
    
    `pull_request` events will notify you when your username is mentioned in the body of a PR.
    `issue_comment` events will notify you when your username is mentioned in an issue or PR comment.
    `pull_request_review` events will notify you when your are added as a PR Approver. You will also be notified 
    if your username is mentioned in a review comment.

    """
    settings_blacklist = """
    ### Blacklist all notifications from defined repositories ###
    Adding repositories to your blacklist will prevent you from getting notified for any of the events 
    that occur in that repository.

    Example usage:
    `/github-notify settings blacklist (add|remove) < organization/repository-name >`

    """


    if help_type == 'subscribe':
        help_message = generic_message + subscribe_message
    elif help_type == 'settings_events':
        help_message = generic_message + settings_events_message
    elif help_type == 'settings_blacklist':
        help_message = generic_message + settings_blacklist
    else:
        help_message = subscribe_message + unsubscribe_message + settings_events_message + settings_blacklist

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
        elif re.match(r'settings events (enable|disable) (pull_request|issue_comment|pull_request_review)$', payload['text'][0]):
            
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
        else:
            response = print_help('generic')
    else:
        response = print_help('generic')


    return { 'user': payload['user_id'][0], 'response': response }