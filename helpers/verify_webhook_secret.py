import hashlib
import hmac
import os
import re
import json
from helpers import setup_logger

logger = setup_logger()

def verify_webhook_secret(signature, payload):
    print('Executing verify_webhook_secret ...')
    return hmac.new(os.environ["GITHUB_SECRET"].encode(),
                    json.dumps(payload, separators=(',',':')).encode(),
                    hashlib.sha1).hexdigest() == re.sub('sha1=', '', signature)

def verify_slack_secret(signature, timestamp, payload):
    print('Executing verify_slack_secret ...')

    sig_basestring = 'v0:' + timestamp + ':' + payload

    return 'v0=' + hmac.new(os.environ["SLACK_APP_SIGNING_SECRET"].encode(),
                    sig_basestring.encode(),
                    hashlib.sha256).hexdigest() == signature        