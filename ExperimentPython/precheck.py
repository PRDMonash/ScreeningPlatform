from log_method import setup_logger
import os

logger = setup_logger('Check Pre-experiment')

def check_files():
    """
    checks if important files are present
    """
    files_to_check = ['Files/Chemicals.csv']
    for file in files_to_check:
        if not os.path.exists(os.path.join(os.getcwd(), file)):
            logger.warning('{} not present!'.format(file))