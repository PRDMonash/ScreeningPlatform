from tkinter.constants import N
from numpy.core.numeric import NaN
from numpy.lib.function_base import insert
import pandas as pd
from pandas.core.frame import DataFrame
from read_NMRcsv import NMRcsvfile
from pathlib import Path
from time import sleep

#experimentDF = pd.read_csv('experiment_DF_test.csv')


def _findreadNMRcsvfile(csvdirectory, WARNING_TIMER = 15):
    searching = True
    csvdirectory = '{}.csv'.format(csvdirectory)
    timer = 0
    while searching:
        if Path(csvdirectory).exists():
            NMRcsv = NMRcsvfile(csvdirectory)
            searching = False
        else:
            sleep(1)
            timer +=1
            if timer == WARNING_TIMER:
                print('Cannot find csv file. Check code, activate "export csv" option and give directory manually')
                input_directory = input('>> ')
                if input_directory == 'AGAIN':
                    timer = 0
                else:
                    csvdirectory = '{}\1D EXTENDED+ 1_Integrals.csv'.format(input_directory)
                    timer = 0
    return NMRcsv, NMRcsv.lastmodified

def _findSolutionDF():
    return pd.read_csv('ReactionSolution_Test.csv')

def updateDF_Mnth(soldf: DataFrame, conv):
    filter1 = soldf['class'] == 'RAFT'
    RAFT_Mw = float(soldf.loc[filter1, 'molecular mass'])

    filter2 = soldf['class'] == 'monomer'
    M_Mw = float(soldf.loc[filter2, 'molecular mass'])
    M_eq = float(soldf.loc[filter2, 'eq'])

    Mntheor = round((M_eq * M_Mw * conv) + RAFT_Mw, 0)
    return Mntheor

def updateDF_conversion(vinyl, reference, solutionDF):
        
    mol_init_monomer = solutionDF.iloc[1]['moles (mol)']
    mol_init_solvent = solutionDF.iloc[3]['moles (mol)']


    integration_vinyl = vinyl
    integration_solvent = reference
    monomer_protons = 2

    if solutionDF.iloc[1]['abbreviation'] == 'MA':
        #print('Monomer is MA')
        monomer_protons = 3
    
    elif solutionDF.iloc[1]['abbreviation'] == 'cycloHA':
        #print('Monomer is cyclohexyl acrylate')
        monomer_protons = 1
    elif solutionDF.iloc[1]['abbreviation'] == 'tertBA':
        print('Monomer is tert butyl acrylate')
        monomer_protons = 0
    

    butyl_acetate_protons = 2
    #print("In UpdateDF_conversion: monomer_protons = {}. (3 for MA, 1 for cycloHA, rest acrylic monomers 2)".format(monomer_protons))

    real_ratio = mol_init_monomer/mol_init_solvent

    relative_integration = butyl_acetate_protons + (monomer_protons*real_ratio)
    
    #expected vinly peak integration at t0
    t0_vinyl = 3*real_ratio

    #experimental integration vinyl peaks
    factor = relative_integration/integration_solvent
    vinyl_experimental = factor * integration_vinyl
    
    conv = 1-(vinyl_experimental/t0_vinyl)

   
    return conv

def add_integralcolumns(exp_df:DataFrame, NMRcsv_object):
    #add columns of integral csv to experiment DF
    integralscolumns = NMRcsv_object.integralcolumns
    expDF_integralcolumns = [i for i in exp_df.columns if i.startswith('I')]

    for column in integralscolumns:
        if not column in expDF_integralcolumns:                                 #if one of the columns is in the dataframe (integration borders are changed)
            for expDF_integralcolumn in expDF_integralcolumns:                  # Delete all the current columns
                exp_df = exp_df.drop(columns = expDF_integralcolumn)
                                                                                #... and at new columns
            insertindex = 3                                                     #at what column index to insert the integral columns
            for column in integralscolumns:
                exp_df.insert(insertindex, column, [0.0]*len(exp_df))           # needs to be a float to insert the integral values afterwards
                insertindex += 1
            print("new integral columns: {}".format(integralscolumns))  
            return exp_df                                                       # and return the updated DF
                                                            
    return exp_df

def updateDF_integrals(experimentDF: DataFrame, csvdirectory:str, csv_file_name:str, mode:str, solution_DF: DataFrame, modified_time):
    NMRcsv, last_time = _findreadNMRcsvfile('{}/1D EXTENDED+ 1_Integrals'.format(csvdirectory))
    if modified_time == 0:
        print('Analyzing {} (last modified: {})'.format(NMRcsv.file, NMRcsv.lastmodified))
    if modified_time == last_time:
        return experimentDF, False, last_time
    experimentDF = add_integralcolumns(experimentDF, NMRcsv)
    
    if solution_DF.empty:
        print('searching for dummy dataframe')
        solution_DF = _findSolutionDF()

    ppm = 0
    for integral, borders in NMRcsv.integralborders.items():
        if borders[0] > ppm:
            vinyl = integral
            ppm = borders[0]
        else:
            reference = integral

    #creates a copy of the experimentsDF and 
    for index in range(len(NMRcsv.df)):
        integrals = (NMRcsv.integral(index, onlyintegrals=True))
        for integralcolumn in integrals.keys():
            experimentDF.at[index,integralcolumn] = float(integrals[integralcolumn])

        conversion = updateDF_conversion(experimentDF.iloc[index][vinyl], experimentDF.iloc[index][reference], solution_DF)
        experimentDF.at[index,'conversion'] = float(conversion)
    
        if mode == 'GPCandNMR':
            if type(experimentDF.loc[index, 'GPC_number']) == type(1):
                experimentDF.loc[index, 'Mn theory'] = updateDF_Mnth(solution_DF, conversion)

        if pd.isnull(experimentDF.loc[index, 'Timesweep']):
            experimentDF.loc[index, 'Timesweep'] = 0
            experimentDF.loc[index, 'Scannumber'] = index
            experimentDF.loc[index, 'Status'] = 'End'

    
    #creates new csv file with updated data
    print(csv_file_name)
    experimentDF.to_csv('{}.csv'.format(csv_file_name))
    print('ExperimentDF updated with NMR data till scan {}.'.format(index))
    
    return experimentDF, True, last_time

#updateDF_integrals(experimentDF, '1D EXTENDED+ 1_Integrals.csv', 'test')

