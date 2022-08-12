import logging
from code_extra.log_method import setup_logger
import os
from code_extra.calculateScans import CalculateScans
from code_extra.defining_folder import SearchExperimentFolder
from code_extra.Constants import FOLDERS
from code_extra.start_experiment import starting
import pandas as pd

logger = setup_logger('test')

def testing_calculateScans():
    parameter_file = os.path.join(FOLDERS['COMMUNICATION'], 'code_Parameters.csv')
    if not os.path.exists(parameter_file):
        logger.warning('{} does not exists...'.format(parameter_file))
    
    df = pd.read_csv(parameter_file)
    print(df.iloc[0]['Mode'])
    

    CalculateScans(df, 'GPCandNMR')

def testing_solutionDataframe():
    solution_file = os.path.join(FOLDERS['COMMUNICATION'], 'code_solution.csv')
    if not os.path.exists(solution_file):
        logger.warning('{} does not exists...'.format(solution_file))

    df = pd.read_csv(solution_file)

    print(len(df))
    print(df.iloc[0]['name'])

    if 'Butyl Acetate' in list(df['name']):
        print('yes')

def testing_experimentfolder():
    comfolder = '//ad.monash.edu/home/User085/jvan0036/Documents/PhD/Monash/Lab/Lab Screening/ScreeningPlatformCode/CommunicationFolder'
    print(os.path.exists(comfolder))
    folder = 'S:/Sci-Chem/PRD/NMR 112/Automated Platform/2022/08/9/433PM_sdf'
    SearchExperimentFolder(folder, comfolder, mode = 'GPCandNMR')
    
def testing_starting():
    starting('S:/Sci-Chem/PRD/NMR 112/Automated Platform/2022/08/12/1238PM_Testing')
    
    

testing_starting()
