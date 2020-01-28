import os
import requests
import urllib
import json
import hmac
import hashlib

api_endpoint = os.environ["API_GATEWAY_URL"]

headers = { 
    'content-type':'application/json',
    'X-GitHub-Event':'pull_request'
    }

json_string = {
  "action": "edited",
  "repository" : {
    "full_name": "example/ansible"
  },
  "pull_request": {
    "title": "Update README.md",
    "user": {
      "login": "throw-away-user-2"
    },
    "body": "this is the new data @bagel-dawg",
    "_links": {
      "html": {
        "href": "https://github.com/bageltech/test-repository-1/pull/11"
      }
    }
  },
  "changes": {
    "body": {
      "from": "this was the original data. "
    }
  }
}

sha1sum = hmac.new(os.environ["GITHUB_SECRET"].encode(),
                    json.dumps(json_string, separators=(',',':')).encode(),
                    hashlib.sha1).hexdigest()

headers['X-Hub-Signature'] = 'sha1=%s' % sha1sum


r = requests.post(api_endpoint, headers=headers, json=json_string)

print(r.status_code)
print(r.content)