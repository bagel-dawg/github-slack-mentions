from helpers.parse_usernames import get_usernames_from_string

def remove_duplicated_users(previous_body, new_body):
    print('Executing remove_duplicated_users ...')
    all_notifiable_users = get_usernames_from_string(new_body)
    already_notified_users = get_usernames_from_string(previous_body)
    return list( set(all_notifiable_users) - set(already_notified_users))