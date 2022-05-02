from numpy.lib.polynomial import RankWarning
from pandas.core.base import DataError
from pandas.core.frame import DataFrame
from experimentDF import create_experimentDF
from numpy.lib.function_base import insert
import pandas as pd
from pathlib import Path
import os
from gpctextfile import AnalyzeGPCtxt

def analyzeGPC(number, txtfile, df, code, GPCfolder, infofolder, rawGPCfolder):
    print('start analyzing GPC {}'.format(number))
    GPC = AnalyzeGPCtxt(txtfile)
    
    filter = df['GPC_number'] == number

    df.loc[filter, 'Mn'] = str(GPC.Mn)
    df.loc[filter, 'Mw'] = str(GPC.Mw)
    df.loc[filter, 'D'] = str(GPC.D)
    
    name_injection = '{}_{}'.format(code, number)
    tres_GPC = 'In progress'
    timesweepnumber= 'In progress'

    try:
        GPC.save_distribution(name_injection, GPCfolder, info = True)
        GPC.save_info_timesweep(name_injection, infofolder, timesweepnumber, tres_GPC)
        GPC.copytxtfile(txtfile, '{}/{}'.format(rawGPCfolder, os.path.basename(txtfile)))
    except:
        pass

    return df

def create_GPCtxt_dict(folder, code):
    file_list = sorted([(item) for item in Path(folder).glob('*{}.txt'.format(code))], key=os.path.getmtime)
    file_list = [str(item).replace("\\","/") for item in file_list]
    file_dic = {int(os.path.basename(i)[:3]): i for i in file_list}
    return file_dic

def search_newGPC(folder, code, gpc_number, df, csv_file_name, gpcfolder, infofolder, rawGPCfolder): 

    file_dict = create_GPCtxt_dict(folder, code)

    #gpc_number = number of already analyzed gpc

    if gpc_number in file_dict.keys() or gpc_number == 0:
        if gpc_number+1 not in file_dict.keys():
            print('Waiting for GPC {}...'.format(gpc_number+1))
            new = False
        elif gpc_number + 1 in file_dict.keys():
            if gpc_number + 1 == len(file_dict):
                print('GPC {} detected.'.format(gpc_number+1))
                new = True
                try:
                    df = analyzeGPC(gpc_number+1, file_dict[gpc_number+1], df, code, gpcfolder, infofolder, rawGPCfolder)    
                except:
                    print("Could not analyze GPC sample {}".format(gpc_number+1))
            else:
                print("Still {} GPC samples to analyze.".format(len(file_dict)-gpc_number))
                print(file_dict)
                for i in range(len(file_dict)-gpc_number):
                    new = True
                    try:
                        df = analyzeGPC(i+gpc_number+1, file_dict[i+gpc_number+1], df, code, gpcfolder, infofolder, rawGPCfolder)
                    except:
                        print('Could not analyze GPC sample {}'.format(i+gpc_number+1))
    if new:
        df.to_csv('{}.csv'.format(csv_file_name))

    gpc_number = len(file_dict)
    return df, gpc_number, new


