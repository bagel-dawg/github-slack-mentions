import hashlib
import hmac
import os
import re
import json
from helpers import setup_logger

logger = setup_logger()

def verify_webhook_secret(signature, payload):
    logger.info('Executing verify_webhook_secret ...')

    logger.debug('GitHub-provided signature: %s') % re.sub('sha1=', '', signature)
    logger.debug('Calculation payload:\n%s') % json.dumps(payload, separators=(',',':')).encode()

    return hmac.new(os.environ["GITHUB_SECRET"].encode(),
                    json.dumps(payload, separators=(',',':')).encode(),
                    hashlib.sha1).hexdigest() == re.sub('sha1=', '', signature)

def verify_slack_secret(signature, timestamp, payload):
    logger.info('Executing verify_slack_secret ...')

    sig_basestring = 'v0:' + timestamp + ':' + payload

    logger.debug('Slack-provided signature: %s') % signature
    logger.debug('Calculation payload:\n%s') % sig_basestring.encode()   

    return 'v0=' + hmac.new(os.environ["SLACK_APP_SIGNING_SECRET"].encode(),
                    sig_basestring.encode(),
                    hashlib.sha256).hexdigest() == signature        