from os import times
import pandas as pd
import matplotlib.pyplot as plt

class MWDcsv():
    def __init__(self, csv) -> None:
        self.__csv = csv
        self.__timesweeps = []
        self.__basicColor = 'skyblue'
        pass

    def getCode(self):
        path_list = self.__csv.split('/')
        list = ['AM_','PM_']
        for part in path_list:
            for i in list:
                if i in part:
                    code = part.split(i)[1]
                    return code    
    def getCSV(self):
        return self.__csv

    def getDF(self):
        return pd.read_csv(self.getCSV())

    def getColumns(self):
        df = self.getDF()
        return list(df.columns)
    
    def getDistribution(self,number, normalized =False):
        if not number in self.getDistributionNumbers():
            print('Could not find {}_x in csv file'.format(number))
            return None
        mwdX = self.getDF()['{}_x'.format(number)].dropna()
        mwdY = self.getDF()['{}_y'.format(number)].dropna()
        if not len(mwdX) == len(mwdY):
            print('Lenght of lists are not the same: {}_x ({}) and {}_y ({})'.format(number, len(mwdX), number, len(mwdY)))
            return None

        if normalized:
            mwdY = [(i-min(mwdY))/(max(mwdY)-min(mwdY)) for i in mwdY]

        return list(mwdX), list(mwdY)

    def getDistributionNumbers(self):
        numbers = []
        for column in self.getColumns():
            if column.endswith('_x'):
                numbers.append(int(column.split('_x')[0]))
        return numbers
    
    def getNumberOfDistributions(self):
        return len(self.getDistributionNumbers())

    def getTimesweeps(self):
        return self.__timesweeps
    
    def setTimesweeps(self, timesweeps):
        self.__timesweeps = timesweeps
    
    def getBasicColor(self):
        return self.__basicColor
    
    def setBasicColor(self, color):
        self.__basicColor = color

    def __color(self, number):
        colours = {1: 'forestgreen', 2:'orange', 3:'tomato', 4:'gold', 5: 'navy', 6:'peru', 7: 'olive', 8:'maroon', 9:'indigo', 10:'purple', int(0):'silver'}
        for i, ts in enumerate(self.getTimesweeps()):
            if number in range(ts[0], ts[1]+1): # stop is excluded, so +1 to include
                return colours[i+1]
        return self.__basicColor

    def saveAllDistributions(self, normalized = False, show=False):
        fig, ax = plt.subplots()
        ax.set_title(self.getCode())
        ax.set_xscale('log')
        ax.set_xlabel('Molecular weigth', color= 'gray')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.xaxis.set_ticks_position('bottom')
        ax.get_yaxis().set_visible(False)
        for distri in (self.getDistributionNumbers()):
            x, y = self.getDistribution(distri, normalized = normalized)
            ax.plot(x,y, c = self.__color(distri))

        plt.savefig('MWD_overlay')
        
        if show:
            plt.show()
        plt.clf()