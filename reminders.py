import json
import os
from github import Github
from helpers.slack_notify import notify_slack
from helpers.user_management import get_notifiable_users

def lambda_handler(event, context):
    print('Executing lamda_handler...')
    
    GH_USERNAME = os.environ["GH_USERNAME"]
    GH_PAT = os.environ["GH_PAT"]

    g = Github(GH_USERNAME, GH_PAT)

    org_repos = g.get_organization(os.environ["GH_ORG"]).get_repos()

    users_to_notify = {}

    # Obtain all open PRs for the defined organization
    for repo in org_repos:
        open_prs = repo.get_pulls(state='open')

        # Find all PRs that are requesting at least one user reviewer
        for pr in open_prs:
            for requested_review in pr.get_review_requests()[0]:

                # Retrieve and check if the retrieved user is notifiable for this type of event
                notifiable_users = get_notifiable_users([requested_review.login], 'pr_reminders', repo.full_name)
                if notifiable_users:
                    for notifiable_user in notifiable_users:
                        # Create a dict of users to notify so we can notify them all at once in a loop later on.
                        if notifiable_user not in users_to_notify:
                            users_to_notify[notifiable_user] = []
                        
                        users_to_notify[notifiable_user].append( { 'pr_title': pr.title, 'pr_link': pr.html_url } )
    
    for slack_id,prs in users_to_notify.items():
        slack_message = """Here's your daily report of open Pull Request reviews! \nYour review has been requested on the following Pull Requests:\n"""
        
        for pr in prs:
            slack_message = slack_message + """<%s|%s> \n""" % ( pr['pr_link'], pr['pr_title'] )

        notify_slack( [slack_id], slack_message )

    return True
