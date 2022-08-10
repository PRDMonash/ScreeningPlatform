from code_extra.log_method import setup_logger
import os
import shutil

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

def SearchExperimentFolder(folder, comfolder, experiment_extras, mode = 'NMR'):
    '''
    Makes the different data folders in the main experiment folder.

    Parameters:
    ------------
    Folder

    Return:
    ----------
    1) Folder where GPCs are going to be stored.\n2) Folder where timesweeps are going to be stored.\n3) Folder where Raw GPCs are going to be stored.\n4) Folder where experiment details are going to be stored.\n5) Folder where Injection infos are going to be stored.
    '''
    global SolutionDataframe

    newfoldersoftware = os.path.join(folder, 'Software details')
    if not os.path.exists(newfoldersoftware):
        os.mkdir(newfoldersoftware)
    
    for _, _, files in os.walk(comfolder):
        break
    
    code = str(folder).split('_')[-1]

    csv_files = [file for file in files if file.endswith('.csv')]
    for csv_file in csv_files:
        src = os.path.join(comfolder, csv_file)
        dst = os.path.join(newfoldersoftware, csv_file.replace('code_', '{}_'.format(code)))
        logger.info('{} copied to {}'.format(csv_file, newfoldersoftware))
        shutil.copyfile(src, dst)


    newfolderplots = os.path.join(folder, 'Plots')
    if not os.path.exists(newfolderplots):
        os.mkdir(newfolderplots)  

    if str(mode) == 'GPCandNMR':
        newfolderGPC = os.path.join(folder, 'Filtered GPC Data')
        if not os.path.exists(newfolderGPC):
            os.mkdir(newfolderGPC)

        newfolderinfoGPC = os.path.join(folder, 'Info GPC Injections')
        if not os.path.exists(newfolderinfoGPC):
            os.mkdir(newfolderinfoGPC)

        newfolderRawGPC = os.path.join(folder, 'Raw GPC text files')
        if not os.path.exists(newfolderRawGPC):
            os.mkdir(newfolderRawGPC)

    elif mode == 'NMR':
        newfolderGPC, newfolderinfoGPC, newfolderRawGPC = 'NaN', 'NaN', 'NaN'        
    
    logger.info('Data folders are created in experiment folder')

    experiment_extras.loc[0, ['GPCfolder', 'Infofolder','Softwarefolder', 'Rawfolder', 'Plotsfolder']] = str(newfolderGPC).replace("\\","/"), str(newfolderinfoGPC).replace("\\","/"),str(newfoldersoftware).replace("\\","/"),str(newfolderRawGPC).replace("\\","/"), str(newfolderplots).replace("\\","/")
    #experiment_extra.to_csv('{}/extras_experiment.csv'.format(newfoldersoftware))
    '''
    if not SolutionDataframe.empty:
        SolutionDataframe.to_csv('{}/ReactionSolution_{}.csv'.format(newfoldersoftware, experiment_extra.loc[0,'code']))
        updateGUI('Solution Dataframe saved in software subfolder')
    else:
        updateGUI('No Solution Details given
    '''
    return experiment_extras