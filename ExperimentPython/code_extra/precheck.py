from code_extra.log_method import setup_logger
import os
import smtplib

logger = setup_logger('Check Pre-experiment')

def check_files():
    """
    checks if important files are present
    """
    files_to_check = ['Files/Chemicals.csv']
    for file in files_to_check:
        if not os.path.exists(os.path.join(os.getcwd(), file)):
            logger.warning('{} not present!'.format(file))

def check_Emailconnection():
    '''Checks the SMTP connection
    checks for SMTP status code (server_status: int)
        SMTP status code
        250 (Requested mail action okay, completed)
        535 (Username and Password not accepted, set 'Allow less secure apps' ON)

    Returns
    ---------
    emailCheck: bool
        True if Status Code is 250 (OK)
        '''
    username = 'polymerautomation@gmail.com'
    password = 'PRD@Monash'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    
    try:
        server.login(username,password)
        server_status = server.noop()[0]

    except smtplib.SMTPAuthenticationError as e:
        server_status = e.smtp_code

    if server_status == 250:
        logger.info('Email OK (250)')
        emailCheck = True
    elif server_status ==535:
        logger.warning('Email not OK (535, Username and Password not accepted, set "Allow less secure apps" ON)')
        emailCheck = False
    else:
        logger.warning('Unknown Email Error, email option not in use')
        emailCheck
    return emailCheck