import os
import requests
import urllib
import json
import hmac
import hashlib

api_endpoint = os.environ["API_GATEWAY_URL"]

headers = { 
    'content-type':'application/json',
    'X-GitHub-Event':'issue_comment'
    }

json_string = {
  "action": "created",
  "repository" : {
    "full_name": "example/ansible"
  },
  "issue": {
    "html_url": "https://github.com/bageltech/test-repository-1/pull/6",
    "title": "Update README.md",
    "user": {
      "login": "bagel-dawg"
    },
    "body": ""
  },
  "comment": {
    "html_url": "https://github.com/bageltech/test-repository-1/pull/6#issuecomment-567334221",
    "user": {
      "login": "bagel-dawg"
    },
    "body": "@bagel-dawg "
  }
}

sha1sum = hmac.new(os.environ["GITHUB_SECRET"].encode(),
                    json.dumps(json_string, separators=(',',':')).encode(),
                    hashlib.sha1).hexdigest()

headers['X-Hub-Signature'] = 'sha1=%s' % sha1sum


r = requests.post(api_endpoint, headers=headers, json=json_string)

print(r.status_code)
print(r.content)