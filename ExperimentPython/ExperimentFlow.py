from time import sleep
from datetime import datetime
from pathlib import Path


CSV_FILE_NAME = '1D EXTENDED+ 1_Integrals.csv'

def SearchForNMRfolder(NMRFolder, code, WARNING_TIMER = 10):
    '''Called by ExperimentFlow(), searches NMR folder (created by Spinsolve software). Will only find the folder if Spinsolve RM protocol is started, and first spectra is measured

    Parameters
    ----------
    NMRFolder: Path
        main folder of NMR data. Normally: Sci-Chem/PRD/NMR 112

    Returns
    -------
    experimentNMRfolder: Path
        folder of NMR data
    '''

    #DebugPrintInitilisation('SearchForNMRfolder')
    timer = 0

    searching = True
    printed = False
    
    while searching == True: #keep searching till folder is found (for 'WARNING_TIMER' sec, thereafter you can enter the directory manually)
        now = datetime.now()
        year, month, day = now.strftime('%Y'), now.strftime('%m'), now.strftime('%d') #extract year, month, day

        experimentNMRfolderDay = "{}\{}\{}\{}".format(NMRFolder, year, month,day)
        
        if printed == False: #print the statement just once
            print('Searching in {} for \'{}\''.format(experimentNMRfolderDay, code))
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



