from log_method import setup_logger
import os

logger = setup_logger('Defining Folders')

def defining_communication_folder(parentfolder:str, update = False):
    """
    Defining the folder for communication between python and LabView

    Parameters
    ----------
    parentfolder: str
        communication folder to be set
    update: bool (default = False)
        for logging, if True adds 'New folder: ...' to log
    
    Return
    ------
    temporary_txtfile: str

    Pathlastexp_textfile:str

    CommunicationMainFolder: str
        new communication folder
    """
    if not os.path.exists(parentfolder):
        os.mkdir(parentfolder)
        logger.info('New communication folder created: {}'.format(parentfolder))
    try:   
        CommunicationMainFolder = parentfolder

        Temporary_textfile = CommunicationMainFolder + '/temporary_experiment.txt'

        open(Temporary_textfile, 'w').close()
        
        Pathlastexp_textfile = CommunicationMainFolder + '/PathLastExperiment.txt'
        open(Pathlastexp_textfile, 'w').close()
            

        if update:
            logger.info("New CommunicationMainFolder: {}".format(CommunicationMainFolder))
        else:
            logger.info("CommunicationMainFolder: {}".format(CommunicationMainFolder))
    except FileNotFoundError as e:
        print('If in lab, use Z:/Sci-Chem/...')
        logger.error('If in Lab, use Z drive!')
        raise
    return Temporary_textfile, Pathlastexp_textfile, CommunicationMainFolder

def defining_PsswinFolder(folder, update = False):
    """
    Defining the folder for GPC data

    Parameters
    ----------
    folder: str
        GPC folder to be set
    update: bool (default = False)
        for logging, if True adds 'New folder: ...' to log
    
    Return
    ------
    PsswinFolder: str
        defined folder for GPC data
    """
    PsswinFolder = folder

    if not os.path.exists(PsswinFolder):
        logger.warning("Could not find GPC folder ({})".format(PsswinFolder))

    if update:
        logger.info("New Psswin: {}".format(folder))
    else:
        logger.info("Psswin: {}".format(folder))
    return PsswinFolder

def defining_NMRFolder(folder, update = False):
    """
    Defining the folder for NMR data

    Parameters
    ----------
    folder: str
        GPC folder to be set
    update: bool (default = False)
        for logging, if True adds 'New folder: ...' to log
    
    Return
    ------
    NMRfolder: str
        defined folder for NMR data
    """
    NMRFolder = folder
    if not os.path.exists(NMRFolder):
        logger.warning("Could not find NMR folder ({})".format(NMRFolder))
    if update:
        logger.info("New NMR: {}".format(folder))
    else:
        logger.info("NMR: {}".format(folder))
    return NMRFolder