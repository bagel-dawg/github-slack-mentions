import os
import slack
from helpers import setup_logger

logger = setup_logger()

def notify_slack(users, message):
    print('Executing notify_slack...')
    sc = slack.WebClient(token=(os.environ["SLACK_BOT_TOKEN"]))

    for user in users:
        sc.chat_postMessage(channel=user, text=message, username='GitHub Notify')