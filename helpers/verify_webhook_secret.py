import hashlib
import hmac
import os
import re
import json

def verify_webhook_secret(signature, payload):

    print(json.dumps(payload, separators=(',',':')).encode())
    print(hmac.new(os.environ["GITHUB_SECRET"].encode(),json.dumps(payload, separators=(',',':')).encode(),hashlib.sha1).hexdigest())

    return hmac.new(os.environ["GITHUB_SECRET"].encode(),
                    json.dumps(payload, separators=(',',':')).encode(),
                    hashlib.sha1).hexdigest() == re.sub('sha1=', '', signature)