import os
import pandas as pd
from tqdm import tqdm
from time import sleep
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

from datetime import datetime
from pathlib import Path

from code_extra.log_method import setup_logger
from code_extra.Constants import FONTS
from code_extra.ExperimentDF import ExperimentDF


logger = setup_logger('Start Experiment')

def WaitstabilisationTime(parameters_file):
    '''
    Calculates stabilisation time (for first timesweep) and waits time (sleep)
    '''
    if not os.path.exists(parameters_file):
        logger.warning('Could not find the parameter csv file ({})'.format(parameters_file))

    parametersDF = pd.read_csv(parameters_file)

    #extracts StartFR (flowrate from first timesweep), reactor volume and stabilisation factor from parameters dataframe and calculates waiting time
    start, volume, stabilisationfactor = parametersDF.loc[0,'StartFR'], parametersDF.loc[0,'Volume'], parametersDF.loc[0,'StabilisationTime']
    waiting_time = (volume * stabilisationfactor) / start #in minutes

    logger.info('Stabilisation started for {} minutes.'.format(waiting_time))
    
    waiting_timesec= int(waiting_time *60) #for sleep function!!

    #fancy progress bar
    for i in tqdm(range(waiting_timesec)):
        sleep(1)


CSV_FILE_NAME = '1D EXTENDED+ 1_Integrals.csv'

def SearchForNMRfolder(extras_file, WARNING_TIMER = 30):
    '''Called by starting(), searches NMR folder (created by Spinsolve software). Will only find the folder if Spinsolve RM protocol is started, and first spectra is measured

    Parameters
    ----------
    NMRFolder: Path
        main folder of NMR data. Normally: Sci-Chem/PRD/NMR 112

    Returns
    -------
    experimentNMRfolder: Path
        folder of NMR data
    '''

    def warning_popup(NMRfolder):
        
        root = Tk()
        logger.info('Software Openend')
        root.title('NMR Platform')
        root.geometry('{}x{}'.format(600, 600))
        root.resizable(False, False)

        popuptitle = Label(root, text = 'Could not find the NMR csv file in\n{}.\n\nMake sure that \n* The Integral borders are set correctly in Spinsolve\n*"Export CSV" option is activated'.format(NMRfolder), font = FONTS['FONT_NORMAL'], padx=15)
        popuptitle.grid(row=0, column = 0, columnspan= 3)

        correct_directory = StringVar()

        search_button = Radiobutton(root, text = 'Search Again', variable = correct_directory, value = 'AGAIN')
        search_button.grid()

        new_folder = Radiobutton(root, text = 'Give new folder', variable = correct_directory, value = 'new', command= root.destroy)
        new_folder.grid()
        
        root.mainloop()

    if not os.path.exists(extras_file):
        logger.warning('Could not find the parameter csv file ({})'.format(extras_file))

    extrasDF = pd.read_csv(extras_file)
    code = extrasDF.loc[0,'code']
    NMRFolder = extrasDF.loc[0,'NMR']

    timer = 0

    searching = True
    printed = False
    
    while searching == True: #keep searching till folder is found (for 'WARNING_TIMER' sec, thereafter you can enter the directory manually)
        now = datetime.now()
        year, month, day = now.strftime('%Y'), now.strftime('%m'), now.strftime('%d') #extract year, month, day

        experimentNMRfolderDay = "{}\{}\{}\{}".format(NMRFolder, year, month,day)
        
        if printed == False: #print the statement just once
            logger.info('Searching NMR folder in {} for \'{}\' (for {} seconds)'.format(experimentNMRfolderDay, code, WARNING_TIMER))
            printed = True

        try:
            #Searched in the folder of the day for the directory with the code. If more folders with same name, takes the last folder
            experimentNMRfolder = [(item) for item in Path(experimentNMRfolderDay).glob('*{}'.format(code))][-1] 
            
            print('NMR data folder: {}'.format(experimentNMRfolder))
            searching = False   

        except:
            sleep(1)
            timer +=1
            if timer == WARNING_TIMER:
                #warning_popup(experimentNMRfolderDay)
                print('It Seems that the folder you are looking for cannot be found. Please give the correct directory or type AGAIN to search for {}\{}.'.format(experimentNMRfolderDay, code))
                again = False
                while not again:
                    correct_directory = input('>> ')
                    if correct_directory == "AGAIN":
                        print('Searching again in {} for \'{}\''.format(experimentNMRfolderDay, code))
                        again = True
                        timer = 0
                    elif Path(correct_directory).exists():
                        print('NMR data folder: {}'.format(correct_directory))
                        return Path(correct_directory)
                    else:
                        print('Folder does not exsist.')
                        printed = False
    
    return experimentNMRfolder

def CreateExpDF(extras_file):

    if not os.path.exists(extras_file):
        logger.warning('Could not find the extras csv file ({})'.format(extras_file))
    extras_DF = pd.read_csv(extras_file)
    
    softwarefolder = extras_DF.loc[0, 'Softwarefolder']
    code = extras_DF.loc[0, 'code']

    scansDF = pd.read_csv(os.path.join(softwarefolder, '{}_Scans.csv'.format(code)))
    parametersDF = pd.read_csv(os.path.join(softwarefolder, '{}_Parameters.csv'.format(code)))
    
    expDF_file = '{}/{}_Experiment.csv'.format(softwarefolder, code)

    expDF_object= ExperimentDF(expDF_file)
    expDF = expDF_object.create_experimentDF(scansDF, parametersDF)

    return expDF

def starting(experimentFolder:str):
    logger.info('Experiment begins! ({})'.format(experimentFolder))
    
    code = str(experimentFolder).split('_')[-1]

    parameters_csv = os.path.join(experimentFolder, 'Software Details', '{}_parameters.csv'.format(code))
    extra_csv = os.path.join(experimentFolder, 'Software Details', '{}_extras.csv'.format(code))
    
        
    #WaitstabilisationTime(parameters_csv)

    #SearchForNMRfolder(extra_csv)

    experiment_DF = CreateExpDF(extra_csv)

    
    





    

    