import os
import warnings
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from shutil import copyfile
from numpy.core.arrayprint import format_float_scientific
import pandas as pd


class AnalyzeGPCtxt:
    '''Analysis of GPC text files.
    Parameters
    -----------
    textfile: Path
        directory of GPC text file
    '''
    def __init__(self, textfile):
        self.filename = textfile
        plt.clf()
        try:
            only_file_name = os.path.basename(os.path.normpath(textfile))
            number = int(only_file_name[:3])
            self.number = number
        except:
            self.number = 'No number'

        with open(textfile, 'r') as f:
            content = f.readlines()
            f.close()
        self.content = content

        for line_all in content:
            if line_all.startswith('Mn:'):
                stripped_MnValue = line_all.strip('\t').replace(' ','').replace('\t', ',').split(',')[1]
                self.Mn = float(stripped_MnValue)
            if line_all.startswith('Mw:'):
                stripped_MwValue = line_all.strip('\t').replace(' ','').replace('\t', ',').split(',')[1]
                self.Mw = float(stripped_MwValue)
            if line_all.startswith('D:'):
                stripped_Dvalue = line_all.strip('\t').replace(' ','').replace('\t', ',').split(',')[1]
                self.D = float(stripped_Dvalue)
            if line_all.startswith('Sample :'):
                Sample = line_all.strip('\t').replace(' ','').replace('\t', ',').replace('\n', ',').split(',')[1]
                self.Samplename = Sample
            if line_all.startswith('Inject date :'):
                injectdate = line_all.strip('\t').replace('\t', ',').replace('\n', ',').split(',')[1]
                self.InjectDate = injectdate
                self.InjectTime = injectdate[-8:]
            if line_all.startswith('Print Date:'):
                printdate = line_all.strip('\t').replace('\t', ',').replace('\n', ',').split(',')[1]
                self.CreatedDate = printdate
                self.CreatedTime = printdate[-8:]

        self.K_value = self.getMHK()
        self.alpha_value = self.getMHa()
    
    def __repr__(self):
        return 'Analysis of {}'.format(self.filename)

    def _getLine(self, startstring):
        for line_all in self.content:
            if line_all.startswith(startstring):
                a = (line_all)
        return a
    
    def getExportFile(self):
        line = self._getLine('Export file')
        exportfile = line.strip('\n').strip(' ').replace('\t', '').split('Export file')[-1].split(':')[-1]
        return exportfile

    def getBaseline(self):
        line = self._getLine('Baseline')
        baseline = line.replace('\t', '').strip('\n').split(':')
        start = float(baseline[1].strip(' ').strip('to'))
        stop = float(baseline[2].strip('ml'))
        return start, stop

    def getMHK(self):
        line = self._getLine('Calibration MH-K :')
        K_value = float(line.strip('\n').strip(' ').replace('\t', '').split('ml/g')[0].split(':')[-1])
        return K_value

    def getMHa(self):
        line = self._getLine('Calibration MH-A')
        alpha = float(line.strip('\n').replace('\t', ' ').split(':')[1].split('-')[0])
        return alpha

    def _getMHparametersfile(self, MHcsv = 'MHparameters.csv'):
        try:
            MHdf = pd.read_csv(MHcsv)
            return MHdf

        except:
            print('Could not find MH parameters in {}...'.format(MHcsv))
            return None
    
    def MHfilePresent(self):
        if self._getMHparametersfile is not None:
            return True
        else:
            return False
        
    
    def MHcorrection(self, M, K, alpha):
        b = M**(self.alpha_value + 1)
        a = (self.K_value * (b))
        c = a / K
        M_new = c ** (1/(1+alpha))
        return round(M_new, 1)

    
    def save_distribution(self, name, folder, extension = 'png', info = False, color = 'skyblue'):
        '''
        Parameters:
        -----------
        name: str

        folder: str

        extension: string, valid picture extension, optional, default 'png'

        info: bool, optional, default False

        color: string, color name, optional
        '''
        norm = [((i-min(self.MWD_y))/(max(self.MWD_y)-min(self.MWD_y))) for i in self.MWD_y]
        fig, ax = plt.subplots()
        ax.set_title(self.Samplename)
        ax.set_xscale('log')
        ax.set_xlabel('Molecular weigth', color= 'gray')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.xaxis.set_ticks_position('bottom')
        ax.get_yaxis().set_visible(False)
        ax.plot(self.MWD_x, norm, color = color)
        if info == True:
            box=dict(boxstyle="round",
                        ec='black',
                        fc='silver')
            ax.text(min(self.MWD_x), 0.7, 'Mn:   {} g/mol\nMw:   {} g/mol\nD:     {}'.format(float(self.Mn), float(self.Mw), float(self.D)), size = 10, bbox = box)
        if folder == '0':
            plt.savefig('{}.{}'.format(name, extension))
        else:
            plt.savefig('{}/{}.{}'.format(folder, name, extension))
        plt.close()
    
    def save_info_timesweep(self, name, folder, timesweepnumber, tres):
        """Saves a quick overview text file of the GPC trace\n\nInputs:\n1)self\n2)name of text file\n3)folder to save ('0' for current folder)\n4)number of timesweep\n5)residence time of sample"""
        now = datetime.now().strftime('{}       {}/{}/{}   {}:{}:{}'.format('%A','%d','%m','%y','%H', '%M', '%S'))
        if folder == '0':
            GPCinfo = open('{}_info.txt'.format(name), 'a+')
            GPCinfo.write('{}\n\nSample#\t\t{}\nTimesweep\t{}\n\ntres\t{}\tminutes\nMn\t{}\tg/mol\nMw\t{}\tg/mol\nD\t{}'.format(self.Samplename,self.number, timesweepnumber,tres, self.Mn, self.Mw, self.D))
            GPCinfo.write('\n\nInjection\t\t\t{}\nMeasurement done\t\t{}\nAnalysis done\t\t{}'.format(self.InjectDate, self.CreatedDate, now))
            GPCinfo.close()

        else:
            GPCinfo = open('{}/{}_info.txt'.format(folder, name), 'a+')
            GPCinfo.write('{}\n\nSample#\t\t{}\nTimesweep\t{}\n\ntres\t{}\tminutes\nMn\t{}\tg/mol\nMw\t{}\tg/mol\nD\t{}'.format(self.Samplename, timesweepnumber,timesweepnumber, tres, self.Mn, self.Mw, self.D))
            GPCinfo.write('\n\nInjection\t\t\t{}\nMeasurement done\t\t{}\nAnalysis done\t\t\t{}'.format(self.InjectDate, self.CreatedDate, now))
            GPCinfo.close()

    def save_complete_txtfile(self, name, folder):
         GPCfull = open('{}/{}.txt'.format(folder, name), 'a+')
         GPCfull.write(self.content)
         GPCfull.close()
    
    def copytxtfile(self, src, dst):
        copyfile(src, dst)

    def _getDistribution(self, startstring, stopstring):
        x, y = [],[]
        data_column = 1
        if startstring == 'ELUstart':
            data_column = 2

        searchquery3 = '{} :'.format(startstring)
        searchquery4 = '{} :'.format(stopstring)
        index_start_summary = np.array([x.startswith(searchquery3) for x in np.array(self.content)], dtype=bool)
        index_stop_summary = np.array([x.startswith(searchquery4) for x in np.array(self.content)], dtype=bool)

        lines4 =(self.content[(np.array(range(len(self.content)))[index_start_summary][0]+1):np.array(range(len(self.content)))[index_stop_summary][0]])
        lines5 =[ x.replace('\t\n', '\n').replace('\t ', ',').strip() for x in lines4]

        for line in lines5[2:]:
            x.append(float(line.split(',')[0]))
            y.append(float((line.split(',')[data_column]).strip()))
        
        return x, y
    
    def getRAW(self, show = False, validate = True, detector_limit = 1, slope_baseline_threshold = 0.01, baseliney_threshold = 0.05, saving = None):
        df = pd.DataFrame()
        x,y = self._getDistribution('RAWstart', 'RAWstop')
        df['raw_x'] = x
        df['raw_y'] = y 
        if validate:
            start_baseline, stop_baseline = self.getBaseline()
            x_distri, y_distri = self.getRAWdistribution()

            df.loc[:, 'distri_x'] = pd.Series(x_distri)
            df.loc[:, 'ditri_y'] = pd.Series(y_distri)

            df.loc[:, 'baseline_left_x'] = pd.Series([start_baseline, start_baseline])
            df.loc[:, 'baseline_left_y'] = pd.Series([0, 1])

            df.loc[:, 'baseline_right_x'] = pd.Series([stop_baseline, stop_baseline])
            df.loc[:, 'baseline_right_y'] = pd.Series([0, 1])

    
            if max(y_distri) > detector_limit:
                #print('WARNING! Max y value RAW: {} (detector limit: {})'.format(max(y_distri), detector_limit))
                plt.hlines(max(y_distri), start_baseline, stop_baseline, linestyles='--', color = 'red')
                
            plt.vlines(start_baseline, min(y), max(y))
            plt.vlines(stop_baseline, min(y), max(y))
            
            slope_baseline = (y_distri[-1]-y_distri[0] ) / ( x_distri[-1] - x_distri[0])
            if slope_baseline > slope_baseline_threshold:
                #print('WARNING! Slope of baseline: {} (threshold : {})'.format(slope_baseline, slope_baseline_threshold))
                plt.plot([x_distri[0], x_distri[-1]], [y_distri[0], y_distri[-1]], color = 'red')

            valid_baseline_left, baseline_left_y, _ = self.checkForBaseline_left()
            if not valid_baseline_left:
                plt.vlines(start_baseline, min(y), max(y), color = 'red')
            
            valid_baseline_right, baseline_right_y,_ = self.checkForBaseline_right()
            if not valid_baseline_right:
                pass
                plt.vlines(stop_baseline, min(y), max(y), color = 'red')

            plt.plot(x_distri, y_distri, color = 'blue')
            plt.plot(x,y, color = 'blue', alpha = 0.4)
            plt.title('RAW {}'.format(self.Samplename))
            plt.xlabel('Time / min')
            plt.ylabel('y value')
        if show:
            plt.show()
        if saving != None:
            saving_directory = saving + '/ValidationRAW_{}'.format(self.Samplename)
            
            plt.savefig(saving_directory)
        if show or saving!=None:
            plt.clf()
        df.to_csv('ValidationRAW_{}.csv'.format(self.Samplename)) 
        return x,y

    def getRAW_ax(self, ax, show = False, validate = True, detector_limit = 1, slope_baseline_threshold = 0.01, baseliney_threshold = 0.05, saving = None):
        
        x,y = self._getDistribution('RAWstart', 'RAWstop')
      
        if validate:
            start_baseline, stop_baseline = self.getBaseline()
            x_distri, y_distri = self.getRAWdistribution()
    
            if max(y_distri) > detector_limit:
                #print('WARNING! Max y value RAW: {} (detector limit: {})'.format(max(y_distri), detector_limit))
                plt.hlines(max(y_distri), start_baseline, stop_baseline, linestyles='--', color = 'red')
                
            plt.vlines(start_baseline, min(y), max(y))
            plt.vlines(stop_baseline, min(y), max(y))
            
            slope_baseline = (y_distri[-1]-y_distri[0] ) / ( x_distri[-1] - x_distri[0])
            if slope_baseline > slope_baseline_threshold:
                #print('WARNING! Slope of baseline: {} (threshold : {})'.format(slope_baseline, slope_baseline_threshold))
                plt.plot([x_distri[0], x_distri[-1]], [y_distri[0], y_distri[-1]], color = 'red')

            valid_baseline_left, baseline_left_y, _ = self.checkForBaseline_left()
            if not valid_baseline_left:
                plt.vlines(start_baseline, min(y), max(y), color = 'red')
            
            valid_baseline_right, baseline_right_y,_ = self.checkForBaseline_right()
            if not valid_baseline_right:
                pass
                plt.vlines(stop_baseline, min(y), max(y), color = 'red')

            ax.plot(x_distri, y_distri, color = 'blue')
            ax.plot(x,y, color = 'blue', alpha = 0.4)
            ax.set_title('RAW {}'.format(self.Samplename))
            ax.set_xlabel('Time / min')
            ax.set_ylabel('y value')

        if show:
            plt.show()
        if saving != None:
            saving_directory = saving + '/ValidationRAW_{}'.format(self.Samplename) 
            plt.savefig(saving_directory)
        if show or saving!=None:
            plt.clf()
        return ax
    

    def checkForBaseline_left(self, baseliney_threshold = 0.05):
        _, y_distri = self.getRAWdistribution()
        warning_string = 'Valid baseline border (left y value)'
        if y_distri[0]> baseliney_threshold:
            warning_string = ('WARNING! Invalid baseline border (left y value): {} (threshold: {})'.format(y_distri[0], baseliney_threshold))
            return False, y_distri[0], warning_string
        else:
            return True, y_distri[0], warning_string
    
    def checkForBaseline_right(self, baseliney_threshold = 0.05):
        _, y_distri = self.getRAWdistribution()
        warning_string = 'Valid baseline border (right y value)'
        if y_distri[-1]> baseliney_threshold:
            warning_string = ('WARNING! Incorrect baseline border (right y value): {} (threshold: {})'.format(y_distri[-1], baseliney_threshold))
            return False, y_distri[-1], warning_string
        else:
            return True, y_distri[-1], warning_string

    def getRAWdistribution(self):
        '''
        Only get x, y elugram of values within baseline
        '''
        x,y = self.getRAW(validate=False)

        start_baseline, stop_baseline = self.getBaseline()
        dict_raw = dict(zip(x,y))
        dict_distr = {a:b for a,b in dict_raw.items() if start_baseline<a<stop_baseline}

        x_distri, y_distri = list(dict_distr.keys()), list(dict_distr.values())
        return x_distri, y_distri

    def checkDetectorLimit(self, detector_limit = 1):
        '''
        Checks if gpc y signal is under detector limit (=1)

        Returns
        --------
        tuple: bool, float
            True if valid y value, max_y_value
        '''
        x,y = self.getRAWdistribution()
        max_y_value = max(y)
        warning_string = 'Valid max y value RAW: {} (detector limit: {})'.format(max_y_value, detector_limit)
        if max_y_value > detector_limit:
            warning_string = 'WARNING! Invalid Max y value RAW: {} (detector limit: {})'.format(max_y_value, detector_limit)
            return False, max_y_value, warning_string # y value is higher than detector limit (FALSE)
        else:
            return True, max_y_value, warning_string



    def getElugram(self, show = False, validating = True):
        x,y = self._getDistribution('ELUstart', 'ELUstop')
        
        if validating:
            max_value = max(y)
            if max_value > 0.97:
                plt.hlines(max_value, min(x), max(x))
                print(self.Samplename)
                print('WARNING! Max value of elugram: {}'.format(max_value))
                show = True
        if show:
            plt.plot(x,y)
            plt.title('Elugram {}'.format(self.Samplename))
            plt.show()
        plt.clf()
        return x,y
    
    def getMWD(self, show = False, info = False, color = 'skyblue', normalized = True ):
        """Displays distribution"""
        x, y = self._getDistribution('MWDstart', 'MWDstop')
        if normalized:
            y = [((i-min(y))/(max(y)-min(y))) for i in y]
        if show:
            fig, ax = plt.subplots()
            ax.set_title(self.Samplename)
            ax.set_xscale('log')
            ax.set_xlabel('Molecular weigth', color= 'gray')
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.xaxis.set_ticks_position('bottom')
            ax.get_yaxis().set_visible(False)
            ax.plot(x, y, color = color)
            if info:
                box=dict(boxstyle="round",
                            ec='black',
                            fc='silver')
                ax.text(min(x), 0.7, 'Mn:   {} g/mol\nMw:   {} g/mol\nD:     {}'.format(float(self.Mn), float(self.Mw), float(self.D)), size = 10, bbox = box)
            plt.show()
            plt.clf()
        
        return x, y

    def getMHcorMn(self, monomer):
        '''
        Extracts the MH parameters and returns the corrected Mn
        
        Parameters:
        ------------
        monomer: string
            abbreviation of monomer
        '''
        k, a = self.getMHparamters(monomer)
        return self.MHcorrection(self.Mn, k, a)

    def getMHparamters(self, monomer):
        MHparametersdf = self._getMHparametersfile()
        if not monomer in list(MHparametersdf['Monomer']):
            print('Could not find the MH parameters for {}'.format(monomer))
            return None, None
                    
        K_analyte = float(MHparametersdf[MHparametersdf['Monomer']==monomer]['K'])
        a_analyte = float(MHparametersdf[MHparametersdf['Monomer']==monomer]['a'])

        return K_analyte, a_analyte

    def monomerInMHfile(self, monomer):
        MHparametersdf = self._getMHparametersfile()
        if monomer in list(MHparametersdf['Monomer']):
            return True
        else:
            return False
    def usedMH(self, monomer):
        if self.monomerInMHfile(monomer):
            return monomer
        else:
            print("WARNING! MH parameters of {} not found. BA will be used".format(monomer))
            return 'BA'

    def getMHcorMWD(self, monomer, show = False, info = True, original = False, savedirectory = None, check =False):
        x,y = self.getMWD()
        K_analyte, a_analyte = self.getMHparamters(monomer)
        
        m_new = [self.MHcorrection(m, K_analyte, a_analyte) for m in x]


        fig, ax = plt.subplots()
        title = '{} ({})'.format(self.Samplename, monomer)
        ax.set_title(title)
        ax.set_xscale('log')
        ax.set_xlabel('Molecular weigth', color= 'gray')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.xaxis.set_ticks_position('bottom')
        ax.get_yaxis().set_visible(False)
           
        ax.plot(m_new, y, color = 'blue')

        if info:
            box=dict(boxstyle="round",
                        ec='blue',
                        fc='silver',
                        alpha = 0.5)
            ax.text(min(x), 0.7, 'Mn:   {} g/mol\n  K = {}\n  a = {}'.format(self.MHcorrection(self.Mn, K_analyte, a_analyte), K_analyte, a_analyte), size = 10, bbox = box)

        if original:
            ax.plot(x, y, color = 'royalblue', alpha = 0.3)
                
            if info:
                box2=dict(boxstyle="round",
                        ec='black',
                        fc='silver',
                        alpha = 0.2)
                ax.text(min(x), 0.4, 'Mn:   {} g/mol\n  raw'.format(float(self.Mn)), size = 10, bbox = box2)
        
        if savedirectory !=None:
            plt.savefig('{}/{}.png'.format(savedirectory, title))
            print('\t{} saved in {}'.format(title, savedirectory))
    
        
        if check:
            print('Checking {}'.format(self.Samplename))
            self.validatingElugram()
        if show:
            plt.show()
        plt.clf()
        
        return m_new, y

 
