from numpy.lib.ufunclike import _deprecate_out_named_y

from .experiment_csv import experiment_csv
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from . import experiment_folder
import os
from .logtxt import logtxt

class alldatacsv(experiment_csv):
    def __init__(self, csvfile) -> None:
        #super().__init__(csvfile, update=False)
        self.csvfile = csvfile
        self.dpLogfile = os.path.join(self.getFolder(), 'ConvDP_logfile.txt')
        self.actionstring = ''
        self.logfile = logtxt(self.getExperimentFolder().getFolder(), self.getCode())

    def getFolder(self):
        return os.path.dirname(self.csvfile)

    def getExperimentFolder(self):
        return experiment_folder.experiment_folder(self.getFolder())

    def getCode(self):
        return self.getExperimentFolder().getCode()

    def getDF(self):
        
        return pd.read_csv(self.csvfile)

    def extractDPdata(self, columnname, all = False, wihtinDetectorLimit = True, conversionCorrected = False):
        '''
        extracts conversion and DP data

        Parameters:
        -----------
        columnname: str
            columnname (Normally 'DP', DP theor', 'DP_corrected', 'DP_corrected_MH')

        Return:
        ---------
            conversions: list
                list of conversion data
            DPs: list
                list of DP data
        '''
        
        df = self.getDF()
        data = df[df['Status'] == 'Timesweep']
        if all:
            return data.loc[data[columnname].notna(), 'conversion'], data.loc[data[columnname].notna(), columnname],
                
        conversions = ((data.loc[(data['Valid_tsjump']==conversionCorrected) & (data['Valid_negative'] == conversionCorrected) & (data['Within Detector limit'] == wihtinDetectorLimit), 'conversion']))
        dps = ((data.loc[(data['Valid_tsjump']==conversionCorrected) & (data['Valid_negative'] == conversionCorrected) & (data['Within Detector limit'] == wihtinDetectorLimit), columnname]))
        return conversions, dps
        conversions = data.loc[(data['Valid_tsjump'] == conversionCorrected) & (data['Valid_negative']== conversionCorrected) & (data['Within Detector limit'] == wihtinDetectorLimit), 'conversion']
        if columnname in list(self.getColumns()):
            dps = data.loc[(data['Valid_tsjump'] == conversionCorrected) & (data['Valid_negative']== conversionCorrected) & (data['Within Detector limit'] == wihtinDetectorLimit), columnname]
            print(dps)
            return conversions, dps

    def getFitDataZeroIndex(self, x, y):
        conversions2 = x[:,np.newaxis]
        
        coefficient, sum_of_residuals, _, _ = np.linalg.lstsq(conversions2, y)

    
        r2 = 1 - sum_of_residuals / (y.size * y.var())

        x_data = list(np.linspace(0,1.1))
        y_data = [i*coefficient[0] for i in x_data]
        return x_data, y_data,coefficient[0], r2[0]
        
    def correctedConvDPPlotLog(self):
        log_file = self.dpLogfile
        with open(log_file, 'w+') as f:
            f.write('==== Conv - DP ====\n')
            #f.write('code: {}\n'.format(self.getCode()))
            f.write(self._getActionString())
            f.close()  
        self.logfile.add('ConvDP data saved in {}'.format(log_file))  
        pass

    def _appendActionString(self, string):
        self.actionstring = self.actionstring + string + '\n'
    
    def _getActionString(self):
        return self.actionstring

    def save_conversionDP(self, show=True, save=False, theor = False, raw=False, corrected =False, MHcor = True, fit = True, correctedConversion = True, saving_directory = "Updated Plots", title = 'Conversion-DP'):
        
        if raw:
            conversions, dpdata = self.extractDPdata('DP')
            plt.scatter(conversions, dpdata, c='blue')

        if theor:
            conversions, dpdata = self.extractDPdata('DP theory')
            plt.scatter(conversions, dpdata, c='black')
        if corrected:
            conversions, dpdata = self.extractDPdata('DP_corrected')
            plt.scatter(conversions, dpdata, c='red')
        
        if MHcor:
            conv_out, dp_out = self.extractDPdata('DP_corrected_MH', all=True)
            dp_out_number = len(dp_out)            
            plt.scatter(conv_out, dp_out, alpha= 0.2, c ='darkblue', label = 'All: {}/{}'.format(dp_out_number,dp_out_number))
            try:
                conversions, dpdata = self.extractDPdata('DP_corrected_MH', conversionCorrected=True, wihtinDetectorLimit= True)
                dp_in_number = len(dpdata)
                plt.scatter(conversions, dpdata, c='darkblue', label = 'Valid: {}/{}'.format(dp_in_number,dp_out_number))
            except:
                print('Could not extract "valid" data...')
                plt.scatter(conv_out, dp_out, alpha= 1, c ='darkblue', label = 'All: {}/{}'.format(dp_out_number,dp_out_number))
            
            
            try:
                self._appendActionString('CorrectedDataSTART')
                for i,j in zip(conversions, dpdata):
                    self._appendActionString('{},{}'.format(i,j))
                self._appendActionString('CorrectedDataSTOP')

                self._appendActionString('AllDataSTART')
                for i,j in zip(conv_out, dp_out):
                    self._appendActionString('{},{}'.format(i,j))
                self._appendActionString('AllDataSTOP')
            except:
                print("could not save conv DP data in log file")
        
 
        if fit:
            print('Fit through MH corrected data.')
            x2, y2, a, r2 =self.getFitDataZeroIndex(conversions, dpdata)
            
            plt.plot(x2, y2, label = 'y = {} x (R2 = {})'.format(round(a, 2), round(r2, 4)))

            self._appendActionString('ZeroInterceptFitSTART')
            for i,j in zip(x2, y2):
                self._appendActionString('{},{}'.format(i,j))
            self._appendActionString('ZeroInterceptFitSTOP')
            
            fit = np.polyfit(conversions, dpdata , 1)
            print(conversions, dpdata)
            x, y = self.getFitData(conversions, dpdata)

            self._appendActionString('FitSTART')
            for i,j in zip(x, y):
                self._appendActionString('{},{}'.format(i,j))
            self._appendActionString('FitSTOP')


            fit_string = self._getEquationString(conversions, dpdata)
            plt.plot(x,y, c='black', label = fit_string)
            plt.plot([0,1], [0,50], '--',color = 'blue', alpha = 0.2)
            
            
        self.correctedConvDPPlotLog()
        if title == 'Conversion-DP':
            title = 'Conversion-DP ({})'.format(self.getCode())
        
        plt.title(title)
        plt.ylim(bottom = 0)
        plt.xlim(0, 1)
        plt.xlabel('Conversion')
        plt.ylabel('DP')
        plt.ylim(0,50)
        title = self._CheckforDot(title)
        plt.legend()
        if save:
            if saving_directory == "Updated Plots":
                saving_dir = '{}/{}'.format(self.getExperimentFolder().getSubfolder(saving_directory), title)
            saving_dir = '{}/{}'.format(saving_directory, title)
            
            plt.savefig(saving_dir)
            self.logfile.add("Conv-DP plot saved as {}".format(saving_dir))
            #self.logfile.add('{} saved in {}'.format(title, self.getPlotFolder()))
        if show:
            plt.show()
        plt.clf()   
    