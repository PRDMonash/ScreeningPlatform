import logging

def setup_logger(name, filename = 'logfile.txt', level = logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    formatter = logging.Formatter('%(levelname)s\t|\t%(asctime)s\t\t%(message)s (%(name)s)')

    file_handler = logging.FileHandler(filename)
    file_handler.setFormatter(formatter)

    print_handler = logging.StreamHandler()
    print_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(print_handler)
    
    return logger