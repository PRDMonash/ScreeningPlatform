import csv
from genericpath import exists
import os
from tkinter import E
from turtle import update

from pandas.io.pytables import format_doc
from Solutioncsv import solution_csv
from experiment_csv import experiment_csv
from logtxt import logtxt
import correctedGPCfolder
import SoftwareDetails
import rawGPCfolder
from  LnPlotFile import LnPlotFile
from ConvDPPlotFile import ConvDPplotFile
from Alldatacsvfile import alldatacsv

class experiment_folder():

    all_subfolders = ['Corrected GPC', 'Filtered GPC Data', 'Info GPC Injections','Timesweep Data', 'Plots', 'Raw GPC text files', 'Software Details', 'Updated Plots']

    def __init__(self, folder:str) -> None:
        '''
        Experiment folder object

        Parameters:
        -----------
        folder: str
            full path of experiment folder
        '''

        if type(folder) != str:
            raise TypeError("'folder' needs to be string (not {})".format(type(folder)))
        if not os.path.exists(folder):
            raise FileNotFoundError("{} not found".format(folder))

        self.folder = folder
        self.logFile = logtxt(folder, code = self.getCode())

    def getCode(self) -> str:
        '''
        Returns code of experiment via path string
        '''
        path_list = self.folder.split('/')
        list = ['AM_','PM_']
        for part in path_list:
            for i in list:
                if i in part:

                    code = part.split(i)[1]

                    return code

    ### FOLDER ###
    def checkFolderPresence(self, folder:str) ->bool:
        '''
        Check if given folder is present in experiment folder. Returns True if folder is present
        
        Parameters
        -----------
        folder: str
            name of folder (Common folders: ['Corrected GPC', 'Filtered GPC Data', 'Info GPC Injections', 'Plots', 'Raw GPC text files', 'Software Details', 'Updated Plots']
        
        Returns
        --------
        present: bool
        '''
        if folder in self.getSubFolders():
            return True
        else:
            return False
    
    def checkSubfolders(self) -> list:
        '''
        Checks for missing subfolders (checks for 'Corrected GPC', 'Filtered GPC Data', 'Info GPC Injections', 'Plots', 'Raw GPC text files', 'Software Details', 'Updated Plots')

        Returns:
        --------
        absent_folders: list
            list of absent subfolders
        '''
        absent_folders = []
        for subfolder in self.all_subfolders:
            if subfolder not in self.getSubFolders():
                absent_folders.append(subfolder)
        return absent_folders

    def getFolder(self) -> str:
        return self.folder

    def getSubFolders(self, full_path = False) -> list:
        '''
        Get list of all subfolders

        Parameters:
        -----------
        full_path: bool
            if True, returns full path (default: False)
        
        Returns
        --------
        folders: list
            list of all subfolders in main experiment folder
        '''
        for _,folders,_ in os.walk(self.folder):
            if full_path:
                return [os.path.join(self.getFolder(), i) for i in folders]
            return folders
    
    def getSubfolder(self,foldername:str) -> str or None:
        '''
        If excists, returns the full path of the given folder name
        else: None
        '''
        if self.checkFolderPresence(foldername):
            return str(os.path.join(self.getFolder(), foldername))
        else:
            return None
    
    ### FILE ###
    def __getFilesDict(self, full_path = True) -> dict:
        '''
        returns dict with extension as key and list of the files as value

        Parameters:
        ------------
        full_path: bool
            if True, returns full path (default: True)

        Returns:
        ---------
        files_dict: dict
            files sorted by extension

        '''
        files = self.getFiles(full_path=False)
        extensions = [file.split('.')[-1] for file in files]
        unique_extensions = (set(extensions))

        files_dict = {}
        for ext in unique_extensions:
            files_list = [file for file in files if file.endswith(ext)]
            if full_path:
                files_list = [os.path.join(self.getFolder(), file ) for file in files_list]
            files_dict.update({ext:files_list})

        return files_dict
    
    def getFilesbyExtension(self, extension:str, full_path = True) -> list:
        '''
        Get files with specific extension in main experiment folder

        Parameters:
        -----------
        extension: str
            extension of files to be returned

        Returns:
        ---------
        files_by_extension: list
            files in main experiment folder of given extension
        
        '''
        if not isinstance(extension, str):
            raise TypeError("extension needs to be 'string'")

        files_dict = self.__getFilesDict(full_path=full_path)
        if not extension in files_dict.keys():
            raise KeyError("No files in {} with extension {}. Extensions present: {}".format(self.getFolder(), extension, list((files_dict.keys()))))
        
        files_by_extension = files_dict[extension]
        return files_by_extension

    def getFiles(self, full_path = True) -> list:
        '''
        returns all files

        parameters:
        ----------
        full_path: bool
            if True, returns full path (default: True)
        
        Returns:
        ---------
        files: list
        
        '''
        for _,_,files in os.walk(self.folder):
            if full_path:
                return [os.path.join(self.getFolder(), file) for file in files]
            return files
    
    ### GET SPECIFIC SUBFOLDER ###
    def correctedGPCfolder(self, foldername = 'Corrected GPC', update = False): #-> correctedGPCfolder.correctedGPCfolder:
        '''
        Returns the correctedGPCfolder object of the experiment folder (if present)
        '''

        if foldername in self.getSubFolders():
            return correctedGPCfolder.correctedGPCfolder(os.path.join(self.getFolder(), foldername), update = update)
        else:
            raise FileNotFoundError('{} not found...'.format(foldername))
        
    def rawGPCfolder(self, foldername = 'Raw GPC text files') -> rawGPCfolder.rawGPCfolder:
        '''
        Returns the rawGPCfolder object of the experiment folder (if present)
        '''
        if foldername in self.getSubFolders():
            return rawGPCfolder.rawGPCfolder(os.path.join(self.getFolder(), foldername))
        else:
            raise FileNotFoundError('{} not found...'.format(foldername))

    def SoftwareDetails(self, foldername = 'Software Details') -> SoftwareDetails.SoftwareDetails:
        '''
        Returns the SoftwareDetails object of the experiment folder (if present)
        '''
        if foldername in self.getSubFolders():
            return SoftwareDetails.SoftwareDetails(os.path.join(self.getFolder(), foldername))
        else:
            raise FileNotFoundError('{} not found...'.format(foldername))

    def getSolutioncsv(self, subfolder = 'Software Details') ->solution_csv:
        '''
        Returns solution csv object of experiment
        '''
        if not subfolder in self.getSubFolders():
            raise FileNotFoundError ('\"{}\" not in experiment folder {}'.format(subfolder, self.getFolder()))
            
        path_folder = os.path.join(self.getFolder(), subfolder)
        
        if not os.path.exists(path_folder):
            raise FileNotFoundError('Could not find {}'.format(path_folder))
        
        path_csv = os.path.join(path_folder, 'ReactionSolution_{}.csv'.format(self.getCode()))
        
        if os.path.exists(path_csv):
            return solution_csv(path_csv)
        else:
            raise FileNotFoundError('Could not find {}'.format(path_csv))
    
    ### GET SPECIFIC FILES ###
    def getFileinFolder(self, end_of_file = 'LnPlotLog.txt') -> str:
        '''
        returns defined file in main experiment folder
        
        Parameters:
        -----------
        end_of_file: str
            searches for this file, extension needs to be included (default: 'LnPlotLog.txt)
        '''
        txt_files = self.getFiles()
        text_files_short = self.getFiles(full_path=False)

        file = [file for file in txt_files if file.endswith(end_of_file)]
        if file == []:
            raise FileNotFoundError("File ending on '{}' not found in {}. (Present Files: {})".format(end_of_file, self.getFolder(), text_files_short))
        if len(file) == 1:
            return file[0]
        else:
            raise FileNotFoundError("Multi files ({}) ending on {} found ({})".format(len(file), end_of_file, file))

    def getLnPlotFile(self) -> LnPlotFile:
        '''
        Returns LnPlotFile object (LnPlotLog.txt) if present
        '''
        file = self.getFileinFolder(end_of_file='LnPlotLog.txt')
        if not os.path.exists(file):
            raise FileNotFoundError('Could not find {}'.format(file))
        return LnPlotFile(file)
    
    def getConvDPplotFile(self) -> ConvDPplotFile:
        '''
        Returns ConvDPplotFile object (ConvDP_logfile.txt) if present
        '''
        file = self.getFileinFolder(end_of_file='ConvDP_logfile.txt')
        if not os.path.exists(file):
            raise FileNotFoundError('Could not find {}'.format(file))
        return ConvDPplotFile(file)
    
    def getExperimentcsv(self, update = True, Timesweepfile = True) -> experiment_csv:
        '''
        Returns experiment csv object if present
        Parameters:
        ------------
        Timesweepfile: Bool, default True
            True: creates/uses csv file with only timesweep data
            False: uses raw data file
        '''
        if Timesweepfile:
            csv_path = os.path.join(self.getFolder(), '{}_Timesweeps.csv'.format(self.getCode()))
            if os.path.exists(csv_path):
                return experiment_csv(csv_path, update = update, solutioncsv = self.getSolutioncsv(), Timesweepfile=Timesweepfile, logfile=self.logFile, plotfolder= self.getSubfolder('Updated Plots'))
            
        csv_path = os.path.join(self.getFolder(), '{}_data.csv'.format(self.getCode()))
        if not os.path.exists(csv_path):
            raise FileNotFoundError('Could not find {}'.format(csv_path))
            

        return experiment_csv(csv_path, update = update, solutioncsv = self.getSolutioncsv(), Timesweepfile=Timesweepfile, logfile=self.logFile, plotfolder= self.getSubfolder('Updated Plots'))
    
    def getAlldatacsv(self):
        csv_path = os.path.join(self.getFolder(), '{}_Alldata.csv'.format(self.getCode()))
        return alldatacsv(csv_path)

    def create_convGCPfile(self):
        df = self.getExperimentcsv(update = False).getDF()
        df = df[df['Mn'].notna()]
        df['conv_%'] = round(df['conversion'] *100, 1)
        df.to_csv('{}/{}_convMnData.csv'.format(self.getFolder(), self.getCode()))

