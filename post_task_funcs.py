from email_utils import send_recovery_email
from mongo_utils import save_user_to_db
from logging_utils import log_error, log_success, log_info


def post_create_user(user_data, verbose=False):
    saved_user_data = dict(list(user_data.items())[:-1])
    if not save_user_to_db(saved_user_data):
        log_error("Failed to save user to database")
        return False

    send_recovery_email(user_data['RecoveryEmail'], user_data['Username'], user_data['Password'])
    log_success(f"User {user_data['Username']} created successfully.")