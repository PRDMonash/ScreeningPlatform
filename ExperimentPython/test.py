import logging
from log_method import setup_logger
import os
from calculateScans import CalculateScans
from Constants import FOLDERS
import pandas as pd

logger = setup_logger('test')

def testing_calculateScans():
    parameter_file = os.path.join(FOLDERS['COMMUNICATION'], 'code_Parameters.csv')
    if not os.path.exists(parameter_file):
        logger.warning('{} does not exists...'.format(parameter_file))
    
    df = pd.read_csv(parameter_file)
    CalculateScans(df, 'GPCandNMR')


testing_calculateScans()