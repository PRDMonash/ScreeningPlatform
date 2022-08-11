from distutils import text_file
from inspect import getfile
import os
import matplotlib.pyplot as plt

from importlib_metadata import files
from matplotlib.pyplot import plot
from . import gpctextfile_V2

class rawGPCfolder():
    def __init__(self, folder) -> None:
        if os.path.exists(folder):
            self.__folder = folder
        else:
            print('Could not find given folder ({})'.format(folder))

    def __repr__(self) -> str:
        return 'rawGPCfolder of experiment IN PROGRESS'

    def getFolder(self):
        return self.__folder

    def getAllFiles(self):
        return [file for _, _, file, in os.walk(self.__folder)][0]

    def getTextFiles(self, full_path = False, object = False):
        files = self.getAllFiles()
        txt_files = [file for file in files if file.split('.')[-1]== 'TXT' or file.split('.')[-1]== 'txt'] # Only txt files, ignore the overview csv files
        txt_files.sort( key = lambda x: int(x.split('_')[0]))
        if full_path:
            txt_files = [os.path.join(self.__folder, textfile) for textfile in txt_files]
        if object:
            txt_files = [gpctextfile_V2.AnalyzeGPCtxt(i) for i in txt_files]
        return txt_files
    
    def getFile(self, i, full_path = False, object = True):
        files = self.getTextFiles(full_path=full_path)
        if i > len(files):
            raise IndexError("Only {} files in subfolder. (Given index: {})".format(len(files),i))
        if object:
            return gpctextfile_V2.AnalyzeGPCtxt(files[i])
        return files[i]

    def getTimeFiledict(self)-> dict:
        '''
        Creates dict with key= gpc injection data and value=txt file
        '''
        timeFileDict = {}
        for file in self.getTextFiles(full_path=True):
            gpc = gpctextfile_V2.AnalyzeGPCtxt(file)
            timeFileDict.update({gpc.InjectDate:file})
        return timeFileDict
    
    
    def validate_all(self):
        '''
        In PRORGRESS

        want to put all the raw data of one exp in one figure
        '''
        fig, axes = plt.subplots(2,2)
        for gpc in self.getTextFiles(full_path = True, object = True):
            print(axes)
            print(axes[0])
            print(type(axes[0]))
            gpc.getRAW_ax(axes[0][0],show = False)
            break
            

        plt.show()