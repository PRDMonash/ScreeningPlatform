import datetime
from ntpath import join
from os import error, times
import os
from time import time
import matplotlib.pyplot as plt
from numpy.core.numeric import NaN
from numpy.lib.shape_base import tile
import pandas as pd
import numpy as np
from pandas.core.dtypes.missing import notna
from pandas.core.frame import DataFrame
from pandas.io.parsers import read_csv

#df = pd.read_csv('FullTestingDFupdate.csv')


def save_scanintegrals(df:DataFrame, code, savingdirectory):
    integralcolumns = [i for i in df.columns if i.startswith('I')]
    df = df.dropna(subset=['conversion'])
    colors_status = {'Timesweep': 'indianred', 'No':'skyblue', int(0):'black', 'End' : 'lightgrey', np.nan:'black', '':'black'}
    lst_marker = ['o', 's', '*', 'v', '^', 'D', 'h', 'x', '+', '8', 'p', '<', '>', 'd', 'H']
    for i, integral in enumerate(integralcolumns):
        plt.scatter(df['Scannumber'], df[integral], marker = lst_marker[i],label = integral,  c=df['Status'].apply(lambda x: colors_status[x]))
    
    title = 'Scan-Integral ({})'.format(code)
    plt.title(title)
    plt.xlabel('Scans')
    plt.ylabel('Absolute Integral')
    plt.legend()
    title = CheckforDot(title)
    plt.savefig('{}/{}'.format(savingdirectory, title))
    plt.clf()

def CheckforDot(title):
    list_title = list(title)
    for i, letter in enumerate(list_title):
        if letter == '.':
            list_title[i] = '_'
    new_title = ''.join(list_title)

    if title != new_title:
        print('New title: {}'.format(new_title))
        return new_title
    return new_title


def save_scanconversion(df:DataFrame,code, savingdirectory):
    df = df.dropna(subset=['conversion'])
    colors_status = {'Timesweep': 'indianred', 'No':'skyblue', int(0):'black', 'End' : 'lightgrey', np.nan:'black', '':'black'}
    plt.scatter(df['Scannumber'], df['conversion'],  c=df['Status'].apply(lambda x: colors_status[x])) 

    title = 'Scan-Conversion ({})'.format(code)
    plt.title(title)
    plt.ylim(0, 1)
    plt.xlabel('Scans')
    plt.ylabel('Conversion')
    title = CheckforDot(title)

    plt.savefig('{}/{}'.format(savingdirectory, title))
    plt.clf()

def save_tresconversion(df:DataFrame, code, savingdirectory):
    colors_timesweep = {1: 'forestgreen', 2:'orange', 3:'tomato', 4:'gold', 5: 'navy', 6:'peru', 7: 'olive', 8:'maroon', 9:'indigo', 10:'purple', int(0):'silver'}
    timesweeps = df[df['Status'] == 'Timesweep']
    plt.scatter(timesweeps['tres'], timesweeps['conversion'],c=timesweeps['Timesweep'].apply(lambda x: colors_timesweep[x]))

    title = 'tres-Conversion ({})'.format(code)
    plt.title(title)
    plt.ylim(0, 1)
    plt.xlabel('tres')
    plt.ylabel('Conversion')
    title = CheckforDot(title)
    plt.savefig('{}/{}'.format(savingdirectory, title))
    plt.clf()

def save_tresMn(df:DataFrame, code, savingdirectory):
    colors_timesweep = {1: 'forestgreen', 2:'orange', 3:'tomato', 4:'gold', 5: 'navy', 6:'peru', 7: 'olive', 8:'maroon', 9:'indigo', 10:'purple', int(0):'black'}
    timesweeps = df[df['Status'] == 'Timesweep']
    timesweeps = timesweeps.dropna(subset=['Mn'])
    timesweeps = timesweeps[~timesweeps['Mn'].isin(['GPC expected'])] # use ~ to NOT IN
    mns = [float(i) for i in list(timesweeps['Mn'])]
    
    if 'Mn theory' in list(df.columns):
        mns_theor = [float(i) for i in list(timesweeps['Mn theory'])]
        plt.scatter(timesweeps['tres'], mns_theor,c= 'silver')

    plt.scatter(timesweeps['tres'], mns ,c=timesweeps['Timesweep'].apply(lambda x: colors_timesweep[x]))

    title = 'tres-Mn ({})'.format(code)
    plt.title(title)
    plt.ylim(bottom = 0)
    plt.xlabel('tres')
    plt.ylabel('Mn (g/mol)')
    title = CheckforDot(title)
    plt.savefig('{}/{}'.format(savingdirectory, title))
    plt.clf()

def save_conversionMn(df:DataFrame, code, savingdirectory):
    colors_timesweep = {1: 'forestgreen', 2:'orange', 3:'tomato', 4:'gold', 5: 'navy', 6:'peru', 7: 'olive', 8:'maroon', 9:'indigo', 10:'purple', int(0):'black'}
    timesweeps = df[df['Status'] == 'Timesweep']
    timesweeps = timesweeps.dropna(subset=['Mn'])
    timesweeps = timesweeps[timesweeps['Mn'] != 'GPC expected']

    mns = [float(i) for i in list(timesweeps['Mn'])]

    if 'Mn theory' in list(df.columns):
        mns_theor = [float(i) for i in list(timesweeps['Mn theory'])]
        plt.scatter(timesweeps['conversion'], mns_theor, c='silver')
    plt.scatter(timesweeps['conversion'], mns,c=timesweeps['Timesweep'].apply(lambda x: colors_timesweep[x]))
    

    title = 'Conversion-Mn ({})'.format(code)
    plt.title(title)
    plt.ylim(bottom = 0)
    plt.xlim(0, 1)
    plt.xlabel('Conversion')
    plt.ylabel('Mn (g/mol)')
    title = CheckforDot(title)
    plt.savefig('{}/{}'.format(savingdirectory, title))
    plt.clf()

def save_GPCdeviation(expDF, code, savingdirectory):
    colors_timesweep = {1: 'forestgreen', 2:'orange', 3:'tomato', 4:'gold', 5: 'navy', 6:'peru', 7: 'olive', 8:'maroon', 9:'indigo', 10:'purple', int(0):'silver'}
    gpcs = expDF.dropna(subset=['Mn'])
    
    gpcs['deviation'] = ((abs(gpcs['Mn theory']- gpcs['Mn']))/ gpcs['Mn theory'] )* 100

    title = 'tres-GPC deviation ({})'.format(code)
    plt.scatter(list(gpcs['tres']), list(gpcs['deviation']), c=gpcs['Timesweep'].apply(lambda x: colors_timesweep[x]))
    plt.xlabel('tres / min')
    plt.ylabel('Deviation / %')
    plt.ylim(0,100)
    plt.title(title)
    title = CheckforDot(title)
    plt.savefig('{}/{}'.format(savingdirectory, title))
    plt.clf()

def save_GPCdifference(expDF, code, savingdirectory):
    colors_timesweep = {1: 'forestgreen', 2:'orange', 3:'tomato', 4:'gold', 5: 'navy', 6:'peru', 7: 'olive', 8:'maroon', 9:'indigo', 10:'purple', int(0):'silver'}
    gpcs = expDF.dropna(subset=['Mn'])
    
    gpcs['difference'] = gpcs['Mn']-gpcs['Mn theory'] 
    print(gpcs['difference'])

    title = 'tres- (GPC exp - GPC theor) ({})'.format(code)
    plt.scatter(list(gpcs['tres']), list(gpcs['difference']), c=gpcs['Timesweep'].apply(lambda x: colors_timesweep[x]))
    plt.xlabel('tres / min')
    plt.ylabel('Difference / g/mol')
    plt.ylim(min(gpcs['difference'])-250, max(gpcs['difference'])+250)
    for line in [-400,400]:
        plt.hlines(line, 0, max(gpcs['tres']), linestyles='dashed')
    plt.title(title)
    title = CheckforDot(title)
    plt.savefig('{}/{}'.format(savingdirectory, title))
    plt.clf()

def save_all_plots(df, code, save_directory):
    #save_scanintegrals(df, code, save_directory)
    #save_scanconversion(df, code, save_directory)
    #save_tresconversion(df, code, save_directory)

    save_tresMn(df, code, save_directory)
    #save_conversionMn(df, code, save_directory)


def _get_poly1d(df, degree = 2):
    timesweeps = df[df['Status'] == 'Timesweep']

    x, y = timesweeps['tres'].dropna(), timesweeps['conversion'].dropna()
    x = x.iloc[:len(y)].dropna()
    x,y = list(x), list(y)
    fit = np.polyfit(x, y , degree)     
    poly = np.poly1d(fit)

    x_values = np.linspace(min(x), max(x), 50)
    y_values = poly(x_values)

    return x_values, y_values

def save_fit(df, code, savingdirectory):
    colors_timesweep = {1: 'forestgreen', 2:'orange', 3:'tomato', 4:'gold', 5: 'navy', 6:'peru', 7: 'olive', 8:'maroon', 9:'indigo', 10:'purple', int(0):'silver'}
    timesweeps = df[df['Status'] == 'Timesweep']

    plt.scatter(timesweeps['tres'], timesweeps['conversion'],c=timesweeps['Timesweep'].apply(lambda x: colors_timesweep[x]), alpha=0.1)
    for i in range(int(max(timesweeps['Timesweep']))):    
        try:
            timesweep = timesweeps[timesweeps['Timesweep'] == i+1]
            x, y = timesweep['tres'].dropna(), timesweep['conversion'].dropna()
            x = x.iloc[:len(y)].dropna()
            fit = np.polyfit(x, y , 2)     
            poly = np.poly1d(fit)
        
            x_values = np.linspace(min(x), max(x), 50)
            plt.plot(x_values, poly(x_values), c = colors_timesweep[i+1], label = 'Timesweep {}'.format(i+1))
        except:
            print('Timesweep {} not ready..'.format(i+1))

    
    #fit all data
    x, y = timesweeps['tres'].dropna(), timesweeps['conversion'].dropna()
    x = x.iloc[:len(y)].dropna()
    x,y = list(x), list(y)
    fit = np.polyfit(x, y , 2)     
    poly = np.poly1d(fit)
    x_values = np.linspace(min(x), max(x), 50)
    plt.plot(x_values, poly(x_values), '--k', alpha = 0.3)

    title = 'tres-Conversion (FIT) ({})'.format(code)
    
    plt.title(title)
    plt.ylim(0, 1)
    plt.xlabel('tres')
    plt.ylabel('Conversion')
    plt.legend()
    title = CheckforDot(title)
    plt.savefig('{}/{}'.format(savingdirectory, title))
    plt.clf()


#save_all_plots(df, 'TEST')
'''
df = pd.read_csv('S:/Sci-Chem/PRD/NMR 112/Automated Platform/GUI July 2021/LS-05M-ethylhexyl_Experiment.csv')
print(df)

dir_path = os.path.dirname(os.path.realpath(__file__))
save_all_plots(df, 'JOREN', dir_path)

directory = 'Z:/Sci-Chem/PRD/NMR 112/Automated Platform/2021/DEBUGGING/LS-05M-ethylhexyl_data.csv'
#directory = input('>> ')
df = pd.read_csv(directory)

dir_path = (os.path.dirname(os.path.realpath(__file__)))

save_all_plots(df, 'Joren', dir_path)
'''