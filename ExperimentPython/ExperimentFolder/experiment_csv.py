from datetime import datetime, time
from operator import eq, index, ne, neg
from re import L, T
from tkinter import DoubleVar
from tkinter.constants import N, S, X
from numpy import core
from numpy.lib.function_base import delete, diff
from numpy.lib.npyio import save
from numpy.lib.shape_base import tile
import pandas as pd
import os
import matplotlib.pyplot as plt
import numpy as np
import warnings
import matplotlib.font_manager as font_manager
from sqlalchemy import except_, false


warnings.filterwarnings('ignore')
import math
from .logtxt import logtxt
from .Solutioncsv import solution_csv
from .rawGPCfolder import rawGPCfolder
from .gpctextfile_V2 import AnalyzeGPCtxt

class experiment_csv():
    def __init__(self, file, solutioncsv = None, update = True, Timesweepfile = False, logfile = None, plotfolder= None) -> None:
        if not os.path.exists(file):
            raise FileNotFoundError('{} not found...')
        self.__file = file

        self.logfile = logfile
        if logfile == None:
            self.logfile = self.__getlogfile()

        filetype = self.getFileType(file) # filetype is data or timesweeps

        self.actionstring = '\n' # initiate action string as string

        if filetype == 'data' and Timesweepfile == True:
            self.logfile.add('Given file is _data.csv file ({}) and _timesweeps.csv file is requested. File will be created'.format(file))
            self.__file = self.__createTimesweepcsv()
            self.logfile.add('Working csv file: {}'.format(self.__file))
        else:
            self.logfile.add('Data analysis based on {}'.format(self.__file))

        self.__plotsFolder = plotfolder
        if plotfolder == None:
            self.__plotsFolder = self.__searchPlotFolder()
        
        
        self.solutioncsv = solutioncsv
        if solutioncsv == None:
            self.solutioncsv = self.__searchSolutioncsv()
        else:
            self.logfile.add('Solution csv given: {}'.format(self.solutioncsv.getFile()))


        if update:
            self.logfile.add('======= NEW UPDATE =======')   
            self.__updating()
            self.updatePlots() 
        if not update:
            if 'ln' in self.getColumns() and 'DP' in self.getColumns():
                self.logfile.add('CSV file not updated but ln and DP data is present')
            else:
                self.logfile.add('WARNING! CSV file not updated. ln and DP data NOT present!')

    ### INIT ###
    def __repr__(self) -> str:
        return 'experiment_csv object for {}'.format(self.getFile())

    def __len__(self):
        return len(self.getDF())

    def getFileType(self, file:str) -> str:
        '''
        Returns 'data' or 'timesweeps' 
        '''
        filetype = file.split('_')[-1].split('.')[0]
        return filetype

    def __searchSolutioncsv(self, subfolder = 'Software Details'):
        '''
        Searched for 1) Software Details folder and 2) ReactionSolution_code.csv. If not found, cannot calculate DPs and returns None
        '''
        path_folder = os.path.join(self.getFolder(), subfolder)
        if not os.path.exists(path_folder):
            self.logfile.add("Could not find 'Software Details' in {}. Cannot calculate DPs".format(self.getFolder()))
            return None
        
        path_csv = os.path.join(path_folder, 'ReactionSolution_{}.csv'.format(self.getCode()))
        if not os.path.exists(path_csv):
            self.logfile.add("Could not find reaction solution csv in {}. Cannot calculate DPs".format(path_folder))
            return None

        self.logfile.add("Reaction Solution file found ({})".format(path_csv))           
        return solution_csv(path_csv)  

    def __updating(self):
        '''
        Updating datafrme with ln and DP
        '''
        columns = self.getColumns()
        if 'ln' in columns:
            self.logfile.add("Ln data already in csv file.. Not updated")
        else:
            self.__setLnColumn()
       
        if 'DP' in columns:
            self.logfile.add("DP data already in csv file.. Not updated")
        else:
            self.__addDPcolumn()

        self.__addrawGPCinfo()
        
        
        self.validating()

    def getRawGPCfolder(self):
        gpcfolder = self.getFolder() + '/Raw GPC text files'
        if not os.path.exists(gpcfolder):
            self.logfile.add('GPC folder ({}) not found...'.format(gpcfolder))
            return None
        return gpcfolder

    def __addrawGPCinfo(self):
        self.logfile.add('Validationg RAW gpc data...')
        df = self.getDF()
        gpcfolder_raw = rawGPCfolder(self.getRawGPCfolder())
        totalTextFiles = len(gpcfolder_raw.getTextFiles())
        totalGPCs = len(df.loc[df['Mn'].notna()])
        
        if totalTextFiles == totalGPCs:
            self.logfile.add('Analyzed GPCs / txt files matches: {} / {}'.format(totalGPCs, totalTextFiles))
        else:
            self.logfile.add('WARNING! Analyzed GPCs / txt files : {} / {}'.format(totalGPCs, totalTextFiles))
        
        validating_raw_gpc_folder = self.getRawGPCfolder() + '/Validation'
        if not os.path.exists(validating_raw_gpc_folder):
            os.mkdir(validating_raw_gpc_folder)
            self.logfile.add('"Validation" folder for raw GPC data created ({})'.format(validating_raw_gpc_folder))
        
        for i, file in enumerate(gpcfolder_raw.getTextFiles(full_path=True)):
            gpc_number_txt = i+1
            
            
            gpc = AnalyzeGPCtxt(file) # raw gpc text file
            gpc_string = 'RAW GPC {}: '.format(gpc.Samplename)
            detectorlimit, y_max_raw, dl_string = gpc.checkDetectorLimit()
            baseline_left_bool , _, bl_left_string = gpc.checkForBaseline_left()
            baseline_right_bool , _, bl_right_string = gpc.checkForBaseline_right()

            df.loc[df['GPC_number']==gpc_number_txt, 'Inject Date'] = gpc.InjectDate
            
            df.loc[df['GPC_number']==gpc_number_txt, 'raw_validDetectionLimit'] = detectorlimit
            if not detectorlimit:
                self.logfile.add(gpc_string + dl_string)

            df.loc[df['GPC_number']==gpc_number_txt, 'raw_ymax'] = y_max_raw
            
            if not baseline_left_bool:
                df.loc[df['GPC_number']==gpc_number_txt, 'raw_validBaseline'] = False
                self.logfile.add(gpc_string + bl_left_string)
            elif not baseline_right_bool:
                df.loc[df['GPC_number']==gpc_number_txt, 'raw_validBaseline'] = False
                self.logfile.add(gpc_string + bl_right_string)
            else:
                df.loc[df['GPC_number']==gpc_number_txt, 'raw_validBaseline'] = True
            
            if not baseline_right_bool or not baseline_left_bool or not detectorlimit:
                df.loc[df['GPC_number']==gpc_number_txt, 'raw_needCorrection'] = True
                gpc.getRAW(saving = validating_raw_gpc_folder) # saves the raw gpc plots that needs to be corrected
            else:
                df.loc[df['GPC_number']==gpc_number_txt, 'raw_needCorrection'] = False
        print(df.columns)
        false_correction = list(df.loc[df['raw_needCorrection']==False, 'GPC_number'])
        true_correction = list(df.loc[df['raw_needCorrection']==True, 'GPC_number'])
        all = len(false_correction) + len(true_correction)
        self.logfile.add("GPC files that need to be corrected: {} / {} ({})".format(len(true_correction), all, true_correction ))    
        self._update_csv(df)


    def __createTimesweepcsv(self):
        '''
        Creates csv file with only timesweep data
        '''
        code = self.getCode()
        path = self.getFolder()
        df = self.getDF()
        
        timesweeps = df[df['Status'] == 'Timesweep']

        save_path = '{}/{}_timesweeps.csv'.format(path, code)
        self.createTimesweepcsv(save_path, timesweeps)
        return save_path
    
    def createTimesweepcsv(self, csvfile, datadf:pd.DataFrame):
        '''
        Saves dataframe as csv file in given directory.

        Parameters:
        ------------
        csvfile: str
            full path where to save
        datadf: pd.DataFrame
            pandas dataframe to save
        '''
        dropcolumns = [column for column in datadf.columns if column.startswith('Unnamed')]
        for column in dropcolumns:
            datadf.drop([str(column)], axis = 1, inplace=True)

        updated = False
        while not updated:
            try:
                datadf.to_csv(csvfile)
                print('\t{} updated'.format(csvfile))
                updated = True
            except:
                proceed = input('Close {}, press "p" to proceed; press "n" to skip saving\n\t>>'.format(csvfile))
                if proceed == 'n':
                    print('\t{} not updated and saved'.format(csvfile))
                    updated = True

    def __getlogfile(self):
        '''
        Returns Log text file object. (If not present yet, creates one.)
        '''
        return logtxt(self.getFolder(), self.getCode())

    def _update_csv(self, datadf:pd.DataFrame, additiontext = ''):
        '''
        Updates csv file

        Parameters:
        -----------
        datadf: pd.DataFrame
            data dataframe to be updated
        additiontext: str
            text to add in log file
        '''
        dropcolumns = [column for column in datadf.columns if column.startswith('Unnamed')]
        for column in dropcolumns:
            datadf.drop([str(column)], axis = 1, inplace=True)

        updated = False
        while not updated:
            try:
                datadf.to_csv(self.getFile())
                self.logfile.add('{} updated. {}'.format(self.getFile(), additiontext))
                updated = True
            except:
                proceed = input('Close {}, press "p" to proceed; press "n" to skip saving\n\t>>'.format(self.getFile()))
                if proceed == 'n':
                    print('\t{} not updated and saved'.format(self.getFile()))
                    updated = True
    
    def checkGPCcorrected(self):
        if 'GPC_updated' in self.getColumns():
            return True
        else:
            return False

    def __setLnColumn(self):       
        '''
        Calculates and adds Ln column for current working file
        '''
        df = self.getDF()
        for i in range(len(df)):
            df.loc[i, 'ln'] = math.log(1/(1-df.loc[i, 'conversion']))

        self.logfile.add('ln(M0/ M) column added to dataframe ({})'.format(self.getCode()))
        self._update_csv(df, additiontext= 'ln(M0/ M) colunm added')
    
    def __addDPcolumn(self):
        '''
        Searches for solution DF, if not found return None. If found, extracts monomer and RAFT info and calculates and adds DP column
        '''
        if not os.path.exists(self.solutioncsv.getFile()):
            self.logfile.add('Could not find solution frame to calculate DP')
            return None

        monomer_MW = float(self.solutioncsv.getChemicalInfo(type = 'monomer', info = 'molecular mass'))
        raft_MW = float(self.solutioncsv.getChemicalInfo(type = 'RAFT', info = 'molecular mass'))

        monomer_name = str(self.solutioncsv.getChemicalInfo(type = 'monomer', info = 'abbreviation'))
        RAFT_name = str(self.solutioncsv.getChemicalInfo(type = 'RAFT', info = 'abbreviation'))
        
        self.__setDPColumn(raft_MW, monomer_MW, raft_name = RAFT_name, monomer_name = monomer_name)

    def __setDPColumn(self, RAFT_MW, monomer_MW, raft_name = 'Unknown RAFT', monomer_name = 'Unknown monomer'):
        
        df = self.getDF()
           
        for i in range(len(df)):
            if not (pd.isna(df.loc[i, 'Mn'])):
                df.loc[i,'DP'] = (float(df.loc[i, 'Mn']) - RAFT_MW) / monomer_MW
                df.loc[i,'Name_monomer'] = monomer_name
                df.loc[i,'MW_monomer'] = monomer_MW
                df.loc[i,'Name_RAFT'] = raft_name
                df.loc[i,'MW_RAFT'] = RAFT_MW
                df.loc[i,'DP theory'] = (float(df.loc[i, 'Mn theory']) - RAFT_MW) / monomer_MW

        

        self.logfile.add('Adding DP (based on {} ({} g/mol) and {} ({} g/mol)) to dataframe ({})'.format(monomer_name, monomer_MW, raft_name, RAFT_MW, self.getCode()))
        self._update_csv(df, additiontext='DP and DP theory column added.')
    
    def __searchPlotFolder(self):
        '''
        Searches for plot Folder. creates one if not exists
        '''
        path = os.path.join(self.getFolder(), 'Updated Plots')
        if not os.path.exists(path):
            os.mkdir(path)
            self.logfile.add('"Updated Plots" folder created ({})'.format(path))
            
        self.setPlotFolder(path)
        return path
    
    
    ### BASIC ###
    def getFile(self):
        '''
        Returns file
        '''
        return self.__file
    
    def getFolder(self):
        '''
        Returns folder as os.path
        '''
        return os.path.dirname(self.__file)

    def getCode(self):
        path_list = self.__file.split('/')
        a = ['AM_','PM_']
        for part in path_list:
            for i in a:
                if i in part:
                    code = part.split(i)[1]
                    if not "\\" in list(code):
                        return code
                    else:
                        return code.split("\\")[0]
    
    def getDF(self):
        '''
        Reads csv file of current working file (data or timesweeps) and returns dataframe
        '''
        return pd.read_csv(self.getFile())
    
    def getColumns(self)->list:
        '''
        Returns list of all the columns in the dataframe
        '''
        return list(self.getDF().columns)

    def setPlotFolder(self, folder, full_path = True):
        '''
        set working plot folder
        Parameters:
        ----------
        folder: str
            name of subfolder
        full_path: bool (default: True)
            if False, add given folder name to folder of file
        '''
        if full_path:
            self.__plotsFolder = folder
        else:
            self.__plotsFolder = '{}/{}'.format(self.getFolder(), folder)
            if not os.path.exists(self.__plotsFolder):
                os.mkdir(self.__plotsFolder)
        return self.__plotsFolder

    def getPlotFolder(self):
        return self.__plotsFolder
    
    def getColours(self):
        return {1: 'forestgreen', 2:'orange', 3:'tomato', 4:'gold', 5: 'navy', 6:'peru', 7: 'olive', 8:'maroon', 9:'indigo', 10:'purple', int(0):'silver'}
    
    def getColunmList(self, column, dropna = True):
        ''''
        get the data of the given column in a list
        
        Parameters:
        -----------
        column: str
            column name (raises TypeError if column not present in dataframe)
        dropna: bool (default: True)
            if True, ignores NA entries in data
        '''
        if not column in self.getColumns():
            raise TypeError('{} not in DF ({}). (Options: {})'.format(column, self.getCode(), self.getColumns()))
            
        df = self.getDF()
        column = df[column]
        if dropna == True:
            column.dropna(inplace=True)

        df = self.getDF()
        return list(column)

    def getGPCsTimesweepSorted(self):
        df = self.getDF()
        GPCs = df[df['GPC_number'].notna()]
        GPCsSorted = []
        for i in range(int(max(GPCs['Timesweep']))):
            GPCs_ts = (GPCs[GPCs['Timesweep'] == i+1])
            GPCsSorted.append([int(min(GPCs_ts['GPC_number'])), int(max(GPCs_ts['GPC_number']))])
        return GPCsSorted
    
    def getTimesweepGPCdict(self):
        df = self.getDF()
        timesweeps = list(df['Timesweep'].unique())

        ts_gpc_dict = {}
        for ts in timesweeps:
            gpcs = list(df.loc[df['Timesweep'] == ts, 'GPC_number'].dropna())
            ts_gpc_dict.update({ts:gpcs})
        
        return ts_gpc_dict

    def setFile(self, file):
        self.__file = file
        if not os.path.exists(self.__file):
            raise FileNotFoundError('{} not found'.format(self.__file))
        
        print('File changed to {}'.format(self.__file))

    def getTresMnPlot(self):
        df = self.getDF()
        timesweeps = df[df['Status'] == 'Timesweep']
        timesweeps = timesweeps.dropna(subset=['Mn'])
        timesweeps = timesweeps[~timesweeps['Mn'].isin(['GPC expected'])] # use ~ to NOT IN
        mns = [float(i) for i in list(timesweeps['Mn'])]
        return list(timesweeps['tres']), mns

    ### PLOTS ###
    def updatePlots(self):
        #self.save_scanintegrals()
        try:
            self.save_tresconversion()
            self.save_tresMn()
            self.save_conversionMn()
            self.save_treslnplot()
            self.save_Lnplot_fit()
            self.save_conversionDP()
            self.save_tresDP()
            self.save_GPCdifference()
            self.save_GPCdeviation()
        except Exception as e:
            self.logfile.add('WARNING! Error in updating plots ({})'.format(e))
        
    def save_scanintegrals(self, show = False):
        original_filetype = self.getFileType(self.__file)
        if original_filetype == 'Timesweeps':
            self.setFile(self.getFile().replace('Timesweeps', 'data'))
        df = self.getDF()
        integralcolumns = [i for i in df.columns if i.startswith('I') and i.endswith(')')]
        df = df.dropna(subset=['conversion'])
        colors_status = {'Timesweep': 'indianred', 'No':'skyblue', int(0):'black', 'End' : 'lightgrey', np.nan:'black', '':'black'}
        lst_marker = ['o', 's', '*', 'v', '^', 'D', 'h', 'x', '+', '8', 'p', '<', '>', 'd', 'H']

        for i, integral in enumerate(integralcolumns):
            plt.scatter(df['Scannumber'], df[integral], marker = lst_marker[i], label = integral,  c=df['Status'].apply(lambda x: colors_status[x]))
    
        title = 'Scan-Integral ({})'.format(self.getCode())
        plt.title(title)
        plt.xlabel('Scans')
        plt.ylabel('Absolute Integral')
        plt.legend()
        title = self._CheckforDot(title)
        plt.savefig('{}/{}'.format(self.getPlotFolder(), title))
        self.logfile.add('{} saved in {}'.format(title, self.getPlotFolder()))
        if show:
            plt.show()
        plt.clf()
        
        if original_filetype == 'Timesweeps':
            self.setFile(self.getFile().replace('data', 'Timesweeps'))
            
    def save_tresconversion(self, save = True, show = False, conv_low = 0, conv_high = 1):
        df = self.getDF()
        timesweeps = df[df['Status'] == 'Timesweep']
        plt.scatter(timesweeps['tres'], timesweeps['conversion'],c=timesweeps['Timesweep'].apply(lambda x: self.getColours()[x]))

        title = 'tres-Conversion ({})'.format(self.getCode())
        plt.title(title)
        plt.ylim(conv_low, conv_high)
        plt.xlabel('tres')
        plt.ylabel('Conversion')
        title = self._CheckforDot(title)
        
        if save:
            plt.savefig('{}/{}'.format(self.getPlotFolder(), title))
            self.logfile.add('{} saved in {}'.format(title, self.getPlotFolder()))
        if show:
            plt.show()
        plt.clf()

 
    def save_tresMn(self, show = False):
        df = self.getDF()
        timesweeps = df[df['Status'] == 'Timesweep']
        timesweeps = timesweeps.dropna(subset=['Mn'])
        timesweeps = timesweeps[~timesweeps['Mn'].isin(['GPC expected'])] # use ~ to NOT IN
        mns = [float(i) for i in list(timesweeps['Mn'])]
        
        if 'Mn theory' in list(df.columns):
            mns_theor = [float(i) for i in list(timesweeps['Mn theory'])]
            plt.scatter(timesweeps['tres'], mns_theor,c= 'silver')

        plt.scatter(timesweeps['tres'], mns ,c=timesweeps['Timesweep'].apply(lambda x: self.getColours()[x]))

        title = 'tres-Mn ({})'.format(self.getCode())
        plt.title(title)
        plt.ylim(bottom = 0)
        plt.xlabel('tres')
        plt.ylabel('Mn (g/mol)')
        title = self._CheckforDot(title)
        plt.savefig('{}/{}'.format(self.getPlotFolder(), title))
        self.logfile.add('{} saved in {}'.format(title, self.getPlotFolder()))
        if show:
            plt.show()
        plt.clf()
    
    def save_tresDP(self, show = False):
        df = self.getDF()
        timesweeps = df[df['Status'] == 'Timesweep']
        timesweeps = timesweeps.dropna(subset=['DP'])
       
        dps = [float(i) for i in list(timesweeps['DP'])]
        
        if 'DP theory' in list(df.columns):
            dps_theor = [float(i) for i in list(timesweeps['DP theory'])]
            plt.scatter(timesweeps['tres'], dps_theor,c= 'silver')

        plt.scatter(timesweeps['tres'], dps ,c=timesweeps['Timesweep'].apply(lambda x: self.getColours()[x]))

        title = 'tres-DP ({})'.format(self.getCode())
        plt.title(title)
        plt.ylim(bottom = 0)
        plt.xlabel('tres')
        plt.ylabel('DP')
        title = self._CheckforDot(title)
        plt.savefig('{}/{}'.format(self.getPlotFolder(), title))
        self.logfile.add('{} saved in {}'.format(title, self.getPlotFolder()))
        plt.clf()
    
    def save_GPCdifference(self, show = False):
        df = self.getDF()
        gpcs = df.dropna(subset=['Mn'])
        
        gpcs['difference'] = gpcs['Mn']-gpcs['Mn theory'] 

        title = 'tres- (GPC exp - GPC theor) ({})'.format(self.getCode())
        plt.scatter(list(gpcs['tres']), list(gpcs['difference']), c=gpcs['Timesweep'].apply(lambda x: self.getColours()[x]))
        plt.xlabel('tres / min')
        plt.ylabel('Difference / g/mol')
        plt.ylim(min(gpcs['difference'])-250, max(gpcs['difference'])+250)
    
        plt.title(title)
        title = self._CheckforDot(title)
        plt.savefig('{}/{}'.format(self.getPlotFolder(), title))
        self.logfile.add('{} saved in {}'.format(title, self.getPlotFolder()))
        if show:
            plt.show()
        plt.clf()
    
    def save_GPCdeviation(self, show = False):
        df = self.getDF()
        gpcs = df.dropna(subset=['Mn'])
        
        gpcs['deviation'] = ((abs(gpcs['Mn theory']- gpcs['Mn']))/ gpcs['Mn theory'] )* 100

        title = 'tres-GPC deviation ({})'.format(self.getCode())
        plt.scatter(list(gpcs['tres']), list(gpcs['deviation']), c=gpcs['Timesweep'].apply(lambda x: self.getColours()[x]))
        plt.xlabel('tres / min')
        plt.ylabel('Deviation / %')
        plt.ylim(0,100)
        plt.title(title)
        title = self._CheckforDot(title)
        plt.savefig('{}/{}'.format(self.getPlotFolder(), title))
        self.logfile.add('{} saved in {}'.format(title, self.getPlotFolder()))
        if show:
            plt.show()
        plt.clf()

    def save_conversionMn(self, show = False):
        df = self.getDF()
        timesweeps = df[df['Status'] == 'Timesweep']
        timesweeps = timesweeps.dropna(subset=['Mn'])
        timesweeps = timesweeps[timesweeps['Mn'] != 'GPC expected']

        mns = [float(i) for i in list(timesweeps['Mn'])]

        if 'Mn theory' in list(df.columns):
            mns_theor = [float(i) for i in list(timesweeps['Mn theory'])]
            plt.scatter(timesweeps['conversion'], mns_theor, c='silver')
        plt.scatter(timesweeps['conversion'], mns,c=timesweeps['Timesweep'].apply(lambda x: self.getColours()[x]))
        

        title = 'Conversion-Mn ({})'.format(self.getCode())
        plt.title(title)
        plt.ylim(bottom = 0)
        plt.xlim(0, 1)
        plt.xlabel('Conversion')
        plt.ylabel('Mn (g/mol)')
        title = self._CheckforDot(title)
        plt.savefig('{}/{}'.format(self.getPlotFolder(), title))
        self.logfile.add('{} saved in {}'.format(title, self.getPlotFolder()))
        if show:
            plt.show()
        plt.clf()

    def getConvDPPlot(self):
        df = self.getDF()
        timesweeps = df[df['Status'] == 'Timesweep']
        timesweeps = timesweeps.dropna(subset=['DP'])
        
        dps = [float(i) for i in list(timesweeps['DP'])]
        return list(timesweeps['conversion']), dps

    def save_conversionDP(self,show = False, save = False, ideal_fit = True):
        df = self.getDF()
        timesweeps = df[df['Status'] == 'Timesweep']
        timesweeps = timesweeps.dropna(subset=['DP'])
    
        monomer_eq = float(self.solutioncsv.getChemicalInfo(type = 'monomer', info = 'eq'))
        if ideal_fit:
            plt.plot([0,1], [0, monomer_eq], ls = '--', c = 'black', alpha =0.2)

        dps = [float(i) for i in list(timesweeps['DP'])]

        if 'DP theory' in list(df.columns):
            dps_theor = [float(i) for i in list(timesweeps['DP theory'])]
            plt.scatter(timesweeps['conversion'], dps_theor, c='silver')
        plt.scatter(timesweeps['conversion'], dps ,c=timesweeps['Timesweep'].apply(lambda x: self.getColours()[x]))
        
        monomer_eq = float(self.solutioncsv.getChemicalInfo(type = 'monomer', info = 'eq'))
        
        plt.plot([0,1], [0, monomer_eq], ls = '--', c = 'black', alpha =0.2)
        title = 'Conversion-DP ({})'.format(self.getCode())
        plt.title(title)
        plt.ylim(bottom = 0)
        plt.xlim(0, 1)
        plt.xlabel('Conversion')
        plt.ylabel('DP')
        title = self._CheckforDot(title)
        if save:
            plt.savefig('{}/{}'.format(self.getPlotFolder(), title))
            self.logfile.add('{} saved in {}'.format(title, self.getPlotFolder()))
        if show:
            plt.show()
        plt.clf()

    def save_Lnplot_fit(self, show = False, save = True, data = True):
        df = self.getDF().dropna(subset=['ln', 'tres'])
        tres, ln = df['tres'], df['ln']

        fit = np.polyfit(tres, ln , 1)
        poly = np.poly1d(fit)
        tres_fit = np.linspace(min(tres), max(tres), 50)
        ln_fit = poly(tres_fit)

        
        plt.plot(tres_fit, ln_fit)
        if data:
            plt.scatter(tres, ln, alpha= 0.2)

        equation = [i.round(3) for i in fit]
        equation_string = 'y = {} x + {}\n{}'.format(equation[0], equation[1], self.getRsquaredLnPlot(x_column='tres', y_column='ln').round(5))

        plt.text(max(tres)*0.77, max(ln_fit)*0.92, equation_string, size=10,
         ha="center", va="center",
         bbox=dict(boxstyle="round",
                    fc ='w', ec ='k',
                    alpha = 0.4
                   
                   )
         )

        title = 'tres-ln (fit) ({})'.format(self.getCode())
        title = self._CheckforDot(title)
        plt.title(title)
        plt.xlabel('tres / min')
        plt.ylabel('ln([M]0/[M]')

        if save == True:
            plt.savefig('{}/{}'.format(self.getPlotFolder(), title))
            self.logfile.add('{} saved in {}'.format(title, self.getPlotFolder()))
        if show:
            plt.show()
        plt.clf()

    def getRsquaredLnPlot(self, x_column, y_column):
        df = self.getDF()
        correlation_matrix = np.corrcoef(df[x_column], df[y_column])
        correlation_xy = correlation_matrix[0,1]
        r_squared = correlation_xy**2
        return r_squared
    
    def getRsquared(self, x, y):
        correlation_matrix = np.corrcoef(x, y)
        correlation_xy = correlation_matrix[0,1]
        r_squared = correlation_xy**2
        return r_squared

    def save_treslnplot(self, show = False, save= True):
        if not 'ln' in self.getColumns():
            print('ln column not in {} dataframe...'.format(self.getCode()))
            return
        
        df = self.getDF()
        plt.scatter(df['tres'], df['ln'], c=df['Timesweep'].apply(lambda x: self.getColours()[x]))

        title = 'tres-ln ({})'.format(self.getCode())
        title = self._CheckforDot(title)
        plt.title(title)
        plt.xlabel('tres / min')
        plt.ylabel('ln([M]0/[M]')
        if show == True:
            plt.show()
        if save == True:
            plt.savefig('{}/{}'.format(self.getPlotFolder(), title))
            self.logfile.add('{} saved in {}'.format(title, self.getPlotFolder()))
        plt.clf()
     
    def _CheckforDot(self, title):
        list_title = list(title)
        for i, letter in enumerate(list_title):
            if letter == '.':
                list_title[i] = '_'
        new_title = ''.join(list_title)

        if title != new_title:
            print('New title: {}'.format(new_title))
            return new_title
        return new_title
    

    def deleteMaxDistance(self, x:list, y:list): 
        fit = np.polyfit(x, y , 1)
        x,y = list(x), list(y) # make list from pandas.series, for indexing
        poly = np.poly1d(fit)     
        difference_list = []
        for sample_number in range(len(y)):
            #print('sample_number: {}/{}'.format(sample_number+1, len(y)))
            tres_sample, ln_sample = x[sample_number], y[sample_number] 
            ln_fit_sample = poly(tres_sample)
        
            difference = (ln_sample - ln_fit_sample)**2
            #print('Difference: {}'.format(difference))
            difference_list.append(difference)

        index_max = difference_list.index(max(difference_list))
        x_max = x[index_max]
        y_max = y[index_max]

        x_new, y_new = [],[]
        for key, value in dict(zip(x, y)).items():
            if key == x_max and value == y_max:
                continue
            else:
                x_new.append(key)
                y_new.append(value)
            
        fit_new = np.polyfit(x_new, y_new, 1)
        r2_new = self.getRsquared(x,y)
        
        return x_new, y_new, fit_new, r2_new

    def _getEquationString(self, x:list, y:list) -> str:
        '''
        Converts x data and y data into equation string of form y = ax + b (r2)
        
        '''
        r2 = self.getRsquared(x,y)
        fit = np.polyfit(x, y, 1)
        equation = [i.round(3) for i in fit]
        equation_string = 'y = {} x + {}    (R2: {})'.format(equation[0], equation[1], r2.round(5))
        return equation_string
    
    def getFitparameters(self, x,y, degree = 1):
        return np.polyfit(x,y, degree)


    def validate_lnplot(self, treshold = 0.999, show = True):
        tres, ln = self.getLnPlot()
        tres_fit, ln_fit = self.getLnPlotFit()
        
        tres_new, ln_new = tres, ln
        r2 = self.getRsquared(tres,ln)
        
        while r2 < treshold:

            tres_new, ln_new, fit_new, r2  = self.deleteMaxDistance(tres_new, ln_new)

        plt.plot(tres_fit, ln_fit, c = 'navy')
        plt.scatter(tres, ln, c= 'navy', alpha= 0.2, label = 'Original ({}/{})'.format(len(ln), len(ln)))
        
        equation_ori = [i.round(3) for i in self.getLnfit()]
        equation_string_ori = 'y = {} x + {}\n{}'.format(equation_ori[0], equation_ori[1], self.getRsquaredLnPlot(x_column='tres', y_column='ln').round(5))

        plt.text(max(tres)*0.77, max(ln_fit)*0.92, equation_string_ori, size=10,
         ha="center", va="center",
         bbox=dict(boxstyle="round",
                    fc ='royalblue', ec ='navy',
                    alpha = 0.2
                   
                   )
         )
        plt.scatter(tres_new, ln_new, c ='maroon', alpha= 0.7, label = 'new ({}/{})'.format(len(ln_new), len(ln)))
        poly = np.poly1d(fit_new)
        x_values = np.linspace(min(tres), max(tres), 50)
        plt.plot(x_values, poly(x_values), c= 'maroon')
        equation_new = [i.round(3) for i in fit_new]
        equation_string_new = 'y = {} x + {}\n{}'.format(equation_new[0], equation_new[1], r2.round(5))

        plt.text(max(tres)*0.77, 0.2, equation_string_new, size=10,
         ha="center", va="center",
         bbox=dict(boxstyle="round",
                    fc ='salmon', ec ='maroon',
                    alpha = 0.2
                   
                   )
         )


        title = 'tres-ln (fit) ({}) ({})'.format(self.getCode(), treshold)
        #title = self._CheckforDot(title) #threshold will have dot in it
        plt.title(title)
        plt.xlabel('tres / min')
        plt.ylabel('ln([M]0/[M]')
        plt.legend()
        if show:
            plt.show()
        plt.clf()
    
    def _getTimesweepColumn(self, number, data = None, return_list = True):
        '''
        return the column of one timesweep
        
        Parameters:
        -----------
        number: int
            number of timesweep
        data: string
            columnm name (default None and returns full dataframe of the timesweep)
        return_list: bool
            if True, returns list of data, False pandas.Series (default: True)
        '''
        df = self.getDF()
        if number > max(df['Timesweep']):
            print('Given number of timesweep ({}) not found. Number of timesweeps: {}'.format(number, max(df['Timesweep'])))
            return
        if data == None:
            return df[df['Timesweep']==number]
        else:
            if data not in self.getColumns():
                print('{} not in dataframe. Valid columns: {}'.format(data, self.getColumns()))
                return

            if return_list:
                return list(df[df['Timesweep']==number][data])
            else:
                return df[df['Timesweep']==number][data]

    
    ### VALIDTATING ###
    def validating(self):
        self._appendActionString('date of analysis: {}\n'.format(datetime.now()))
        self.conversionJumps()
        self.negativeConversions()

        self.CorrectedLnPlot(corrected=True, moving_average=True)

    
    def negativeConversions(self):
        ''''
        Add 'Valid_negative' column to dataframe and creates plots checking for negative conversions
        '''
        df = self.getDF()
        colors = self.getColours()
        self._appendActionString('-> negative conversion values')

        last_timesweep = int(max(df['Timesweep']))
        df['Valid_negative'] = True
        df.loc[df['conversion'] <0 ,  'Valid_negative'] = False
        negatives_total = len(df.loc[df['Valid_negative'] == False ])

        for timesweep in range(last_timesweep):
            timewsweep_number = timesweep +1 # zero indexed
            tres = self._getTimesweepColumn(timewsweep_number, 'tres')
            conv = self._getTimesweepColumn(timewsweep_number, 'conversion')
            number_neg = len([i for i in conv if i<0])
            if number_neg>0:
                percentage = round((number_neg / len(conv))*100, 2)
                warning_atring = ("WARNING: {} negative conversions in timesweep {} ({} % of timesweep {} data)".format(number_neg, timewsweep_number, percentage, timewsweep_number))
                self._appendActionString(warning_atring)

            plt.scatter(df['tres'], df['conversion'], color = 'silver', label = self.getCode(), alpha = 0.1)
            plt.scatter(tres, conv, label = 'Timesweep {}'.format(timewsweep_number), color =colors[timewsweep_number], alpha = 0.3)
            
            saving_folder = self.__plotsFolder + '/Validating'
            if not os.path.exists(saving_folder):
                os.mkdir(saving_folder)
            
            negatives = (df.loc[(df['Valid_negative'] == False) & (df['Timesweep'] == timewsweep_number)])
            plt.hlines(0, min(tres), max(tres), color = 'red', alpha = 0.5)
            plt.scatter(negatives['tres'], negatives['conversion'], color = colors[timewsweep_number], label = '{} negative conversions'.format(len(negatives)))
            
            plt.legend()
            plt.xlabel('tres / min')
            plt.ylabel('conversion')
            plt.title('Timesweep {} Negative Conversions: {}'.format(timewsweep_number, len(negatives)))
            plt.savefig(saving_folder + '/NegativeConversion_timesweep{}'.format(timewsweep_number))
            
            plt.clf()
            
        self._update_csv(df, 'Validated on negative conversions. Negative conversions: {}'.format(negatives_total))
           
    def conversionJumps(self, threshold_tsjump = 0.05, show = False):
        '''
        Checks on conversion jumps based on given threshold_tsjump parameter (default 0.05) and creates plots
        '''
        self._appendActionString('-> conversion jump (threshold = {}%)'.format(threshold_tsjump*100))
        df = self.getDF()
        colors = self.getColours()

        conv_dic = {}
        last_timesweep = int(max(df['Timesweep']))

        df['Valid_tsjump'] = True
        for i in range(last_timesweep):
            print('-------------')
            print("Compare between timesweep {} and {}".format(i, i+1))
            print('-------------')
            
            timewsweep_number = i +1 # zero indexed
            plt.title("Valid timesweep jump between timesweep {} and {}".format(timewsweep_number, timewsweep_number +1))

            tres_1 = self._getTimesweepColumn(timewsweep_number, 'tres')
            conv_1 = self._getTimesweepColumn(timewsweep_number, 'conversion')
            max_conv, min_conv = max(conv_1), min(conv_1)
            x_fit1, y_fit1 = self.getFitData(tres_1, conv_1)

            fit = np.polyfit(tres_1,conv_1, 1)
            poly = np.poly1d(fit)
            last_point = round(poly(tres_1[-1]),2)  
            print('Timesweep {}:\nfit: {}\nLast Point: {}'.format(i, fit, last_point)) 
            print('Points to create graph: ({}, {}) and ({} , {})'.format(tres_1[0], round(poly(tres_1[0]),2), tres_1[-1], round(poly(tres_1[-1]),2)))      

            first_conv, last_conv = conv_1[0], conv_1[-1]
            conv_dic.update({timewsweep_number:[first_conv, last_conv]})            

            if timewsweep_number + 1> last_timesweep:
                continue

            tres_2 = self._getTimesweepColumn(timewsweep_number+1, 'tres')
            conv_2 = self._getTimesweepColumn(timewsweep_number+1, 'conversion')
            x_fit2, y_fit2 = self.getFitData(tres_2, conv_2)

            fit = np.polyfit(tres_2,conv_2, 1)
            poly = np.poly1d(fit)
            first_point = round(poly(tres_2[0]),2)
            print('Timesweep {}:\nfit: {}\nFirst Point: {}'.format(i+1, fit, first_point))
            print('Points to create graph: ({}, {}) and ({} , {})\n'.format(tres_2[0], round(poly(tres_2[0]),2), tres_2[-1], round(poly(tres_2[-1]),2)))     

            difference = abs(last_point-first_point)
            print('Difference: {}'.format(difference))

            if difference> threshold_tsjump:
                for i in range(timewsweep_number+1):
                    filter = df['Timesweep']==i
                    df.loc[filter, 'Valid_tsjump'] = False
                string = ("WARNING: Conversion difference between timesweep {} and {} ({} %) exceeds threshold value of {} %".format(timewsweep_number-1, timewsweep_number,round(difference*100,2), round(threshold_tsjump*100, 2)))
                self._appendActionString(string)
                plt.title("Invalid timesweep jump between timesweep {} and {}".format(timewsweep_number, timewsweep_number +1))


            plt.scatter(df['tres'], df['conversion'], color = 'silver', alpha = 0.1, label = self.getCode())
        
            plt.scatter(tres_1, conv_1, label = 'timesweep {}'.format(timewsweep_number), color =colors[timewsweep_number], alpha =0.15)
            plt.plot(x_fit1, y_fit1, color = colors[timewsweep_number])
        
            plt.scatter(tres_2, conv_2, label = 'timesweep {}'.format(timewsweep_number+1), color = colors[timewsweep_number+1], alpha = 0.15)
            plt.plot(x_fit2, y_fit2, color = colors[timewsweep_number+1])

            text_x = tres_1[-1]-5
            if text_x<1:
                text_x = 1

            plt.text(text_x, conv_1[-1]+0.1, 'Difference of {}'.format(round(difference,2 )))
            plt.ylim(0,1)
            plt.legend()
            plt.xlabel('Residence Time / min')
            plt.ylabel('Conversion')

            saving_folder = self.__plotsFolder + '/Validating' 
            if not os.path.exists(saving_folder):
                os.mkdir(saving_folder)
                self.savingfolder = saving_folder           
            plt.savefig(saving_folder + '/Timesweepjump_{}vs{}'.format(timewsweep_number, timewsweep_number+1))
            if show:
                plt.show()
            plt.clf()

        del_ts = set(df.loc[df['Valid_tsjump']== False, 'Timesweep'])
        if del_ts == set():
            del_ts = '0'

        self._update_csv(df, 'Validated on timesweep jumps. Invalid timesweeps: {}'.format(del_ts))
    
   
    def _appendActionString(self, string):
        self.actionstring = self.actionstring + string + '\n'
    
    def _getActionString(self):
        return self.actionstring

    

    def correctedLnPlotLog(self):
        log_file = self.__file.split('.csv')[0] + '_LnPlotLog.txt'
        with open(log_file, 'w+') as f:
            f.write('==== tres-Ln ====\n')
            f.write('code: {}\n'.format(self.getCode()))
            f.write(self._getActionString())
            f.close()    
        pass
    
    def getFitData(self, x, y, degree = 1):
        '''
        Get Linear regression through data

        Parameters:
        -----------
        x: list
            x data
        y: list
            y data
        degree: int
            degree of polynomial (default linear regression , degree = 1)
        
        Returns:
        ---------
        x_values: list
            fitted x_values, 50 points between min and max of given x data
        y_values: list
            linear regression data
        '''
        fit = np.polyfit(x, y , degree)

        poly = np.poly1d(fit)
        x_values = np.linspace(min(x), max(x), 50)
        return list(x_values), list(poly(x_values))

    def CorrectedLnPlot(self, original = True, corrected = True, threshold_tsjump = 0.05, moving_average = True, window = 25, show = False, save = True, monomerConc_title = True):
        
        df = self.getDF() #get dataframe
        number_of_timesweeps_raw = len(df['Timesweep'].unique()) #number of timesweeps of experiment
        number_of_timesweeps_corr = len((df.loc[(df['Valid_tsjump'] == True) & (df['Valid_negative'] == True), 'Timesweep']).unique()) #number of valid timesweeps
        self.logfile.add('Timesweep corrected / timesweep raw : {} / {} '.format(number_of_timesweeps_corr, number_of_timesweeps_raw)) #add to log

        original_alpha = 1 
        corrected_alpha = 1
        colours = ['gray', 'lightgreen', 'forestgreen']
        # Get original plot
        if original:
            if corrected or moving_average:
                original_alpha = 0.2
            
            self._appendActionString('---- Raw data ----')
            self._appendActionString('Datapoints: {}/{}'.format(len(df['tres']), len(df['tres'])))
            self._appendActionString('Timesweeps: {}/{}'.format(number_of_timesweeps_raw, number_of_timesweeps_raw))
            equation = self._getEquationString(df['tres'], df['ln'])
            self._appendActionString('fit: {}'.format(equation))
            plt.scatter(df['tres'], df['ln'], label = 'raw', alpha= original_alpha, c = colours[0])
            fit_x, fit_y= self.getFitData(df['tres'], df['ln'])
            plt.plot(fit_x, fit_y, label = 'raw - fit\n{}'.format(equation),c = colours[0])
            
        if corrected:
            colour = colours[2]
            if moving_average:
                corrected_alpha = 0.3
                colour = colours[1]
            self._appendActionString('\n---- Corrected data ----')

           #check for negative conversions
            new_df = df.loc[(df['Valid_tsjump'] == True) & (df['Valid_negative'] == True)]
            self._appendActionString("\tNo negative Conversions")
            self._appendActionString('Datapoints: {}/{}'.format(len(new_df['tres']), len(df['tres'])))
            equation = self._getEquationString(new_df['tres'], new_df['ln'])
            self._appendActionString('fit: {}'.format(equation))
            

            #check for conversion jumps
            self._appendActionString("\tNo Invalid Timesweepjumps")           
            self._appendActionString('Datapoints: {}/{}'.format(len(new_df['tres']), len(df['tres'])))
            self._appendActionString('Timesweeps: {}/{}'.format(len(new_df['Timesweep'].unique()), number_of_timesweeps_raw))
            equation = self._getEquationString(new_df['tres'], new_df['ln'])
            self._appendActionString('fit: {}'.format(equation))

            plt.scatter(new_df['tres'], new_df['ln'], label = 'Corrected', alpha=corrected_alpha, c = colour)
            fit_x, fit_y= self.getFitData(new_df['tres'], new_df['ln'])
            plt.plot(fit_x, fit_y, label = 'corrected - fit\n{}'.format(equation), c = colour)
            
            
        if moving_average:    
            self._appendActionString('\n---- Moving average ----')
            self._appendActionString('window: {}'.format(window))
            if not corrected:
                new_df = df
                self._appendActionString('Warning: Moving Average on Raw data')
            tres_s = (new_df['tres'].rolling(window=window).mean()).dropna()
            ln_s = (new_df['ln'].rolling(window =window).mean()).dropna()
            self._appendActionString('Datapoints: {}/{}'.format(len(tres_s), len(df['tres'])))
            self._appendActionString('Timesweeps: {}/{}'.format(len(new_df['Timesweep'].unique()), number_of_timesweeps_raw))
            equation = self._getEquationString(tres_s, ln_s)
            self._appendActionString('fit: {}'.format(equation))
            self._appendActionString('Moving Averge fit values: {}'.format(self.getFitparameters(tres_s, ln_s)))

            plt.scatter(tres_s, ln_s, label = 'Moving Average (window = {})'.format(window), c = colours[2])
            fit_x, fit_y= self.getFitData(new_df['tres'], new_df['ln'])
            plt.plot(fit_x, fit_y, label = 'moving average - fit\n{}'.format(equation), c = colours[2])
            self.logfile.add('Ln Plot Moving Average fit (window = {}): {}'.format(window, equation))

        self._appendActionString('\nMovingAverageFitSTART')
        #self._appendActionString('\nMovingAveragex,MovingAveragey')   
        for x,y in zip(fit_x, fit_y):
            self._appendActionString('{},{}'.format(x,y))
        self._appendActionString('\nMovingAverageFitSTOP')   
        title = 'Residence Time - ln ({})'.format(self.getCode())
        if monomerConc_title:
            monomer_abbr = str(self.solutioncsv.getChemicalInfo(type = 'monomer', info = 'abbreviation'))
            monomer_M = int(round(float(self.solutioncsv.getChemicalInfo(type = 'monomer', info = 'Molar (M)')), 0))
            title = '{}M {} - Residence Time - ln'.format(monomer_M, monomer_abbr)
        title = self._CheckforDot(title)
        plt.title(title)
        plt.xlabel('Residence Time / min')
        plt.ylabel('ln([M]0/[M]')
        font = font_manager.FontProperties(style='normal', size=8)
        plt.legend(prop = font)
        self.correctedLnPlotLog()
        if save:
            plt.savefig('{}/{}'.format(self.getPlotFolder(), title))
        if show:
            plt.show()
        
        plt.clf()

            
        