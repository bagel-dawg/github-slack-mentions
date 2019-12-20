import json

# notifiable_users = { 
#     'bagel-dawg': { 
#         'slack_id' : 'UD92073PS',
#         'events_enabled' : {
#             'pull_request' : True,
#             'issue_comment' : True,
#             'pull_request_review' : True
#         },
#         'repo-blacklist' : []
#     }
# }

def get_notifiable_users(users, github_event, repository):

    return_users = []

    for user in users:
        if (user in notifiable_users):
            if notifiable_users[user]['events_enabled'][github_event] and (repository not in notifiable_users[user]['repo-blacklist']):
                return_users.append(notifiable_users[user]['slack_id'])
    
    return return_users
