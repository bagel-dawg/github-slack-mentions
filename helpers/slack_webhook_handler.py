import re
import os
import slack
from helpers.user_management import import_user, delete_user, modify_blacklist, modify_event, modify_reminder_window
from helpers import setup_logger

logger = setup_logger()

def print_help(help_type):
    logger.info('Executing print_help ...')

    logger.debug('help_type: %s') % help_type

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
        logger.debug('help_type: subscribe, setting help message to: generic, subscribe_message')
        help_message = generic_message + subscribe_message
    elif help_type == 'settings':
        logger.debug('help_type: settings, setting help message to: generic, settings_events_message, settings_blacklist, settings_notification_hour')
        help_message = generic_message + settings_events_message + settings_blacklist + settings_notification_hour
    elif help_type == 'settings_events':
        logger.debug('help_type: settings_events, setting help message to: generic, settings_events_message')
        help_message = generic_message + settings_events_message
    elif help_type == 'settings_blacklist':
        logger.debug('help_type: settings_blacklist, setting help message to: generic, settings_blacklist')
        help_message = generic_message + settings_blacklist
    elif help_type == 'settings_reminders':
        logger.debug('help_type: settings_reminders, setting help message to: generic, settings_notification_hour')
        help_message = generic_message + settings_notification_hour
    else:
        logger.debug('help_type generic, setting help message to: subscribe_message, unsubscribe_message, settings_events_message, settings_blacklist, settings_notification_hour')
        help_message = subscribe_message + unsubscribe_message + settings_events_message + settings_blacklist + settings_notification_hour

    logger.debug('Final help message:\n%s') % help_message
    return help_message

def slack_webhook_handler(payload):
    logger.info('Executing slack_webhook_handler ...')
    valid_payloads = [
        'subscribe',
        'unsubscribe',
        'settings',
        'help'
    ]

    if 'text' not in payload:
        logger.debug('Slack bot recieved an empty string, print generic help message')
        response = print_help('')
        return { 'user': payload['user_id'][0], 'response': response }

    if any( item in payload['text'][0]  for item in valid_payloads ):

        logger.debug('Slack bot recieved a payload:\n%s') % payload['text'][0]

        # If subscribe command is called, try to register the user
        if re.match(r'^subscribe', payload['text'][0]):
            
            logger.debug('Payload matched ^subscribe regex')

            # Split the payload text by space should result 
            # in ['subscribe', 'githubusername']
            # If it doesn't error out.
            gh_username = payload['text'][0].split(' ')
            if len(gh_username) == 2:
                logger.debug('payload matched expected syntax, importing user..')
                import_user(gh_username[1], payload['user_id'][0])
                response = "%s subscribed to github mentions!" % payload['user_id'][0]
            else:
                logger.debug('subscribe regex matched, but the syntax afterwards was malformed.')
                response = print_help('subscribe')

        # If unsubscribe command is called, remove the user from the DB
        elif re.match(r'^unsubscribe', payload['text'][0]):

            logger.debug('Payload matched ^unsubscribe regex, unsubscribing user based on slack ID: %s') % payload['user_id'][0]
            delete_user(payload['user_id'][0])
            response = 'The github account associated with your Slack ID has been unsubscribed from mentions.'

        # If settings is called, farm out to usermanagement functions based on what you want
        elif re.match(r'settings events (enable|disable) (pull_request|issue_comment|pull_request_review|pr_reminders)$', payload['text'][0]):
            
            logger.debug('Payload matched a valid setting syntax! ')    
            payload_items = payload['text'][0].split(' ')
        
            logger.debug('payload items parsed: %s') % payload_items

            if len(payload_items) == 4:
                state = True if payload_items[2] == 'enable' else False
                event = payload_items[3]
                modify_event(payload['user_id'][0], state, event)
                response = 'Settings updated!'
            else:
                logger.debug('Payload parsed, but doesnt contain correct number of arguments, pritning settings_event help message')
                response = print_help('settings_events')                
            

        elif re.match(r'settings blacklist (add|remove)', payload['text'][0]):            
            logger.debug('Payload matched valid settings blacklist regex')

            payload_items = payload['text'][0].split(' ')

            logger.debug('payload items parsed: %s') % payload_items

            if len(payload_items) == 4:
                state = True if payload_items[2] == 'add' else False
                repo = payload_items[3] 
                modify_blacklist(payload['user_id'][0], state, repo)
                response = 'Blacklist updated!'
            else:
                logger.debug('Payload parsed, but doesnt contain correct number of arguments, pritning settings_blacklist help message')
                response = print_help('settings_blacklist')

        elif re.match(r'settings reminder_time', payload['text'][0]):
            logger.debug('Payload matched valid settings reminder_time regex')            
            payload_items = payload['text'][0].split(' ')
            logger.debug('payload items parsed: %s') % payload_items

            if len(payload_items) == 3:
                state = payload_items[2]
                modify_reminder_window(payload['user_id'][0], state)
                response = 'Reminder hour updated!'
            else:
                logger.debug('Payload parsed, but doesnt contain correct number of arguments, pritning settings_reminders help message')
                response = print_help('settings_reminders')

        else:
            logger.debug('Payload was valid, but didnt match any valid regexes ( %s ). Printing generic settings help') % valid_payloads
            response = print_help('settings')
    else:
        logger.debug('Payload does not contain a valid payload ( %s ), printing generic help message') % valid_payloads
        response = print_help('generic')


    return { 'user': payload['user_id'][0], 'response': response }