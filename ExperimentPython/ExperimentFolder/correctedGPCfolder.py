from msilib.schema import Error
import os
from tkinter.constants import S
from .gpctextfile_V2 import AnalyzeGPCtxt
import pandas as pd
from tkinter import filedialog
from .experiment_csv import experiment_csv
from .MWDsCSV import MWDcsv
from . import experiment_folder
from .rawGPCfolder import rawGPCfolder
from .Solutioncsv import solution_csv
import numpy as np
import matplotlib.pyplot as plt
from .logtxt import logtxt

class correctedGPCfolder():
    def __init__(self, folder, update = False) -> None:
        ''''
        Class of corrected GPC folder
        '''
        if not os.path.exists(folder):
            raise FileNotFoundError('corrected GPC folder {} not found...'.format(folder))

        
        self.__folder = folder
        self.__infoCSV = None
        self.__mwdCSV = None
        self.__alldatafile = None
        self.__corroctionCSV = None
        self.logfile = logtxt(self.getExperimentFolder().getFolder(), self.getCode())
        
        self.Alldatafile = self.searchAllDatafile()
        
        self.__MHcorrectedFolder = self.searchMHcorrectedfolder()

        self.searchMwdcsv()
        if update:
            self.createOverviewcsvs()
            self.plotAllGPC(save = self.getFolder())

    def __repr__(self) -> str:
        return 'CorrectedGPCfolder of experiment {}.'.format(self.getCode())
        
    ### INIT ###
    def searchMHcorrectedfolder(self):
        MH_correctedFolder = os.path.join(self.getFolder(), 'MH corrected MWDs')
        if not os.path.exists(MH_correctedFolder):
            os.mkdir(MH_correctedFolder)
            self.logfile.add('New MH corrected folder created: {}'.format(MH_correctedFolder))
        
        return MH_correctedFolder
    
    def searchMwdcsv(self):
        csvfiles = self.getCSVfiles()
        if len(csvfiles) > 0: # check if csv files are already there ( give names)
            for file in csvfiles:
                if file.endswith('_MHcorrectedMWDs.csv'):
                    path = os.path.join(self.getFolder(), file)
                    self.setMwdCSV(path)
                if file.endswith('_GPCinfo.csv'):
                    path2 = os.path.join(self.getFolder(), file)
                    self.setInfoCSV(path2)
                if file.endswith('_corrections.csv'):
                    path3 = os.path.join(self.getFolder(), file)
                    self.setCorrectionCSV(path3)

    def searchAllDatafile(self):
        files = (self.getExperimentFolder().getFiles())
        for i in files:
            if str(i).endswith('AllData.csv'):
                return i

   
    ### BASIC ###   
    def getFolder(self):
        return self.__folder
    
    def getMonomer(self):
        ''''
        extracts monomer abbreviation form solution dataframe
        '''
        solution = experiment_folder.experiment_folder(os.path.dirname(self.__folder)).getSolutioncsv()
        monomer = solution.getChemicalInfo(type = 'monomer', info = 'abbreviation')
        return monomer

    def getCode(self):
        code = self.getExperimentFolder().getCode()
        return code

    def getDF(self):
        return pd.read_csv(self.getInfoCSV())
    
    def getExperimentFolder(self):
        return experiment_folder.experiment_folder(os.path.dirname(self.__folder))

    def getRAWgpcfolder(self) -> rawGPCfolder:
        '''
        Returns Raw gpc folder
        '''
        return self.getExperimentFolder().rawGPCfolder()
    
    def getMHcorrectedFolder(self):
        return self.__MHcorrectedFolder



    def getAllFiles(self):
        return [file for _, _, file, in os.walk(self.__folder)][0]

    def getTextFiles(self, full_path = False):
        files = self.getAllFiles()
        txt_files = [file for file in files if file.split('.')[-1]== 'TXT'] # Only txt files, ignore the overview csv files
        txt_files.sort( key = lambda x: int(x.split('_')[0]))
        if full_path:
            txt_files = [os.path.join(self.getFolder(), textfile) for textfile in txt_files]
        return txt_files

    def getCSVfiles(self, full_path = False):
        files = self.getAllFiles()
        csv_files = [file for file in files if file.split('.')[-1]== 'csv'] # Only csv files
        if full_path:
            csv_files = [os.path.join(self.getFolder(), csvfile) for csvfile in csv_files]
        return csv_files

    def getFilesDict(self):
        """
        Dict with txt: amount of text files and csv: amount of csv files
        """
        return {'txt': len(self.getTextFiles()), 'csv': len(self.getCSVfiles())}
    
    def getInfoCSV(self):
        return self.__infoCSV
    
    def getCorrectionCSV(self):
        if self.__corroctionCSV != None:
            return self.__corroctionCSV
        else:
            for csv in self.getCSVfiles(full_path=True):
                if csv.endswith('CorrectionInfo.csv'):
                    return csv    
    
    def setCorrectionCSV(self, corrcsv):
        self.__corroctionCSV = corrcsv

    def setInfoCSV(self, infocsv):
        self.__infoCSV = infocsv
    
    def setMwdCSV(self, mwdcsv):
        self.__mwdCSV = mwdcsv

    ### PLOT ###
    def plotAllGPC(self, show = False, save = None, title = None):
        df = pd.read_csv(self.__mwdCSV)
        ts_gpc = self.getExperimentFolder().getExperimentcsv(update=False).getTimesweepGPCdict()
        colors = self.getExperimentFolder().getExperimentcsv(update=False).getColours()

        fig, ax = plt.subplots()
        ax.set_title(self.getCode())
        if title != None:
            ax.set_title(title)
        ax.set_xscale('log')
        ax.set_xlabel('Molecular weigth', color= 'gray')
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.xaxis.set_ticks_position('bottom')
        ax.get_yaxis().set_visible(False)

        for i in range(len(self.getTextFiles())):
            try:
                number = i+1
                for timesweep, gpc in ts_gpc.items():
                    if number in gpc:
                        tsnumber = timesweep
                
                x,y = df['{}_x'.format(number)], df['{}_y'.format(number)]
                ax.plot(x, y, color = colors[tsnumber])
            except KeyError as e:
                print("Could not include {}_x ({})".format(i, e))
        if save == None:
            savingdirectory = self.getMHcorrectedFolder()
            plt.savefig(savingdirectory + '/{}_allGPCs'.format(self.getCode()))
        if show:           
            plt.show()
        plt.clf()

    ### MAIN ###
    def createOverviewcsvs(self):
        
        all_textFiles = self.getTextFiles()
        self.logfile.add('Validation of Corrected GPC Files files (total:{})'.format(len(all_textFiles)))

        all_gpc = {} # initiate all the data dictionaries

        mwds_corr = {}

        short_overviewDF = pd.DataFrame()
        mwd_DF = pd.DataFrame()
        correction_info_all_DF = pd.DataFrame()
        rawGPCfolder = self.getRAWgpcfolder()
        if len(all_textFiles) < len(rawGPCfolder.getTextFiles()):
            self.logfile.add('Not all text files in raw gpc folder ({}) are corrected..'.format(rawGPCfolder.getFolder()))
        
        raw_gpc_files = (rawGPCfolder.getTimeFiledict())
        for i, txtfile in enumerate(all_textFiles):
            print('Analysing {}... ({}/{})'.format(txtfile, i+1, len(all_textFiles)))
            number = (txtfile.split('_Inj_')[0])
        
            full_path = (os.path.join(self.getFolder(), txtfile))
            gpc = AnalyzeGPCtxt(full_path)

            # Short info not MHP corrected #
            short_overviewDF.loc[i, 'Mn corrected'] = gpc.Mn
            short_overviewDF.loc[i, 'Mw corrected'] = gpc.Mw
            short_overviewDF.loc[i, 'D corrected'] = gpc.D

            mwd_file = '{}/{}_QuickInfo.csv'.format(self.getFolder(), self.getCode())
            self.setMwdCSV(mwd_file)
            self.__update_csv(mwd_file, short_overviewDF)

            # MH corrected csv file #
            monomer_abb = self.getMonomer()
            monomer_abb = gpc.usedMH(monomer_abb)
            x, y = gpc.getMHcorMWD(monomer_abb,savedirectory=self.getMHcorrectedFolder(), original= True)
            mwds_corr.update({'{}_x'.format(number): x})
            mwds_corr.update({'{}_y'.format(number): y})

            mwd_corr_df = pd.DataFrame(dict([ (k,pd.Series(v)) for k,v in mwds_corr.items() ]))
            mwd_corr_file = '{}/{}_MHcorrectedMWDs.csv'.format(self.getFolder(), self.getCode())
            self.setMwdCSV(mwd_corr_file)
            self.__update_csv(mwd_corr_file, mwd_corr_df)

            correction_info_all_DF.loc[number, 'name'] = gpc.Samplename # add sample name
            correction_info_all_DF.loc[number, 'Inject Date'] = gpc.InjectDate # add gpc injection date

            if gpc.InjectDate in raw_gpc_files.keys(): # searches for the correct raw GPC info from the raw gpc dictionary
                raw_gpc_file = raw_gpc_files[str(gpc.InjectDate)]
                raw_gpc = AnalyzeGPCtxt(raw_gpc_file)
                raw_Mn = raw_gpc.Mn
            else:
                raw_gpc_file = 'Not Found'
                raw_Mn = 0


            monomer = self.getMonomer()
            
            correction_info_all_DF.loc[number, 'Raw GPC folder'] = raw_gpc_file
            correction_info_all_DF.loc[number, 'Mn_raw'] = raw_Mn

            correction_info_all_DF.loc[number, 'Mn_corrected'] = gpc.Mn
            correction_info_all_DF.loc[number, 'MH_alpha_raw'] = gpc.getMHa()
            correction_info_all_DF.loc[number, 'MH_K_raw'] = gpc.getMHK()
            correction_info_all_DF.loc[number, 'Max y (elugram)'] = gpc.checkDetectorLimit()[1]
            correction_info_all_DF.loc[number, 'Within Detector limit'] = gpc.checkDetectorLimit()[0]
            correction_info_all_DF.loc[number, 'MH file Found'] = gpc.MHfilePresent()
            correction_info_all_DF.loc[number, 'Monomer'] = monomer
            correction_info_all_DF.loc[number, 'in MH file'] = gpc.monomerInMHfile(monomer)
            monomer_used = gpc.usedMH(monomer)
            correction_info_all_DF.loc[number, 'used_MH'] = monomer_used
            correction_info_all_DF.loc[number, 'MH_alpha_monomer'] = gpc.getMHparamters(monomer_used)[1]
            correction_info_all_DF.loc[number, 'MH_K_monomer'] = gpc.getMHparamters(monomer_used)[0]
            correction_info_all_DF.loc[number, 'Mn_corrected_MH'] = gpc.getMHcorMn(monomer_used)
            correction_info_all_DF.loc[number, 'MWD_corrected_file'] = mwd_file
            correction_info_all_DF.loc[number, 'MWD_corrected_file_MH'] = mwd_corr_file

            correction_info_file = '{}/{}_CorrectionInfo.csv'.format(self.getFolder(), self.getCode())
            self.setCorrectionCSV(correction_info_file)
            self.__update_csv(correction_info_file, correction_info_all_DF)

        if not gpc.monomerInMHfile(monomer):
            self.logfile.add('Coul not found MH parameters for {}. {} was used for MH correction.'.format(monomer, monomer_used))
        else:
            self.logfile.add('MH parameters for {} found. MWDs corrected.'.format(monomer))

        self.logfile.add('CorrectionInfo.csv file saved ({})'.format(correction_info_file))
        self.logfile.add('All corrected MWDs saved ({})'.format(mwd_corr_file))

    def getMonomer(self):
        monomer = self.getExperimentFolder().getSolutioncsv().getChemicalInfo(type='monomer', info = 'abbreviation')
        return monomer

    def __update_csv(self, csvfile, datadf:pd.DataFrame):
        updated = False
        while not updated:
            try:
                datadf.to_csv(csvfile)
                print('\t{} updated'.format(csvfile))
                updated = True
            except Exception as e:
                print(e)
                proceed = input('Close {}, press "p" to proceed; press "n" to skip saving\n\t>>'.format(csvfile))
                if proceed == 'n':
                    print('\t{} not updated and saved'.format(csvfile))
                    updated = True
    
        
    ### UPDATING ###
    def updateExperimentDF2(self, ExpDF_obj: experiment_csv):
        self.logfile.add('Updating {} with gpc data of {}'.format(ExpDF_obj.getFile(), self.getFolder()))

        ExpDF = ExpDF_obj.getDF()
        gpcInfocsv = self.getCorrectionCSV()
       

        gpc_infoDF = pd.read_csv(gpcInfocsv)
        ExpDF = ExpDF.merge(gpc_infoDF, how = 'left', on = 'Inject Date')       
        
        ExpDF['DP_corrected'] = (ExpDF['Mn_corrected'] - ExpDF['MW_RAFT'] ) / ExpDF['MW_monomer']
        ExpDF['DP_corrected_MH'] = (ExpDF['Mn_corrected_MH'] - ExpDF['MW_RAFT'] ) / ExpDF['MW_monomer']

        folder = self.getExperimentFolder().getFolder()
        full_file = '{}/{}_AllData.csv'.format(folder, self.getCode())
        self.__update_csv(full_file, ExpDF)
        return full_file
