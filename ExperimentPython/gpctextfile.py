import os
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from shutil import copyfile

class AnalyzeGPCtxt:
    '''Analysis of GPC text files.
    Parameters
    -----------
    textfile: Path
        directory of GPC text file
    '''
    def __init__(self, textfile):
        self.filename = textfile
        
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

            mwd_x, mwd_y = [],[]

            searchquery3 = 'MWDstart :'
            searchquery4 = 'MWDstop :'
            index_start_summary = np.array([x.startswith(searchquery3) for x in np.array(content)], dtype=bool)
            index_stop_summary = np.array([x.startswith(searchquery4) for x in np.array(content)], dtype=bool)

            lines4 =(content[(np.array(range(len(content)))[index_start_summary][0]+1):np.array(range(len(content)))[index_stop_summary][0]])
            lines5 =[ x.replace('\t\n', '\n').replace('\t ', ',').strip() for x in lines4]

            for line in lines5[2:]:
                mwd_x.append(float(line.split(',')[0]))
                mwd_y.append(float((line.split(',')[1]).strip()))
            self.MWD_x = mwd_x
            self.MWD_y = mwd_y

    def __repr__(self):
        return 'Analysis of {}'.format(self.filename)

    def show_distribution(self, info = False, color = 'skyblue'):
        """Displays distribution"""
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
        plt.show()
    
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

    