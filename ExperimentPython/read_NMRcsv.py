from pathlib import Path
import os
import pandas as pd
import matplotlib.pyplot as plt
from time import strftime, localtime

class NMRcsvfile():
    def __init__(self, csv):
        self.df = pd.read_csv(csv)
        self.file = csv
        self.lastmodified = strftime('%Y-%m-%d %H:%M:%S', localtime(os.path.getmtime(csv)))


        self.columns = self.__getcolumns(integralsonly = False)
        self.integralcolumns = self.__getcolumns(integralsonly = True)

        self.integralborders = self.__getintegralborders()
        self.duration = self.__duration()

    def __getcolumns(self, integralsonly):
        columns = list(self.df.columns)
        if integralsonly:
            del columns[0]
        return columns
    
    def __getintegralborders(self):
        numberofintegrals = len(self.columns)-1
        
        integralborders = {}
        for i in range(numberofintegrals):
            entry = (self.columns[i+1])

            integral = entry.replace(')','').split('(')
            
            borders = integral[1].split('|')
            borders = [float(i) for i in borders]
            
            integralborders.update({entry:borders})
        return integralborders
    
    def all_integrals(self):
        '''
        UNDER CONSTRCUTION
        '''
        borders = self.__getintegralborders__()
        print(borders.keys())
        print(self.df.values)
        allintegrals = {}

        return allintegrals
    
    def integral(self, number:int, onlyintegrals = False):
        '''
        returns specific entry in dictionary
        '''
        integral_dict = {}
        for column in self.columns:
            integral_dict.update({column: self.df.iloc[number][column]}) #X Axis column is the time in min

        if onlyintegrals:
            del integral_dict['X Axis']

        return integral_dict

    def lastintegral(self):
        '''
        entry dictionnary of last entry
        '''
        return self.integral(-1)

    def __duration(self):
        '''duration of experiment in hours'''
        x = self.lastintegral()['X Axis']
        return (x/60)

    def show_integralPlot(self):
        '''
        Shows integral plot reaction time (min)/ integration
        '''

        for integral in self.columns[1:]:
            plt.scatter(self.df['X Axis'], self.df[integral], label = integral)
        
        plt.legend()
        plt.ylabel('integration')
        plt.xlabel('reaction time / min')
        plt.show()
    
    def delta_t(self):
        delta_t = []
        for i in range(len(self.df)):
            if i != len(self.df)-1:
                a = float(self.df.iloc[i+1]['X Axis'])-float(self.df.iloc[i]['X Axis'])
                delta_t.append(a*60)
        
        average = round(sum(delta_t)/len(delta_t), 2)
        plt.scatter(range(len(delta_t)), delta_t, label= 'Average: {}'.format(average))
        plt.xlabel('scans')
        plt.ylabel('delta t / sec')
        plt.ylim(0,25)
        plt.legend()
        plt.hlines(average, 0, len(delta_t), colors='k', linestyles='-')
        plt.show()
'''
directory = '1D EXTENDED+ 1_Integrals_1.csv'
csvfile = NMRcsvfile(directory)
print(csvfile.df)
print(csvfile.columns)
print(csvfile.integralborders)
print(csvfile.integral(2))
print(csvfile.lastintegral())
print(csvfile.duration)

csvfile.show_integralPlot()
'''
        