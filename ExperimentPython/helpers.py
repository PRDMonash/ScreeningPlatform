from log_method import setup_logger

logger = setup_logger('Helper')

def isfloat(x):
    """ Checks if value is float. Returns Boolean. True if value is float"""
    try:
        a = float(x)
    except ValueError:
        logger.warning('\tError: No change, entry needs to be a number')
        return False
    else:
        return True