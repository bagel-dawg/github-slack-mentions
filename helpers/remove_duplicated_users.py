from helpers.parse_usernames import get_usernames_from_string
from helpers import setup_logger

logger = setup_logger()

def remove_duplicated_users(previous_body, new_body):
    logger.info('Executing remove_duplicated_users ...')

    logger.debug('Updated string:\n%s') % new_body
    logger.debug('Previous string:\n%s') % previous_body
 
    all_notifiable_users = get_usernames_from_string(new_body)
    already_notified_users = get_usernames_from_string(previous_body)

    logger.debug('Users not yet mentioned in new_string:\n %s') % list( set(all_notifiable_users) - set(already_notified_users))

    return list( set(all_notifiable_users) - set(already_notified_users))