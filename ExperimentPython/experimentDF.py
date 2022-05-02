from time import time
from matplotlib.pyplot import sca
import pandas as pd
from pandas.core.frame import DataFrame
from calculateScans import GPCinjections


def lststrTolst(lststr):
    if type(lststr) == type(['list']):
        return lststr
    else:
        lst =  lststr.replace('[','').replace(']','').split(',')
        lst = [float(i) for i in lst]
        return lst

def DF_to_dict(df):
    diction = {}
    for entry in range(len(df)):
        entry_dic = {}
        for column in df.columns:
            entry_dic.update({column:df.iloc[entry][column]})
        diction.update({entry:entry_dic})
    return diction

def read_csvs(scan_csv, tsparameter_csv):
    scans_DF = pd.read_csv(scan_csv)
    timesweep_DF = pd.read_csv(tsparameter_csv)

    return scans_DF, timesweep_DF


def create_experimentDF(scans_DF: DataFrame, timesweep_DF: DataFrame, mode: str, csv_file_name = 'experiment_DF_test'):
    '''
    creates the main experiment DF and csv file with name
    '''
    #transform to dictianaries, easier to work with (in my opininon)
    timesweep_dict = DF_to_dict(timesweep_DF)
    scans_dict = DF_to_dict(scans_DF)

    columnsDF = ['Scannumber','Timesweep', 'Status', 'conversion', 'treaction','tres' ]
    nmr_interval = timesweep_dict[0]['NMR interval']

    stopScan = 'Stop Scan NMR'


    if mode == 'GPCandNMR':
        columnsDF = ['Scannumber','Timesweep', 'Status', 'conversion', 'treaction','tres', 'GPC_number', 'Mn', 'Mw', 'D', 'tres_GPC']

        #convert the tres GPC entry from a string of a list to a proper list
        for i in range(len(scans_dict)):
            #scans_dict[i]['tresGPCinjections'] = lststrTolst(scans_dict[i]['tresGPCinjections'])

            #experiment DF is as long as the last GPC scan
            gpc_number = 1
            stopScan = 'Stop Scan GPC'
            
            #ISERTED 11/06
            inj_dict = {}
            volume = timesweep_dict[i]['volume']
            nmr_interval = timesweep_dict[i]['NMR interval']
            gpc_interval = timesweep_dict[i]['GPC Interval']
            for i in range(len(timesweep_dict)):
                start_min = timesweep_dict[i]['Start']
                stop_min = timesweep_dict[i]['Stop']
                inj_dict = GPCinjections(volume, start_min, stop_min, nmr_interval, gpc_interval, inj_dict)
            
            print(inj_dict)
        ####STOP

    #initialize DataFrame
    experimentDF = pd.DataFrame(columns= columnsDF)

    #starts with first entry of timesweep 
    timesweep_number = 0
    last_stop_scan = int(scans_DF.iloc[-1][stopScan])

    for i in range(last_stop_scan):
        #print('\n')
        #print('i : {}'.format(i))
        experimentDF.loc[i, 'Scannumber'] = int(i)
        if i < scans_dict[timesweep_number][stopScan]:
            pass
        else:
            timesweep_number +=1

        experimentDF.loc[i, 'Timesweep'] = timesweep_number +1

        if i in range(int(scans_dict[timesweep_number]['Start Scan NMR']), int(scans_dict[timesweep_number]['Stop Scan NMR'])+1):
            max_tres = timesweep_dict[timesweep_number]['Stop']
                
            experimentDF.loc[i, 'Status'] = 'Timesweep'

            experimentDF.loc[i, 'treaction'] = int(treaction)
            #print('treaction: {}'.format(treaction))
        
            volume = timesweep_dict[timesweep_number]['volume']
            f1 = timesweep_dict[timesweep_number]['StartFR']
            f2 = timesweep_dict[timesweep_number]['StopFR']
            
            tres = round((( volume / f1 ) + (treaction * (1 - (f2 / f1)))/60), 4)
            #print('tres: {}'.format(tres))

            if tres == max_tres:
                print('same tres')
                
            if tres> max_tres:
                print('Last NMR timesweep spectra is during stabilization')
                tres = max_tres
                treaction = int(tres*60)
            

            experimentDF.loc[i, 'Status'] = 'Timesweep'
            experimentDF.loc[i, 'treaction'] = int(treaction)
            experimentDF.loc[i, 'tres'] = tres



            if mode == 'GPCandNMR':
                '''
                if float(tres) in list(scans_dict[timesweep_number]['tresGPCinjections']):
                    for GPC_column in ['Mn', 'Mw', 'D']:
                        experimentDF.loc[i, GPC_column] = 'GPC expected'
                        experimentDF.loc[i, 'GPC_number'] = gpc_number
                    gpc_number += 1
                '''
                ##EDIT on 11/06
                foo = [float(i[1]) for i in list(inj_dict.values())]
                if float(tres) in foo:
                    for GPC_column in ['Mn', 'Mw', 'D']:
                        experimentDF.loc[i, GPC_column] = 'GPC expected'
                        experimentDF.loc[i, 'GPC_number'] = gpc_number
                        experimentDF.loc[i, 'tres_GPC'] = [float(i[0]) for i in list(inj_dict.values())][gpc_number-1]

                    gpc_number +=1 

            treaction += nmr_interval
        else:
            experimentDF.loc[i, 'Status'] = 'No'
            treaction = 0


    experimentDF.to_csv('{}.csv'.format(csv_file_name))   

    print('experimentDF.py: {}'.format(experimentDF))
    return experimentDF

'''
scans_dir = 'Z:/Sci-Chem/PRD/NMR 112/Automated Platform/2021/DEBUGGING/Software details/LS-05M-ethylhexyl_Scans.csv'
scans_DF = pd.read_csv(scans_dir)

ts_DF = pd.read_csv('ExperimentParameters.csv')

create_experimentDF(scans_DF, ts_DF, 'GPCandNMR' )

'''