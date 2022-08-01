from tkinter import *
from tkinter import ttk
from tkinter import messagebox, filedialog
from PIL import Image, ImageTk
import numpy as np
import time
from time import gmtime, strftime, sleep
from glob import glob
from glob import iglob
import os
from os import walk
import shutil
import csv
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as mpatches
from datetime import datetime
import smtplib, ssl
from IPython import display
import pylab as pl
import smtplib, traceback, os, sys
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

import ExperimentFlow as startup
import experimentDF
import UpdateDF_NMRdata
import UpdateDF_GPCdata
import save_plots
import calculateScans

global Labviewscript
Labviewscript = 'GPC-NMR Timesweep_GUIversion_version4_lab112_gpcPC.vi' #This is the Labview script that is used

append2 = []
string_list=[]
def updateGUI(updatetext):
    now = datetime.now().strftime('{}/{}/{}  {}:{}:{}'.format('%d','%m','%y','%H', '%M','%S'))
    string = '{}\t\t{}'.format(now, updatetext)
    string_list.append(string)
    print(string)

    try:
        stabili_label = Label(parameter_frame_exp, text = string, anchor = 'w', bg = 'gray', width = 200)
        stabili_label.grid()
    except:
        pass

    if len(append2) == 0:    
        for string in string_list:
            if string.endswith('LabView Check: Communication folder found, subfolder created'):
                append2.append('yes')
                save_in = '{}/{}_OverviewText.txt'.format(experiment_extra.loc[0, 'Softwarefolder'],experiment_extra.loc[0,'code'])
                with open (save_in, 'w+') as textfile:
                    for string2 in string_list:
                        textfile.write(string2)
                        textfile.write('\n')
                textfile.close()
                save_in = '{}/{}_OverviewText.txt'.format(experiment_extra.loc[0, 'Softwarefolder'],experiment_extra.loc[0,'code'])
                break
            else:
                pass

            save_in = 'OverviewText.txt'
            with open (save_in, 'w+') as textfile:
                for string2 in string_list:
                    textfile.write(string2)
                    textfile.write('\n')
            textfile.close()

    elif len(append2) == 1:
        try:
            save_in = '{}/{}_OverviewText.txt'.format(experiment_extra.loc[0, 'Softwarefolder'],experiment_extra.loc[0,'code'])
            with open (save_in, 'a+') as textfile:
                textfile.write(string)
                textfile.write('\n')
            textfile.close()
        except:
            save_in = 'OverviewText.txt'
            with open (save_in, 'w+') as textfile:
                for text in string_list:
                    textfile.write(text)
                    textfile.write('\n')
            textfile.close()

#fonts
font_normal = ('Ariel', 15)
font_header = ('Courier',30)
font_button = ('Ariel', 10)
font_header_bold = ('Ariel', 18, 'bold')
font_entry = ('Ariel', 17)
font_small = ('Ariel', 10)
font_small_bold = ('Ariel', 10, 'bold')

box=dict(boxstyle="round", ec='black', fc='silver')

timesweepColor = 'indianred'
stabilisatinColor = 'skyblue'

DRIVE = 'S'

#for Simulation
interval_loop = float(15)
simul = 0 #0 is no simulation
if simul == 0:
    print('WARNING!!!!!! simul is on. SIMULATION, NO WAITING FOR STABILISATION TIME')

#Contstants
col_names = ['Start','Stop', 'volume', 'StartFR','StopFR', 'stabilisation time', 'dead volume 1', 'Dead Volume 2', 'GPC Interval', 'Dead Volume 3','Dilution FR', 'DeadVolume1(min)', 'DeadVolume2(min)', 'DeadVolume3(min)', 'NMR interval', 'mode']
parametersDF = pd.DataFrame(columns = col_names)
overviewscansDF = pd.DataFrame(columns= ['Start entry','Start Scan NMR', 'Stop Scan NMR', 'Start Scan GPC', 'Stop Scan GPC', 'GPC Samples', 'tresGPCinjections'])
experiment_extra = pd.DataFrame(columns = ['code', 'Mainfolder','GPCfolder', 'Timesweepfolder', 'Infofolder','Softwarefolder', 'Rawfolder', 'Plotsfolder'])

def check_Emailconnection():
    '''Checks the SMTP connection
    Returns
    -------
    server_status: int
        SMTP status code
        250 (Requested mail action okay, completed)
        535 (Username and Password not accepted, set 'Allow less secure apps' ON)
        '''
    username = 'polymerautomation@gmail.com'
    password = 'PRD@Monash'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    
    try:
        server.login(username,password)
        server_status = server.noop()[0]

    except smtplib.SMTPAuthenticationError as e:
        server_status = e.smtp_code

    return server_status

def defining_communication_folder(parentfolder, update = False):
    global Temporary_textfile
    global Pathlastexp_textfile
    global CommunicationMainFolder
    try:   
        CommunicationMainFolder = parentfolder
        Temporary_textfile = open(CommunicationMainFolder + '/temporary_experiment.txt', 'w').close()
        Temporary_textfile = CommunicationMainFolder + '/temporary_experiment.txt'
        Pathlastexp_textfile = CommunicationMainFolder + '/PathLastExperiment.txt'
        if update:
            updateGUI("New CommunicationMainFolder: {}".format(CommunicationMainFolder))
        else:
            updateGUI("CommunicationMainFolder: {}".format(CommunicationMainFolder))
    except FileNotFoundError as e:
        print('If in lab, use Z:/Sci-Chem/...')
        raise

def defining_PsswinFolder(folder, update = False):
    global PsswinFolder
    PsswinFolder = folder
    if update:
        updateGUI("New Psswin: {}".format(folder))
    else:
        updateGUI("Psswin: {}".format(folder))
def defining_NMRFolder(folder, update = False):
    global NMRFolder
    NMRFolder = folder
    if update:
        updateGUI("New NMR: {}".format(folder))
    else:
        updateGUI("NMR: {}".format(folder))


defining_communication_folder('{}:/Sci-Chem/PRD/NMR 112/Automated Platform/Final_LabView_allVIs/PythonCommunication'.format(DRIVE))
defining_PsswinFolder('{}:/Sci-Chem/PRD/GPC 112/2018-March/Projects'.format(DRIVE))
#defining_NMRFolder('{}:/Sci-Chem/PRD/NMR 112'.format(DRIVE))
defining_NMRFolder('C:/PROJECTS/DATA')

statusCode = check_Emailconnection()
if statusCode == 250:
    updateGUI('Email OK (250)')
    emailCheck = True
elif statusCode ==535:
    updateGUI('Email not OK (535, Username and Password not accepted, set "Allow less secure apps" ON)')
    emailCheck = False
else:
    updateGUI('Unknown Email Error, email option not in use')
    emailCheck = False

def DebugPrintInitilisation (printedString):
    debug= False
    if debug == True:
        print('\t{}'.format(printedString))
    else:
        pass
def DebugPrintTiming (printedString):
    debug= False
    if debug == True:
        print('\t{}'.format(printedString))
    else:
        pass
def debugPrintFig(printedString):
    debug= False
    if debug == True:
        print('\t{}'.format(printedString))
    else:
        pass
def debugPrint(printedString):
    debug= True
    if debug == True:
        print('\t{}'.format(printedString))
    else:
        pass

try:
    monomerDF = pd.read_csv('Monomer_info.csv')
    updateGUI('Monomor file found ({} monomers defined)...'.format(monomerDF.shape[0]))
except:
    monomerDF = pd.DataFrame()
    updateGUI('Could not find Monomer_infO.csv')

def df_to_csv(content, Filename, folder):
    folder = str(folder)
    folder1 = folder.replace("\\","/")
    
    if os.path.exists(folder1) == True: 
        try:
            content.to_csv('{}/{}.csv'.format(folder1, Filename))

        except IOError:
            saved = False
            i = 0
            while saved == False:
                try:
                    content.to_csv('{}/{}_updated{}.csv'.format(folder1, Filename, i))
                    print('Original file is open, new file created: {}_updated{}.csv'.format(Filename, i))
                    saved = True
                except:
                    i += 1
    else:
        print('Experiment folder not found...')
        try:
            content.to_csv('{}.csv'.format(Filename))
            print('File created in {}.'.format(os.getcwd()))
        except IOError:
            saved = False
            i = 0
            while saved == False:
                try:
                    content.to_csv('{}_updated{}.csv'.format(Filename, i))
                    print('Previous Updated file is open, new file created: {}_updated{}.csv'.format(Filename, i))
                    saved = True
                except:
                    i += 1

def sendEmail (AttachementPNG):
    '''If error, check if 'Less Secure app access' in privacy settings of email is ON!'''
    print('def sendEmail')
    #define mail address from which e-mail with error code is sent
    fromaddr = 'polymerautomation@gmail.com'
    #define mail address to which e-mail with error code is sent
    toaddrs  = experiment_extra.loc[0,'Emails']
    print(toaddrs)
    if len(toaddrs) == 0:
        updateGUI('No email adress was given. No email sent.')
        return 'No email'
    else:
        print('Sending Email')

    #define the multipart message
    print("check 1")
    msg = MIMEMultipart()
    msg['Subject'] = 'Timesweep Experiment ({}) Finished'.format(experiment_extra.loc[0,'code'])
    msg['From'] = fromaddr
    print("check 2")
    text = MIMEText('Dear User,\n\nyour timesweep experiment is finished.\n\nIn the attachement, you can find the NMR and the GPC data.\n\nA detailed overview of the experiment can be found in the following directory:\n{}\n\nKind Regards,\nAutomation Platform'.format(experiment_extra.loc[0,'Mainfolder']))
    msg.attach(text)
    for ImgFileName in AttachementPNG:
        img_data = open(ImgFileName, 'rb').read()
        image = MIMEImage(img_data, name=os.path.basename(ImgFileName))
        msg.attach(image)
    print("check 3")
    # define account and sending details
    username = 'polymerautomation@gmail.com'
    password = 'PRD@Monash'
    server = smtplib.SMTP('smtp.gmail.com:587')
    server.ehlo()
    server.starttls()
    server.login(username,password)
    for receiver in toaddrs:
        try:
            print('check4')
            msg['To'] = receiver
            print('check5')
            server.sendmail(fromaddr, receiver, msg.as_string())
            print('check6')
            updateGUI('Email sent to {}'.format(receiver))
            print('check7')
        except:
            print('no email send')
            updateGUI('Could not send email to {}'.format(receiver))
    server.quit()
    return 'Emails okay'


def WaitstabilisationTime():
    '''Calculates stabilisation time (for first timesweep) and waits time (sleep)
    '''
    DebugPrintInitilisation('WaitstabilisationTime')

    #extracts StartFR (flowrate from first timesweep), reactor volume and stabilisation factor from parameters dataframe and calculates waiting time
    start, volume, stabilisationfactor = parametersDF.loc[0,'StartFR'], parametersDF.loc[0,'volume'], parametersDF.loc[0,'stabilisation time']
    waiting_time = (volume * stabilisationfactor) / start #in minutes

    DebugPrintInitilisation('\tStabilisation time calculated')

    updateGUI('After stabilisation ({} min), start spinsolve and set the following integration borders in the spectra: {}'.format(waiting_time, experiment_extra.loc[0, 'integrals']))
    
    waiting_timesec= waiting_time *60 #for sleep function!!

    #if simulation, no stabilisation time
    if simul == 0:
        DebugPrintInitilisation('\tNo simulation, waiting stabilisation ({} min)...'.format(waiting_time))
        sleep(waiting_timesec)
        updateGUI('Stabilisation done')
    else:
        updateGUI('wait 2 seconds (normally stabilisation time)')
        sleep(2)
        DebugPrintInitilisation('\tnSimulation, only wait 2 sec')

def ExperimentFlow ():
    '''Called by startexp();\n
    (i) wait stabilisation time, 
    (ii) exports csv file with all scannumbers to experiment folder, 
    (iii) creates experimentDF (also to csv),
    (iv) starts NMR and GPC data collection in loop'''

    DebugPrintInitilisation('ExperimentFlow')

    WaitstabilisationTime()
    code = experiment_extra.loc[0, 'code']
    mode = parametersDF.loc[0, 'mode']

    scansDF = calculateScans.CalculateScans(parametersDF, mode = mode)
    scansDF_directory = '{}/{}_{}'.format(experiment_extra.loc[0, 'Softwarefolder'], code, 'Scans.csv')
    scansDF.to_csv(scansDF_directory) #saves scans in csv file

    NMRfolder = startup.SearchForNMRfolder(NMRFolder, code, WARNING_TIMER=30)
    
    expDF_directory = '{}/{}_Experiment'.format(experiment_extra.loc[0, 'Softwarefolder'], code)
    expDF = experimentDF.create_experimentDF(scansDF, parametersDF, mode, expDF_directory)
    updateGUI("Experiment csv file created ({}.csv)".format(expDF_directory))
    
    
    analysis = True
    gpc_number = 0
    modify_time = 0
    saving_directory_plots, GPCfolder, infofolder, rawGPCfolder = experiment_extra.loc[0, ['Plotsfolder', 'GPCfolder', 'Infofolder', 'Rawfolder']]
    nmr_interval = parametersDF.loc[0,'NMR interval']

    while analysis:
        print("sleeps {}".format(nmr_interval))
        sleep(nmr_interval)
        #nextLoop = input('>> Next Loop press ENTER')
        expDF, newNMR_bool, modify_time = UpdateDF_NMRdata.updateDF_integrals(expDF, NMRfolder, expDF_directory, mode, SolutionDataframe, modify_time)
        if newNMR_bool == False:
            try:
                save_plots.save_scanconversion(expDF, code, saving_directory_plots)
                save_plots.save_scanintegrals(expDF, code, saving_directory_plots)
                save_plots.save_tresconversion(expDF, code, saving_directory_plots)
                save_plots.save_fit(expDF, code, saving_directory_plots)
            except PermissionError:
                print('Please close the .png files to update the experiment plots')
            except:
                print('could not save plots for unknown reason')
            continue

        if mode == 'GPCandNMR':    
            expDF, gpc_number, newGPC = UpdateDF_GPCdata.search_newGPC(PsswinFolder, code, gpc_number, expDF, expDF_directory, GPCfolder, infofolder, rawGPCfolder)
            if newGPC:
                try:
                    save_plots.save_tresMn(expDF, code, saving_directory_plots)
                    save_plots.save_conversionMn(expDF, code, saving_directory_plots)
                except PermissionError:
                    print('Please close the .png files to update the experiment plots')
                    print('GPC plots are updated')
        try:
            save_plots.save_scanconversion(expDF, code, saving_directory_plots)
            save_plots.save_scanintegrals(expDF, code, saving_directory_plots)
            save_plots.save_tresconversion(expDF, code, saving_directory_plots)
        except PermissionError:
            print('Please close the .png files to update the experiment plots')
            
       
        try:
            expDF.to_csv('{}/{}_data.csv'.format(experiment_extra.loc[0,'Mainfolder'], code))
        except:
            pass

    print('End of Experiment')
       
def startexp():
    """ Starts LabVIEW by writting 'start' in text file. Calls ExperimentFlow()"""
    DebugPrintInitilisation('startexp')

    startfile = open(Temporary_textfile, 'w') 
    startfile.write('start')
    startfile.close()

    #name_file_tresconversion = '{}-Tres-conversion.png'.format(experiment_extra.loc[0,'code'])
    #print('{}/{}'.format(experiment_extra.loc[0,'Mainfolder'] ,name_file_tresconversion))

    DebugPrintInitilisation('\tStart written in textfile. LabView should start.')
    updateGUI('Start Spinsolve after Stabilisation')
    ExperimentFlow()


def SearchCommunicationFolder(folder):
    '''
    Makes the different data folders in the main experiment folder.

    input:\n Folder

    Output:\n1) Folder where GPCs are going to be stored.\n2) Folder where timesweeps are going to be stored.\n3) Folder where Raw GPCs are going to be stored.\n4) Folder where experiment details are going to be stored.\n5) Folder where Injection infos are going to be stored.
    '''
    global SolutionDataframe

    mode = parametersDF.loc[0, 'mode']

    newfolderTimesweepdata = os.path.join(folder, 'Timesweep Data')
    if not os.path.exists(newfolderTimesweepdata):
        os.mkdir(newfolderTimesweepdata)
    newfoldersoftware = os.path.join(folder, 'Software details')
    if not os.path.exists(newfoldersoftware):
        os.mkdir(newfoldersoftware)
    parametersDF.to_csv('{}/ParameterDF.csv'.format(newfoldersoftware))
    newfolderplots = os.path.join(folder, 'Plots')
    if not os.path.exists(newfolderplots):
        os.mkdir(newfolderplots)  

    if str(mode) == 'GPCandNMR':
        newfolderGPC = os.path.join(folder, 'Filtered GPC Data')
        if not os.path.exists(newfolderGPC):
            os.mkdir(newfolderGPC)

        newfolderinfoGPC = os.path.join(folder, 'Info GPC Injections')
        if not os.path.exists(newfolderinfoGPC):
            os.mkdir(newfolderinfoGPC)

        newfolderRawGPC = os.path.join(folder, 'Raw GPC text files')
        if not os.path.exists(newfolderRawGPC):
            os.mkdir(newfolderRawGPC)

    elif mode == 'NMR':
        newfolderGPC, newfolderinfoGPC, newfolderRawGPC = 'NaN', 'NaN', 'NaN'        
    
    updateGUI('Data folders are created in experiment folder')

    experiment_extra.loc[0, ['GPCfolder', 'Timesweepfolder', 'Infofolder','Softwarefolder', 'Rawfolder', 'Plotsfolder']] = str(newfolderGPC).replace("\\","/"), str(newfolderTimesweepdata).replace("\\","/"), str(newfolderinfoGPC).replace("\\","/"),str(newfoldersoftware).replace("\\","/"),str(newfolderRawGPC).replace("\\","/"), str(newfolderplots).replace("\\","/")
    experiment_extra.to_csv('{}/extras_experiment.csv'.format(newfoldersoftware))

    if not SolutionDataframe.empty:
        SolutionDataframe.to_csv('{}/ReactionSolution_{}.csv'.format(newfoldersoftware, experiment_extra.loc[0,'code']))
        updateGUI('Solution Dataframe saved in software subfolder')
    else:
        updateGUI('No Solution Details given')
    return newfolderGPC, newfolderTimesweepdata, newfolderRawGPC

def isfloat(x):
    """ Checks if value is float. Returns Boolean. True if value is float"""
    try:
        a = float(x)
    except ValueError:
        updateGUI('\tError: No change, entry needs to be a number')
        return False
    else:
        return True

spinsolveImage = 'Spinsolve.png'      
##### APP ####
root = Tk()
root.title('NMR Platform')
root.geometry('{}x{}'.format(1000, 750))
root.resizable(False, False)
root.wm_iconbitmap('Pictures\Benchtop NMR.ico')

def NMRGPC():
    tab_control.tab(tab_wGPC_Setup, state = 'normal')
    tab_control.tab(tab_wGPC_Timesweeps, state = 'disabled')
    tab_control.tab(tab_wGPC_Initialisation, state = 'disabled')
    tab_control.tab(tab_wGPC_Conversion, state = 'disabled')
    tab_control.insert(1, tab_overview, state = 'normal')
    tab_control.select(tab_wGPC_Setup)
    optionNMR_btm.configure(state= 'disabled')
    optionwGPC_btm.configure(state= 'disabled')
    updateGUI('Mode: NMR and GPC')


def NMR():
    tab_control.tab(tab_wGPC_Setup, state = 'hidden')
    tab_control.tab(tab_wGPC_Timesweeps, state = 'hidden')
    tab_control.tab(tab_wGPC_Conversion, state = 'hidden')
    tab_control.tab(tab_wGPC_Initialisation, state = 'hidden')
    
    tab_control.tab(tab_NMR_Setup, state = 'normal')
    tab_control.tab(tab_NMR_Timesweeps, state = 'disabled')
    tab_control.tab(tab_NMR_Initialisation, state = 'disabled')
    tab_control.tab(tab_NMR_Conversion, state = 'disabled')
    tab_control.insert(1, tab_overview, state = 'normal')
    optionNMR_btm.configure(state= 'disabled')
    optionwGPC_btm.configure(state= 'disabled')
    tab_control.select(tab_NMR_Setup)
    updateGUI('Mode: NMR')

#create tabs
tab_control = ttk.Notebook(root)
tab_welcome = ttk.Frame(tab_control)
tab_control.add(tab_welcome, text='Welcome')
tab_overview = ttk.Frame(tab_control)
tab_control.add(tab_overview, text='Experiment', state ='hidden')

###Welcome Tab ###
Welcome_top_frame = Frame(tab_welcome, bg='white', width=1000, height=50, pady=3, padx = 400)
Welcome_top_frame.grid(row=0, sticky = 'ew')
header_Welcome = Label(Welcome_top_frame, text= 'Welcome',bg='white', font = font_header)
header_Welcome.grid()

Welcome_Option_frame = Frame(tab_welcome)
Welcome_Option_frame.grid()
Welcom_option_frame_header = Label(Welcome_Option_frame, text = 'Choose a mode of operation', font = font_header_bold)
Welcom_option_frame_header.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)
optionNMR_btm = Button(Welcome_Option_frame, text = "NMR", command = NMR,width = 20, height = 3, font = font_header_bold)
optionNMR_btm.grid(row = 1, column = 0, padx = 10, pady=10)
optionwGPC_btm = Button(Welcome_Option_frame, text = "NMR-GPC", command = NMRGPC, width = 20, height = 3, font = font_header_bold)
optionwGPC_btm.grid(row =1, column = 1, padx = 10, pady = 10)

def update_comfolder():
    global comfolder_path
    filename = filedialog.askdirectory()
    comfolder_path.set(filename)
    defining_communication_folder(filename, update = True)

comfolder_label = Label(Welcome_Option_frame,text="Communication Folder", font = font_entry)
comfolder_label.grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 10)
comfolder_path = StringVar(value =CommunicationMainFolder)
comfolder = Label(Welcome_Option_frame,textvariable=comfolder_path)
comfolder.grid(row=3, column=0, columnspan = 2)
comfolder_btn = Button(Welcome_Option_frame, text="Browse", command=update_comfolder)
comfolder_btn.grid(row=3, column=2)

def update_NMRmainfolder():
    global NMRmainfolder_path
    filename = filedialog.askdirectory()
    NMRmainfolder_path.set(filename)
    defining_NMRFolder(filename, update = True)

NMRmainfolder_label = Label(Welcome_Option_frame,text="Spinsolve Folder", font = font_entry)
NMRmainfolder_label.grid(row = 4, column = 0, columnspan = 2, padx = 10, pady = 10)
NMRmainfolder_path = StringVar(value = NMRFolder)
NMRmainfolder = Label(Welcome_Option_frame,textvariable=NMRmainfolder_path)
NMRmainfolder.grid(row=5, column=0, columnspan = 2)
NMRmainfolder_btn = Button(Welcome_Option_frame, text="Browse", command=update_NMRmainfolder)
NMRmainfolder_btn.grid(row=5, column=2)

def update_Psswinmainfolder():
    global Psswinmainfolder_path
    filename = filedialog.askdirectory()
    Psswinmainfolder_path.set(filename)
    defining_NMRFolder(filename, update = True)

Psswinmainfolder_label = Label(Welcome_Option_frame,text="Psswin Folder", font = font_entry)
Psswinmainfolder_label.grid(row = 6, column = 0, columnspan = 2, padx = 10, pady = 10)
Psswinmainfolder_path = StringVar(value = PsswinFolder)
Psswinmainfolder = Label(Welcome_Option_frame,textvariable=Psswinmainfolder_path)
Psswinmainfolder.grid(row=7, column=0, columnspan = 2)
Psswinmainfolder_btn = Button(Welcome_Option_frame, text="Browse", command=update_Psswinmainfolder)
Psswinmainfolder_btn.grid(row=7, column=2)

labviewscript_info = Label(Welcome_Option_frame, text = "Labview script", font= font_small_bold)
labviewscript_info.grid(row = 8, column = 0, columnspan = 2, padx = 10)
script = Label(Welcome_Option_frame, text = Labviewscript, font= font_small)
script.grid(row=9, column=0, columnspan = 2)


#GPC-NMR tabs
tab_wGPC_Setup = ttk.Frame(tab_control)
tab_wGPC_Timesweeps = ttk.Frame(tab_control)
tab_wGPC_Conversion = ttk.Frame(tab_control)
tab_wGPC_Initialisation = ttk.Frame(tab_control)

tab_control.add(tab_wGPC_Setup, text = 'Setup', state = 'disabled')
tab_control.add(tab_wGPC_Timesweeps, text='Timesweeps', state = 'disabled')
tab_control.add(tab_wGPC_Conversion, text='Conversion', state = 'hidden')
tab_control.add(tab_wGPC_Initialisation, text='Initialisation', state = 'disabled')

#only NMR tabs
tab_NMR_Setup = ttk.Frame(tab_control)
tab_NMR_Timesweeps = ttk.Frame(tab_control)
tab_NMR_Conversion = ttk.Frame(tab_control)
tab_NMR_Initialisation = ttk.Frame(tab_control)


tab_control.add(tab_NMR_Setup, text = 'Setup', state = 'hidden')
tab_control.add(tab_NMR_Timesweeps, text='Timesweeps', state = 'hidden')
tab_control.add(tab_NMR_Conversion, text='Conversion', state = 'hidden')
tab_control.add(tab_NMR_Initialisation, text='Initialisation', state = 'hidden')


tab_LabView_help = ttk.Frame(tab_control)
tab_control.add(tab_LabView_help, text = 'LabView Help', state = 'hidden')
tab_Pss_help = ttk.Frame(tab_control)
tab_control.add(tab_Pss_help, text = 'Pss Help', state = 'hidden')
tab_Spinsolve_help = ttk.Frame(tab_control)
tab_control.add(tab_Spinsolve_help, text = 'Spinsolve Help', state = 'hidden')

def goback():
    if parametersDF.loc[0, 'mode'] == 'GPCandNMR':
        tab_control.tab(tab_wGPC_Initialisation, state = 'normal')
        tab_control.tab(tab_wGPC_Setup, state = 'normal')
        tab_control.tab(tab_wGPC_Timesweeps, state = 'normal')
        tab_control.tab(tab_LabView_help, state = 'hidden')
        tab_control.tab(tab_Pss_help, state = 'hidden')
        tab_control.tab(tab_Spinsolve_help, state = 'hidden')
        tab_control.select(tab_wGPC_Initialisation)
    elif parametersDF.loc[0, 'mode'] == 'NMR':
        tab_control.tab(tab_NMR_Initialisation, state = 'normal')
        tab_control.tab(tab_NMR_Setup, state = 'normal')
        tab_control.tab(tab_NMR_Timesweeps, state = 'normal')
        tab_control.tab(tab_LabView_help, state = 'hidden')
        tab_control.tab(tab_Pss_help, state = 'hidden')
        tab_control.tab(tab_Spinsolve_help, state = 'hidden')
        tab_control.select(tab_NMR_Initialisation)
    else:
        print('ERROR! NOT SUPPOSSED TO HAPPEN')
        root.destroy()
        
###LABVIEW HELP TAB###
LabviewHelp_top_frame = Frame(tab_LabView_help, bg='white', width=1000, height=50, pady=3, padx = 400)
LabviewHelp_top_frame.grid(row=0, sticky = 'ew')
header_LabviewHelp = Label(LabviewHelp_top_frame, text= 'Labview Help',bg='white', font = font_header)
header_LabviewHelp.grid()

LabviewHelp_picture_frame = Frame(tab_LabView_help)
LabviewHelp_picture_frame.grid()

LabviewHelp_picture_Step1 = PhotoImage(file = 'Pictures\Labview_Step1.png')
LabviewHelp_picture_Step1_Label = Label(master = LabviewHelp_picture_frame, image= LabviewHelp_picture_Step1)
LabviewHelp_picture_Step1_Label.grid(row = 0, column =0, padx = 10, pady= 10)

LabviewHelp_picture_Step2 = PhotoImage(file = 'Pictures\Labview_Step2.png')
LabviewHelp_picture_Step2_Label = Label(master = LabviewHelp_picture_frame, image= LabviewHelp_picture_Step2)
LabviewHelp_picture_Step2_Label.grid(row = 1, column = 0, padx = 10, pady= 10)

LabviewHelp_bottom_frame = Frame(tab_LabView_help, width=1000, height=50, pady=3, padx = 400)
LabviewHelp_bottom_frame.grid()
back_help_LabView = Button(LabviewHelp_bottom_frame, text = 'back', command = goback, font = font_button, width = 6)
back_help_LabView.grid()

###Pss HELP TAB###  
PssHelp_top_frame = Frame(tab_Pss_help, bg='white', width=1000, height=50, pady=3, padx = 400)
PssHelp_top_frame.grid(row=0, sticky = 'ew')
header_PssHelp = Label(PssHelp_top_frame, text= 'Pss Help',bg='white', font = font_header)
header_PssHelp.grid()

PssHelp_picture_frame = Frame(tab_Pss_help, bg = 'red')
PssHelp_picture_frame.grid()

PssHelp_picture_Step1 = PhotoImage(file = 'Pictures\Pss_Step1.png')
PssHelp_picture_Step1_Label = Label(master = PssHelp_picture_frame, image= PssHelp_picture_Step1)
PssHelp_picture_Step1_Label.grid(row = 0, column =0, padx = 10, pady= 10)

PssHelp_picture_Step2 = PhotoImage(file = 'Pictures\Pss_Step2.png')
PssHelp_picture_Step2_Label = Label(master = PssHelp_picture_frame, image= PssHelp_picture_Step2)
PssHelp_picture_Step2_Label.grid(row = 0, column = 1, padx = 10, pady= 10)

PssHelp_picture_Step3 = PhotoImage(file = 'Pictures\Pss_Step3.png')
PssHelp_picture_Step3_Label = Label(master = PssHelp_picture_frame, image= PssHelp_picture_Step3)
PssHelp_picture_Step3_Label.grid(row = 1, column = 0, padx = 10, pady= 10)

PssHelp_picture_Step4 = PhotoImage(file = 'Pictures\Pss_Step4.png')
PssHelp_picture_Step4_Label = Label(master = PssHelp_picture_frame, image= PssHelp_picture_Step4)
PssHelp_picture_Step4_Label.grid(row = 1, column = 1, padx = 10, pady= 10)

PssHelp_bottom_frame = Frame(tab_Pss_help, width=1000, height=50, pady=3, padx = 400)
PssHelp_bottom_frame.grid()
PssHelp_back = Button(PssHelp_bottom_frame, text = 'back', command = goback, font = font_button, width = 6)
PssHelp_back.grid()

###Spinsolve HELP TAB###  
SpinsolveHelp_top_frame = Frame(tab_Spinsolve_help, bg='white', width=1000, height=50, pady=3, padx = 400)
SpinsolveHelp_top_frame.grid(row=0, sticky = 'ew')
header_SpinsolveHelp = Label(SpinsolveHelp_top_frame, text= 'Spinsolve Help',bg='white', font = font_header)
header_SpinsolveHelp.grid()

SpinsolveHelp_picture_frame = Frame(tab_Spinsolve_help)
SpinsolveHelp_picture_frame.grid(sticky = 'w')

SpinsolveHelp_picture_Step1 = PhotoImage(file = 'Pictures\Spinsolve_Step1_final.png')
SpinsolveHelp_picture_Step1_Label = Label(master = SpinsolveHelp_picture_frame, image= SpinsolveHelp_picture_Step1)
SpinsolveHelp_picture_Step1_Label.grid(row = 0, column =0, padx = 10, pady= 10)

SpinsolveHelp_picture_Step2 = PhotoImage(file = 'Pictures\Spinsolve_Step2_final.png')
SpinsolveHelp_picture_Step2_Label = Label(master = SpinsolveHelp_picture_frame, image= SpinsolveHelp_picture_Step2)
SpinsolveHelp_picture_Step2_Label.grid(row = 0, column = 1, padx = 10, pady= 10)

SpinsolveHelp_picture_Step3 = PhotoImage(file = 'Pictures\Spinsolve_Step3_final.png')
SpinsolveHelp_picture_Step3_Label = Label(master = SpinsolveHelp_picture_frame, image= SpinsolveHelp_picture_Step3)
SpinsolveHelp_picture_Step3_Label.grid(row = 1, column = 0, padx = 10, pady= 10)

SpinsolveHelp_picture_Step4 = PhotoImage(file = 'Pictures\Spinsolve_Step4_final.png')
SpinsolveHelp_picture_Step4_Label = Label(master = SpinsolveHelp_picture_frame, image= SpinsolveHelp_picture_Step4)
SpinsolveHelp_picture_Step4_Label.grid(row = 1, column = 1, padx = 3, pady= 10)

SpinsolveHelp_bottom_frame = Frame(tab_Spinsolve_help, width=1000, height=50, pady=3, padx = 400)
SpinsolveHelp_bottom_frame.grid()
back_help_LabView = Button(SpinsolveHelp_bottom_frame, text = 'back', command = goback, font = font_button, width = 6)
back_help_LabView.grid()

###SETUP TAB###
#Create Main frame of Setup Tab
wGPC_setup_top_frame = Frame(tab_wGPC_Setup, bg='white', width=1000, height=50, pady=3, padx = 400)
wGPC_setup_top_frame.grid(row=0, sticky = 'ew')

wGPC_setup_picture_frame = Frame(tab_wGPC_Setup, bg='white', width=1000, height=300, padx=175, pady=3)
wGPC_setup_picture_frame.grid(row=1,sticky = 'ew')

wGPC_setup_parameter_frame = Frame(tab_wGPC_Setup, bg='gray', width=1000, height=350, pady=3)
wGPC_setup_parameter_frame.grid(row=2,sticky = 'ew')

wGPC_setup_confirm_frame = Frame(tab_wGPC_Setup, bg='gray', width=1000, height=50, pady=10, padx = 400)
wGPC_setup_confirm_frame.grid(row=4, sticky="ew")

#Make-Up Top Frame
name_window = Label(wGPC_setup_top_frame, text= 'Setup',bg='white')
name_window.config(font=font_header)
name_window.grid()

#Make-Up Picture_frame
wGPC_picure_setup = PhotoImage(file = 'Pictures/NMRGPCsetup.png')
wGPC_LabelPicture = Label(master = wGPC_setup_picture_frame, image= wGPC_picure_setup, bg ='white')
wGPC_LabelPicture.grid()
    
#make-up Parameter frame
def change_values():
    updateGUI('Parameters Changed')
    list_parameters = parameterList1
    entries = [i[0] for i in list_parameters]
    entries_values = [i.get() for i in entries]

    for i, value in enumerate(entries_values):
        if list(value) == []:
            pass
        else:
            if isfloat(value) == True and float(list_parameters[i][4]) != float(value):
                if float(value) == 0:
                    return updateGUI('\tNo changes, entry needs to be non-zero value.')
                else:
                    parameterList1[i][4] = float(value)
            else:
                pass

    for i, parameter in enumerate(parameterList1):
        parameter[1] = Label(wGPC_setup_parameter_frame, text = parameter[4], bg = 'gray', width = 20)
        parameter[1].config(font=font_normal, anchor = 'e')
        parameter[1].grid(row = i, column =4)
    
parameterList1 = [['entry1', 'default1', 'Reactor Volume', 'mL', 0.90, 'change1'],
            ['entry2', 'default2', 'Dead Volume 1', 'mL', 0.32,'change2' ],
            ['entry3', 'default3', 'Dead Volume 2', 'mL', 0.17 ,'change3'],
            ['entry4', 'default4', 'Dead Volume 3', 'mL', 0.17 ,'change4'],
            ['entry5', 'default5', 'NMR Interval', 'sec', 17 ,'change5'],
            ['entry6', 'default6', 'GPC Interval', 'minutes', 3 ,'change6'],
            ['entry7', 'default7', 'Stabilization factor', 'x', 1.3,'change7'],
            ['entry8', 'default87', 'Dilution Flowrate', 'mL/min', 1.5,'change8']]

for i, v in enumerate(parameterList1):
    parameter = Label(wGPC_setup_parameter_frame, text = v[2], bg = 'gray', width = 30)
    parameter.config(font=font_normal)
    parameter.grid(row = i, column =0)

    v[0] = Entry(wGPC_setup_parameter_frame, width = 15)
    v[0].grid(row = i, column = 1)

    unit = Label(wGPC_setup_parameter_frame, text = v[3], bg ='gray', width= 10)
    unit.config(font=font_normal, anchor = 'w')
    unit.grid(row = i, column = 2)

    v[5] = Button(wGPC_setup_parameter_frame, text= 'Change', command = change_values)
    v[5].grid(row =i, column = 3)
     
    v[1] = Label(wGPC_setup_parameter_frame, text = v[4], bg = 'gray', width = 20)
    v[1].config(font=font_normal, anchor = 'e')
    v[1].grid(row = i, column =4)

    unit2 = Label(wGPC_setup_parameter_frame, text = v[3], bg ='gray')
    unit2.config(font=font_normal)
    unit2.config(font = font_normal)
    unit2.grid(row = i, column = 5)


def extractChemicals():
    global RAFTlist
    global solventlist
    global initiatorlist
    global monomerlist
    global chemicals 

    chemicals = pd.read_csv('Chemicals.csv')

    RAFTlist = chemicals[chemicals["class"]=='RAFT']
    solventlist = chemicals[chemicals["class"]=='solvent']
    initiatorlist = chemicals[chemicals["class"]=='initiator']
    monomerlist = chemicals[chemicals["class"]=='monomer']

global SolutionDataframe
SolutionDataframe = pd.DataFrame()

def changeSolution():
    def confirmSolution():
        finalMonomer, finalSolvent, finalRAFT, finalInitiator = optionsMonomer.get(), optionsSolvent.get(), optionsRAFT.get(), optionsinitiator.get()
        if not isfloat(gramRAFT.get()) or not isfloat(graminitiator.get()) or not isfloat(mLMonomer.get()) or not isfloat(mLsolvent.get()):
            solution_popup.destroy()
            return None
        
        monomer,solvent, raft, initiator = (monomerlist[monomerlist['abbreviation']==finalMonomer]), (solventlist[solventlist['abbreviation']==finalSolvent]), (RAFTlist[RAFTlist['abbreviation']==finalRAFT]), (initiatorlist[initiatorlist['abbreviation']==finalInitiator])
        global SolutionDataframe
        SolutionDataframe = pd.concat([raft, monomer, initiator, solvent], ignore_index = True)

        #extract entries ()
        SolutionDataframe.loc[SolutionDataframe['class'] == 'RAFT', 'mass (g)'] = float(gramRAFT.get())
        SolutionDataframe.loc[SolutionDataframe['class'] == 'monomer', 'volume (mL)'] = float(mLMonomer.get())
        SolutionDataframe.loc[SolutionDataframe['class'] == 'initiator', 'mass (g)'] = float(graminitiator.get())
        SolutionDataframe.loc[SolutionDataframe['class'] == 'solvent', 'volume (mL)'] = float(mLsolvent.get())
        #convert volume to mass
        SolutionDataframe.loc[SolutionDataframe['class'] == 'monomer', 'mass (g)'] = float(mLMonomer.get()) * float(SolutionDataframe.loc[SolutionDataframe['class'] == 'monomer', 'density'])
        SolutionDataframe.loc[SolutionDataframe['class'] == 'solvent', 'mass (g)'] = float(mLsolvent.get()) * float(SolutionDataframe.loc[SolutionDataframe['class'] == 'solvent', 'density'])

        #moles in dataframe
        SolutionDataframe['moles (mol)'] = SolutionDataframe['mass (g)'] / SolutionDataframe['molecular mass']
        #molar in dataframe
        total_volume = SolutionDataframe['volume (mL)'].sum()
        SolutionDataframe['Molar (M)'] = SolutionDataframe['moles (mol)'] / (total_volume/1000)
        #eq in dataframe
        molesRAFT = float(SolutionDataframe.loc[SolutionDataframe['class']=='RAFT', 'moles (mol)'])
        SolutionDataframe['eq'] = [i/molesRAFT for i in SolutionDataframe['moles (mol)']]
        
        #create summary string
        #Monomer:Raft:ini xx:1:xxx (xxxx g/mol); xM Monomer; Solvent
        raft = SolutionDataframe.iloc[0]
        monomer = SolutionDataframe.iloc[1]
        initiator = SolutionDataframe.iloc[2]
        solvent = SolutionDataframe.iloc[3]

        Mn_100 = raft['molecular mass'] + (monomer['molecular mass']*monomer['eq'])
        
        summaryString = '{}:{}:{}  {} : {} : {} ( {} g/mol);\n {}M {};\n {}'.format(raft['abbreviation'], 
                                                                            monomer['abbreviation'], 
                                                                            initiator['abbreviation'],
                                                                            round(raft['eq'],1),
                                                                            round(monomer['eq'],2),
                                                                            round(initiator['eq'],2),
                                                                            round(Mn_100, 1),
                                                                            round(monomer['Molar (M)'],2),
                                                                            monomer['abbreviation'],
                                                                            solvent['abbreviation'])
        

        
        solution_popup.destroy()
        solutionSummary1.config(text = summaryString)
        solutionSummary.config(text = summaryString)
        updateGUI('Reaction Solution: {}'.format(summaryString.replace('\n','')))
        #solutionDataFrame.loc['Monomer'] = [finalMonomer, monomerlist.loc[monomerlist['name']== finalMonomer, 'molecular mass'], monomerlist.loc[monomerlist['name']== finalMonomer, 'density']]

    solution_popup = Toplevel()
    solution_popup.title('Reaction Solution')

    popuptitle = Label(solution_popup, text = 'Reaction Solution', font = font_header, padx=15)
    popuptitle.grid(row=0, column = 0, columnspan= 2)
    #monomer
    mLMonomer = Entry(solution_popup)
    mLMonomer.grid(row=1, column = 1)

    optionsMonomer = StringVar()
    optionsMonomer.set('MA')
    MenuMonomer = OptionMenu(solution_popup, optionsMonomer, *monomerlist['abbreviation'])
    MenuMonomer.grid(row = 1, column= 0)

    monomerlabel = Label(solution_popup, text = 'mL')
    monomerlabel.grid(row=1, column = 2)
    #RAFT
    gramRAFT = Entry(solution_popup)
    gramRAFT.grid(row=2, column = 1)

    optionsRAFT = StringVar()
    optionsRAFT.set('DoPAT')
    MenuRAFT = OptionMenu(solution_popup, optionsRAFT, *RAFTlist['abbreviation'])
    MenuRAFT.grid(row = 2, column= 0)

    RAFTlabel = Label(solution_popup, text = 'g')
    RAFTlabel.grid(row=2, column = 2)
    #initator
    graminitiator = Entry(solution_popup)
    graminitiator.grid(row=3, column = 1)

    optionsinitiator = StringVar()
    optionsinitiator.set("AIBN")
    MenuInitiator = OptionMenu(solution_popup, optionsinitiator, *initiatorlist['abbreviation'])
    MenuInitiator.grid(row = 3, column= 0)

    initiatorlabel = Label(solution_popup, text = 'g')
    initiatorlabel.grid(row=3, column = 2)
    #solvent
    mLsolvent = Entry(solution_popup)
    mLsolvent.grid(row=4, column = 1)

    optionsSolvent = StringVar()
    optionsSolvent.set("DMSO")
    MenuSolvent = OptionMenu(solution_popup, optionsSolvent, *solventlist['abbreviation'])
    MenuSolvent.grid(row = 4, column= 0)

    solventlabel = Label(solution_popup, text = 'mL')
    solventlabel.grid(row=4, column = 2)

    Confirmsolution2 = Button(solution_popup, text = 'Confirm', command = confirmSolution, font = font_button)
    Confirmsolution2.grid(row=5, column = 1)

     
extractChemicals()
solutionSummary1 = Label(wGPC_setup_parameter_frame, text = 'Reaction Solution', bg = 'gray', font = font_normal, pady = 20)
solutionSummary1.grid(row = i+1, column= 0, columnspan = 2, rowspan = 2 )
solution_button1 = Button(wGPC_setup_parameter_frame, text = 'Reaction solution', command = changeSolution)
solution_button1.grid(row = i+1, column= 3)


#maku-up btm-frame

def Confirm_reactor_parameters ():
    updateGUI('Reactor parameters confirmed')
    confirm_reactorParameters.configure(state = 'disabled')
    for parameterline in parameterList1:
        parameterline[5].configure(state = 'disabled')
        parameterline[0].configure(state = 'readonly')
    tab_control.tab(tab_wGPC_Timesweeps, state = 'normal')
    tab_control.select(tab_wGPC_Timesweeps)
    confirm_reactorParameters.configure(state = 'disabled')
    
confirm_reactorParameters = Button(wGPC_setup_confirm_frame, text = 'Confirm', command = Confirm_reactor_parameters, height= 3, width = 15, font = font_button)
confirm_reactorParameters.grid()

####TIMESWEEP TAB####
#Create Main frame of Timesweep Tab
wGPC_timesweep_top_frame = Frame(tab_wGPC_Timesweeps, bg='white', width=1000, height=50, pady=3, padx = 400)
wGPC_timesweep_top_frame.grid(row=0, sticky="ew")
wGPC_timesweep_picture_frame = Frame(tab_wGPC_Timesweeps, bg='white', width=1000, height=300, padx=175, pady=3)
wGPC_timesweep_picture_frame.grid(row=1, sticky="nsew")
wGPC_timesweep_parameter_frame = Frame(tab_wGPC_Timesweeps, bg='gray', width=1000, height=350, pady=3,padx = 3)
wGPC_timesweep_parameter_frame.grid(row=3, sticky="ew")
wGPC_timesweep_confirm_frame = Frame(tab_wGPC_Timesweeps, bg='gray', width=1000, height=50, pady=10, padx = 10)
wGPC_timesweep_confirm_frame.grid(row=4, sticky="ew")

#Make-Up Top Frame in Timesweep Tab
wGPC_timesweep_header = Label(wGPC_timesweep_top_frame, text= 'Timesweeps',bg='white')
wGPC_timesweep_header.config(font=font_header)
wGPC_timesweep_header.grid()

#Make-Up wGPC_timesweep_picture_frame in Timsweep Tab
picture_timesweep = PhotoImage(file = 'Pictures\Timesweeps_pictureFrame.png')
LabelPicture = Label(master = wGPC_timesweep_picture_frame, image=picture_timesweep, bg ='white')
LabelPicture.grid()

#Make-Up Parameter_frame_timesweep in Timesweep Tab
wGPC_all_ts_info = [] #list where all the timesweeps will be saved
reactorvol, NMRinterval1, GPCinterval1 = parameterList1[0][4],parameterList1[4][4],parameterList1[5][4]

def insert_timesweep():
    updateGUI('Timesweep added to experiment')

    #delete whitespaces in entry
    ts_from_en1 = (ts_from_en.get()).replace(' ', '')
    ts_to_en1 = (ts_to_en.get()).replace(' ', '')

    #checks if entry is number
    if isfloat(ts_from_en.get()) == True and isfloat(ts_to_en.get()):
        if float(ts_from_en1) != float(ts_to_en1) and float(ts_to_en1) != 0 and float(ts_from_en1) !=0:
            number_of_added_timesweep = len(wGPC_all_ts_info) +1

            from_ , to_ = float(ts_from_en.get()), float(ts_to_en.get())
            fr1, fr2 = float(reactorvol)/float(from_),float(reactorvol)/float(to_)

            timesweep_info = ['label_{}'.format(number_of_added_timesweep), 'Timesweep {}: From {} minutes ({} mL/min) to {} minutes ({} mL/min) (NMR interval: {}sec, GPC interval: {}min)'.format(number_of_added_timesweep, from_, round(fr1, 3), to_, round(fr2, 3), NMRinterval1, GPCinterval1), from_, to_]
            updateGUI('\tAdded timesweep: {}'.format(timesweep_info[1]))
            wGPC_all_ts_info.append(timesweep_info)

            for i, ts_info in enumerate(wGPC_all_ts_info):
                ts_info[0] = Label(wGPC_timesweep_parameter_frame, text = ts_info[1], bg = 'gray', width = 90, font = font_small, anchor = 'w')
                ts_info[0].grid(row = 5+i, columnspan = 6)

                entryText = DoubleVar()
                entryText.set(wGPC_all_ts_info[-1][-1])
                ts_from_en.configure(textvariable=entryText, state= 'readonly')

            confirm_ts_btm.config(state = 'normal')
            delete_ts_btm.config(state = 'normal')
        else:
            updateGUI('\tError: No change, entries cannot be the same')
    else:
        pass

def delete_timesweep():
    print(len(wGPC_all_ts_info) != 0)
    if len(wGPC_all_ts_info) != 0:
        updateGUI('Last timesweep deleted')
        updateGUI('\tDeleted timesweep: {}'.format(wGPC_all_ts_info[-1][1]))
        wGPC_all_ts_info[-1][0].destroy()
        wGPC_all_ts_info.pop(-1)
    else:
        pass

    if len(wGPC_all_ts_info) == 0:
        confirm_ts_btm.config(state = 'disabled')
        delete_ts_btm.config(state = 'disabled')
        entryText = DoubleVar()
        ts_from_en.configure(textvariable=entryText, state= 'normal')
    else:
        entryText = DoubleVar()
        entryText.set(wGPC_all_ts_info[-1][-1])
        ts_from_en.configure(textvariable=entryText, state= 'readonly')
        pass


tsparam = Label(wGPC_timesweep_parameter_frame, text = "Insert Timesweep Parameters", bg = 'gray', width = 27)
tsparam.config(font= font_header_bold)
    
ts_from_lbl = Label(wGPC_timesweep_parameter_frame, text = 'From (minutes)', width= 15, bg ='gray', font = font_normal, anchor = 'center')
ts_from_en = Entry(wGPC_timesweep_parameter_frame, width = 5, font= font_entry)

ts_to_lbl = Label(wGPC_timesweep_parameter_frame, text = 'To (minutes)', bg = 'gray', font = font_normal, anchor = 'center')
ts_to_en = Entry(wGPC_timesweep_parameter_frame, width = 5, font=font_entry)

insert_ts_btm = Button(wGPC_timesweep_parameter_frame, text = 'Add', command = insert_timesweep,font=font_button)
delete_ts_btm = Button(wGPC_timesweep_parameter_frame, text = 'Delete', command = delete_timesweep, font=font_button, state = 'disabled')

confirmed_ts = Label(wGPC_timesweep_parameter_frame, text = 'List of Timesweeps', bg ='gray')
confirmed_ts.config(font=font_header_bold, anchor ='w')

ts_from_lbl.grid(row = 1, column = 1, columnspan = 2)
ts_from_en.grid(row = 2, column = 1)
ts_to_lbl.grid(row = 1, column = 4, columnspan =2)
ts_to_en.grid(row = 2, column = 4) 
insert_ts_btm.grid(row = 3, column = 2)
delete_ts_btm.grid(row = 3, column = 3)
confirmed_ts.grid(row = 4, column =0)
tsparam.grid(row = 0, column =1, columnspan = 4)

def finalize_timesweeps ():
    print(wGPC_all_ts_info == 0)
    reactorvol = parameterList1[0][4]
        
    #f= open("//ad.monash.edu/home/User085/jvan0036/Documents/PhD/Joren/experiment.txt","a")
    for i, timesweep in enumerate(wGPC_all_ts_info):
        fr1, fr2 = reactorvol/timesweep[2], reactorvol/timesweep[3]
        #Create DF with all the parameters
        parametersDF.loc[i, 'Start']= timesweep[2]
        parametersDF.loc[i, 'Stop']= timesweep[3]
        parametersDF.loc[i, 'volume'] = parameterList1[0][4]
        parametersDF.loc[i, 'StartFR'] = fr1
        parametersDF.loc[i, 'StopFR'] = fr2
        parametersDF.loc[i, 'dead volume 1'] = parameterList1[1][4]
        parametersDF.loc[i, 'Dead Volume 2'] = parameterList1[2][4]
        parametersDF.loc[i, 'Dead Volume 3'] = parameterList1[3][4]
        parametersDF.loc[i, 'NMR interval'] = parameterList1[4][4]
        parametersDF.loc[i, 'GPC Interval'] = parameterList1[5][4]
        parametersDF.loc[i, 'stabilisation time'] = parameterList1[6][4]
        parametersDF.loc[i, 'Dilution FR'] = parameterList1[7][4]
        parametersDF.loc[i, 'DeadVolume1(min)'] = parametersDF.loc[i, 'dead volume 1']/parametersDF.loc[i,'StopFR']
        parametersDF.loc[i, 'DeadVolume2(min)'] = parametersDF.loc[i,'Dead Volume 2']/parametersDF.loc[i ,'StopFR']
        parametersDF.loc[i, 'DeadVolume3(min)'] = parametersDF.loc[i,'Dead Volume 3']/parametersDF.loc[i,'Dilution FR']
        parametersDF.loc[i, 'mode'] = 'GPCandNMR'
                
    updateGUI('Confirmed timesweep Experiment:\n{}'.format(parametersDF))
    scannumbers = calculateScans.CalculateScans(parametersDF, mode = 'GPCandNMR')
    print(scannumbers)
    totalscan = scannumbers['Stop Scan GPC'].iloc[-1]
    total_time = (totalscan * parametersDF.loc[0,'NMR interval']) /60
    totalgpc = sum([scannumbers['GPC Samples'].iloc[i] for i in range(int(scannumbers.shape[0]))])
        
    entry1 = parametersDF.iloc[0]
    stabili = ((entry1['volume']*entry1['stabilisation time']))
    allDvs = (((entry1['dead volume 1'] + entry1['Dead Volume 2']+ entry1['Dead Volume 3']) * int(scannumbers.shape[0])))
    ts_number= int(scannumbers.shape[0])
    totalvolume = stabili +(ts_number* allDvs)

    summary_1 = Label(wGPC_timesweep_confirm_frame, text = 'Total time:             {}min'.format(round(total_time,1)), width = 90, bg= 'gray', anchor = 'w',padx = 10)
    summary_1.grid(row= 1, column= 0)
    summary_2 = Label(wGPC_timesweep_confirm_frame, text = 'Total NMR scans:         {}'.format(round(totalscan,0)), width = 90, bg= 'gray', anchor = 'w')
    summary_2.grid(row= 2, column= 0)
    summary_3 = Label(wGPC_timesweep_confirm_frame, text = 'Total GPC samples:       {}'.format(round(totalgpc,0)), width = 90, bg= 'gray', anchor = 'w')
    summary_3.grid(row= 3, column= 0)
    summary_4 = Label(wGPC_timesweep_confirm_frame, text = 'Volume Needed:       {} mL'.format(round(totalvolume,1)), width = 90, bg= 'gray', anchor = 'w')
    summary_4.grid(row= 4, column= 0)

    ts_from_en.configure(state = 'readonly')
    ts_to_en.configure(state = 'readonly')
    insert_ts_btm.configure(state = 'disabled')
    delete_ts_btm.configure(state = 'disabled')
    confirm_ts_btm.configure(state = 'disabled')


    tab_control.tab(tab_wGPC_Conversion, state = 'normal')
    tab_control.select(tab_wGPC_Conversion)

    
summary_1 = Label(wGPC_timesweep_confirm_frame, text = ' ', width = 90, bg= 'gray', anchor = 'w', padx = 10)
summary_1.grid(row= 1, column= 0)
    
confirm_ts_btm = Button(wGPC_timesweep_confirm_frame, text = 'Confirm', height= 3, width = 15,  command = finalize_timesweeps, state = 'disabled', font = font_button)
confirm_ts_btm.grid(row= 1, column =2, rowspan = 3)

confirmed_ts = Label(wGPC_timesweep_parameter_frame, text = ' ', width = 22, bg ='gray')
confirmed_ts.config(font=('Ariel', 17, 'bold'), anchor ='w')
confirmed_ts.grid(row = 4, column =0)

####### Conversion Tab GPC #######
wGPC_top_frame_conv = Frame(tab_wGPC_Conversion, bg='white', width=1000, height=50, pady=3, padx = 400)
wGPC_top_frame_conv.grid(row=0, sticky="ew")

name_window_conv = Label(wGPC_top_frame_conv, text= 'Conversion',bg='white', font = font_header)
name_window_conv.grid()

def confirm_conversion_wGPC ():
    global conversion_determination
    global mol_init_monomer
    global mol_init_IS

    conversion_determination= Conversion_option_wGPC.get()

    if conversion_determination == 1:
        if isfloat(mol_monomerEntry_wGPC.get()) and isfloat(mol_internal_standardEntry_wGPC.get()):
            mol_init_monomer = float(mol_monomerEntry_wGPC.get())
            mol_init_IS = float(mol_internal_standardEntry_wGPC.get())
            Conversion_Label_wGPC.config(text = 'Ratio Internal Standard/monomer is {}'.format(float(mol_init_IS)/float(mol_init_monomer)))

            mol_internal_standardEntry_wGPC.configure(state='disabled')
            mol_monomerEntry_wGPC.configure(state = 'disabled')
            mol_monomerLabel_wGPC.configure(foreground = 'gray' )
            mol_ISlabel_wGPC.configure(foreground = 'gray' )
            confirm_conv_btm_wGPC.configure(state ='disabled')
            tab_control.tab(tab_wGPC_Initialisation, state = 'normal')
            tab_control.select(tab_wGPC_Initialisation)
            monomer_radio_wGPC.configure(state = 'disabled')
            IS_radio_wGPC.configure(state= 'disabled')
            updateGUI('Conversion will be determined via internal standard peaks (4-hydroxy benzaldehyde; ratio IS/monomer {})'.format(float(mol_init_IS)/float(mol_init_monomer)))
        else:
            Conversion_Label_wGPC.config(text = 'Entry has to be a number')
    elif conversion_determination == 2:
        mol_internal_standardEntry.configure(state='disabled')
        mol_monomerEntry.configure(state = 'disabled')
        mol_monomerLabel.configure(foreground = 'gray' )
        mol_ISlabel.configure(foreground = 'gray' )
        tab_control.tab(tab_wGPC_Initialisation, state = 'normal')
        tab_control.select(tab_wGPC_Initialisation)
        confirm_conv_btm_wGPC.configure(state ='disabled')
        monomer_radio.configure(state = 'disabled')
        IS_radio.configure(state= 'disabled')
        updateGUI('Conversion will be determined via the monomer peaks (no internal standard)')
    
    elif conversion_determination == 3:
        mol_internal_standardEntry.configure(state='disabled')
        mol_monomerEntry.configure(state = 'disabled')
        mol_monomerLabel.configure(foreground = 'gray' )
        mol_ISlabel.configure(foreground = 'gray' )
        tab_control.tab(tab_wGPC_Initialisation, state = 'normal')
        tab_control.select(tab_wGPC_Initialisation)
        confirm_conv_btm_wGPC.configure(state ='disabled')
        monomer_radio.configure(state = 'disabled')
        IS_radio.configure(state= 'disabled')
        updateGUI('Conversion will be determined via solvent (butyl acetate) + monomer peak')

    conversion_determination = Conversion_option_wGPC.get() #1 = internal standard, 2 = monomer, 3 = solvent

    

def IS_selected_wGPC():
    mol_internal_standardEntry_wGPC.configure(state = 'normal')
    mol_monomerEntry_wGPC.configure(state = 'normal')
    Conversion_Label_wGPC.config(text = 'Internal Standard')
    mol_monomerLabel_wGPC.configure(foreground = 'black' )
    mol_ISlabel_wGPC.configure(foreground = 'black' )
    

def monomer_selected_wGPC():
    Conversion_Label_wGPC.config(text = 'Conversion will be calculated with monomer peaks (only MA for now)')
    mol_internal_standardEntry_wGPC.configure(state='disabled')
    mol_monomerEntry_wGPC.configure(state = 'disabled')
    mol_monomerLabel_wGPC.configure(foreground = 'gray' )
    mol_ISlabel_wGPC.configure(foreground = 'gray' )


def solvent_selected_wGPC():
    Conversion_Label_wGPC.config(text = 'Conversion will be calculated based on the solvent+monomer peak (butyl acetate)')
    mol_internal_standardEntry_wGPC.configure(state='disabled')
    mol_monomerEntry_wGPC.configure(state = 'disabled')
    mol_monomerLabel_wGPC.configure(foreground = 'gray' )
    mol_ISlabel_wGPC.configure(foreground = 'gray' )

Conversion_option_wGPC = IntVar()

IS_radio_wGPC = Radiobutton(tab_wGPC_Conversion, text="Internal Standard", font = font_entry, variable=Conversion_option_wGPC, value=1, command = IS_selected_wGPC)
IS_radio_wGPC.grid()
mol_monomerLabel_wGPC = Label(tab_wGPC_Conversion, text = "Monomer initial (mol)")
mol_monomerLabel_wGPC.grid()
mol_monomerEntry_wGPC= Entry(tab_wGPC_Conversion)
mol_monomerEntry_wGPC.grid()
mol_ISlabel_wGPC = Label(tab_wGPC_Conversion, text = "4-hydroxy benzaldehyde initial (mol)")
mol_ISlabel_wGPC.grid()
mol_internal_standardEntry_wGPC = Entry(tab_wGPC_Conversion)
mol_internal_standardEntry_wGPC.grid()

monomer_radio_wGPC = Radiobutton(tab_wGPC_Conversion, text="Monomer", font = font_entry, variable=Conversion_option_wGPC, value=2, command = monomer_selected_wGPC)
monomer_radio_wGPC.grid()

solvent_radio_wGPC = Radiobutton(tab_wGPC_Conversion, text="Solvent (Butyl Acetate)", font = font_entry, variable=Conversion_option_wGPC, value=3, command = solvent_selected_wGPC)
solvent_radio_wGPC.grid()



Conversion_t0_frame_wGPC = Frame(tab_wGPC_Conversion)
Conversion_t0_frame_wGPC.grid()

Conversion_Label_wGPC = Label(Conversion_t0_frame_wGPC, text = 'Choose option')
Conversion_Label_wGPC.grid(row = 0, column = 1, columnspan = 3)


confirm_conv_btm_wGPC = Button(Conversion_t0_frame_wGPC, text = 'Confirm', height= 3, width = 15,  command = confirm_conversion_wGPC, font = font_button)
confirm_conv_btm_wGPC.grid(row= 1, column =2, rowspan = 3)

####### Init Tab ######
#Create Main frame of init Tab
wGPC_top_frame_init = Frame(tab_wGPC_Initialisation, bg='white', width=1000, height=50, pady=3, padx = 400)
wGPC_top_frame_init.grid(row=0, sticky="ew")
wGPC_picture_frame_init = Frame(tab_wGPC_Initialisation, bg='white', width=1000, height=300, padx=175, pady=3)
wGPC_picture_frame_init.grid(row=1, sticky="nsew")
wGPC_parameter_frame_init = Frame(tab_wGPC_Initialisation, bg='gray', width=1000, height=350, pady=3,padx = 3)
wGPC_parameter_frame_init.grid(row=3, sticky="ew")
wGPC_btm_frame_init = Frame(tab_wGPC_Initialisation, bg='gray', width=1000, height=50, pady=10, padx = 400)
wGPC_btm_frame_init.grid(row=4, sticky="ew")

#Make-Up Top Frame in init Tab
name_window_init = Label(wGPC_top_frame_init, text= 'Initialisation',bg='white', font = font_header)
name_window_init.grid()

#Make-Up picture_frame_init in Timsweep Tab
picture_init = PhotoImage(file = 'Pictures\Init_picture.png')
LabelPicture_init = Label(master = wGPC_picture_frame_init, image=picture_init, bg ='white')
LabelPicture_init.grid(row = 1, column =1)

#Make-Up Parameter_frame_timesweep in ininialisation Tab
tsparam = Label(wGPC_parameter_frame_init, text = "Start Initialisation", bg = 'gray', font=font_header_bold, padx = 150)
tsparam.grid(row = 0, column =1, columnspan=2)
#Experiment code

def check_experimentFoldertxtfile(expfolder, exp_code):
    directory_code = os.path.basename(expfolder).split('_')[-1]
    if not directory_code == exp_code:
        print('It seems that the code given by LabView ({}) does not match the real code ({}). Please give the correct Experiment Folder'.format(directory_code, exp_code))
        experimentfolder = input('>> ')
        return experimentfolder
    return expfolder

def confirmLabview():
    ExperimentFolder = Path(open(Pathlastexp_textfile, 'r').read().replace("\\", "/"))
    print('Communication folder: {}'.format(ExperimentFolder))
    ExperimentFolder = Path(check_experimentFoldertxtfile(ExperimentFolder, code))
    found = False
    while found == False:
        if ExperimentFolder.exists () == True:
            labelLabviewInfo.configure(text = 'Communication folder found')
            found = True
        else:
            labelLabviewInfo.configure(text = 'Communication folder NOT found.')
            updateGUI('Labview Folder not found')
            print('Experiment Folder not found. Please give the correct Experiment Folder.')
            ExperimentFolder = Path(input('>> '))
            labelLabviewInfo.configure(text = 'Communication folder found')
    experiment_extra.loc[0, 'Mainfolder'] = ExperimentFolder
    SearchCommunicationFolder(ExperimentFolder)
    updateGUI('LabView Check: Communication folder found, subfolder created')
    labelPss.configure(text = 'Open the PSSwin software and name the experiment ({}.txt).'.format(code))
    confirmPss.configure(state = 'normal')
    HelpPss.configure(state = 'normal')
    confirmLabview.configure(state = 'disabled')
    HelpLabview.configure(state = 'disabled')

def confirmPss():
    labelPssInfo.configure(text = 'Pss Check')
    updateGUI('Psswin is okay')
    labelSpinsolve.configure(text = 'Name the experiment ({}) in the Spinsolve software.'.format(code))
    confirmPss.configure(state = 'disabled')
    HelpPss.configure(state = 'disabled')
    confirmSpinsolve.configure(state = 'normal')
    HelpSpinsolve.configure(state = 'normal')

def confirmSpinsolve():
    labelSpinsolveInfo.configure(text = 'Spinsolve Check')
    updateGUI('Spinsolve is okay')
    confirmSpinsolve.configure(state = 'disabled')
    HelpSpinsolve.configure(state = 'disabled')
    confirmEmail.configure(state = 'normal')
    AddEmail.configure(state = 'normal')
    entryEmail.configure(state = 'normal')
    experiment_extra['Emails'] = [[]]
    labelEmailinfo.configure(text = 'Optional: Data will be send via email at the end of the experiment')

def add_emailadress():
    emailadress = entryEmail.get()
    print(emailadress)
    print(experiment_extra.at[0, 'Emails'])
    print(type(experiment_extra.at[0, 'Emails']))
    experiment_extra.loc[0, 'Emails'].append(emailadress)
    entryEmail.delete(0, 'end')
    labelEmailinfo.configure(text = 'Email adresses : {}'.format(tuple(experiment_extra.loc[0, 'Emails'])))

def confirm_emailadress():
    AddEmail.configure(state = 'disabled')
    entryEmail.configure(state = 'readonly')
    start_btn.configure(state = 'normal')
    confirmEmail.configure(state = 'disabled')

def HelpLabView():
    tab_control.tab(tab_LabView_help, state = 'normal')
    tab_control.select(tab_LabView_help)
    tab_control.tab(tab_wGPC_Setup, state = 'disabled')
    tab_control.tab(tab_wGPC_Timesweeps, state = 'disabled')
    tab_control.tab(tab_wGPC_Initialisation, state = 'disabled')

def HelpPss():
    tab_control.tab(tab_Pss_help, state = 'normal')
    tab_control.select(tab_Pss_help)
    tab_control.tab(tab_wGPC_Setup, state = 'disabled')
    tab_control.tab(tab_wGPC_Timesweeps, state = 'disabled')
    tab_control.tab(tab_wGPC_Initialisation, state = 'disabled')

def HelpSpinsolve():
    tab_control.tab(tab_Spinsolve_help, state = 'normal')
    tab_control.select(tab_Spinsolve_help)
    tab_control.tab(tab_wGPC_Setup, state = 'disabled')
    tab_control.tab(tab_wGPC_Timesweeps, state = 'disabled')
    tab_control.tab(tab_wGPC_Initialisation, state = 'disabled')


def confirm_code ():
    global code
    code = code_en.get()
    code_en.configure(state = 'readonly')
    wGPC_confirm_code.configure(state = 'disabled')

    monomer = optionVar.get() #Needs improvemt (for all the monomers)
    monomer_options.configure(state = 'disabled')

    with open(Temporary_textfile,"a") as f:
        f.write('Code,,')
        f.write(code)
        f.close()

    updateGUI('Code ({}) and timesweep parameters are communicated to LabVIEW software'.format(code))

    experiment_extra.loc[0, 'code'] = code
    monomerDF = pd.read_csv('Monomer_info.csv')

    experiment_extra.loc[0, 'Monomer'] = monomer
    experiment_extra.loc[0, 'integrals'] = monomerDF[monomerDF['Monomer'] == monomer].iloc[0,1]
    experiment_extra.loc[0, 'ConversionForumula'] = monomerDF[monomerDF['Monomer'] == monomer].iloc[0,2]

    parametersDF.to_csv('{}/ExperimentParameters.csv'.format(CommunicationMainFolder))

    labelLabview.configure(text = 'Open the LabVIEW and start running the software.')
    confirmLabview.configure(state = 'normal')
    HelpLabview.configure(state = 'normal')
    return code
    
code_lbl = Label(wGPC_parameter_frame_init, text = 'Experiment Code', bg = 'gray', width = 15, font=font_normal)
code_lbl.grid(row =3, column =0)

code_en = Entry(wGPC_parameter_frame_init, font= font_entry, width = 30)
code_en.grid(row =3, column =1)

monomer_lbl = Label(wGPC_parameter_frame_init, text = 'Monomer', bg = 'gray', font=font_normal)
monomer_lbl.grid(row =3, column =2)

optionVar = StringVar()
optionVar.set("Other")
    
listmonomers = [monomer for monomer in monomerDF['Monomer']]
monomer_options = OptionMenu(wGPC_parameter_frame_init, optionVar, *listmonomers )
monomer_options.grid(row = 3, column= 3)
#ok Button
wGPC_confirm_code = Button(wGPC_parameter_frame_init, text ='OK', font= font_button, command = confirm_code, width = 6)
wGPC_confirm_code.grid(row =4, column =1, columnspan = 2)
    
labelLabview = Label(wGPC_parameter_frame_init, text = 'LABVIEW', font= font_normal, bg= 'gray')
labelLabview.grid(row =5, column = 0, columnspan =2)
confirmLabview = Button(wGPC_parameter_frame_init, text = 'Ok', font = font_button, command = confirmLabview, state = 'disabled', width = 6)
confirmLabview.grid(row = 5, column = 3)
HelpLabview = Button(wGPC_parameter_frame_init, text = 'Help', font = font_button, state = 'disabled', command = HelpLabView, width = 6)
HelpLabview.grid(row = 5, column = 4)
labelLabviewInfo = Label(wGPC_parameter_frame_init, text = '', font = font_small, bg= 'gray')
labelLabviewInfo.grid(row = 6, column = 0, columnspan= 2)

labelPss = Label(wGPC_parameter_frame_init, text = 'PSS', font= font_normal, bg= 'gray')
labelPss.grid(row =7, column = 0, columnspan =2)
confirmPss = Button(wGPC_parameter_frame_init, text = 'Ok', font = font_button, state= 'disabled', command = confirmPss, width = 6)
confirmPss.grid(row = 7, column = 3)
HelpPss = Button(wGPC_parameter_frame_init, text = 'Help', font = font_button, state = 'disabled', command = HelpPss, width = 6)
HelpPss.grid(row = 7, column = 4)
labelPssInfo = Label(wGPC_parameter_frame_init, text = '', font = font_small, bg= 'gray')
labelPssInfo.grid(row = 8, column = 0, columnspan= 2)

labelSpinsolve = Label(wGPC_parameter_frame_init, text = 'Spinsolve', font= font_normal, bg= 'gray')
labelSpinsolve.grid(row =9, column = 0, columnspan =2)
confirmSpinsolve = Button(wGPC_parameter_frame_init, text = 'Ok', font = font_button, state = 'disabled', command = confirmSpinsolve, width = 6)
confirmSpinsolve.grid(row = 9, column = 3)
HelpSpinsolve = Button(wGPC_parameter_frame_init, text = 'Help', font = font_button, state = 'disabled', command = HelpSpinsolve, width = 6)
HelpSpinsolve.grid(row = 9, column = 4)
labelSpinsolveInfo = Label(wGPC_parameter_frame_init, text = '', font = font_small, bg= 'gray')
labelSpinsolveInfo.grid(row = 10, column = 0, columnspan= 2)

labelEmail= Label(wGPC_parameter_frame_init, text = 'Email', font= font_normal, bg= 'gray')
labelEmail.grid(row =11, column = 0, columnspan =1)
entryEmail= Entry(wGPC_parameter_frame_init, text = 'Email', font= font_entry, state = 'readonly', width = 30)
entryEmail.grid(row =11, column = 1, columnspan =1)
confirmEmail = Button(wGPC_parameter_frame_init, text = 'Confirm', font = font_button, state = 'disabled', command = confirm_emailadress, width = 6)
confirmEmail.grid(row = 11, column = 3)
AddEmail = Button(wGPC_parameter_frame_init, text = 'Add', font = font_button, state = 'disabled', command = add_emailadress, width = 6)
AddEmail.grid(row = 11, column = 4)
labelEmailinfo = Label(wGPC_parameter_frame_init, text = '', font = font_small, bg= 'gray')
labelEmailinfo.grid(row = 12, column = 0, columnspan= 2)

start_btn = Button(wGPC_btm_frame_init, text ='Start', font = font_header_bold ,state = 'disabled', command = startexp)
start_btn.grid()

#Make-up page
top_frame_exp = Frame(tab_overview, bg='white', width=1000, height=50, pady=3, padx = 400)
parameter_frame_exp = Frame(tab_overview, bg='gray', width=1000, height=350, pady=3)
top_frame_exp.grid(row=0, sticky="ew")
parameter_frame_exp.grid(row=1, sticky="ew")

#Make-Up Top Frame in exp Tab
name_window_exp = Label(top_frame_exp, text= 'Experiment',bg='white', font = font_header)
name_window_exp.grid()

#########################
#######  ONLY NMR  ######
#########################
#Create Main frame of Setup Tab
NMR_setup_top_frame = Frame(tab_NMR_Setup, bg='white', width=1000, height=50, pady=3, padx = 400)
NMR_setup_top_frame.grid(row=0, sticky = 'ew')

NMR_setup_picture_frame = Frame(tab_NMR_Setup, bg='white', width=1000, height=300, padx=175, pady=3)
NMR_setup_picture_frame.grid(row=1,sticky = 'ew')

NMR_setup_parameter_frame = Frame(tab_NMR_Setup, bg='gray', width=1000, height=350, pady=3)
NMR_setup_parameter_frame.grid(row=2,sticky = 'ew')

NMR_setup_confirm_frame = Frame(tab_NMR_Setup, bg='gray', width=1000, height=50, pady=10, padx = 400)
NMR_setup_confirm_frame.grid(row=4, sticky="ew")

#Make-Up Top Frame
name_window = Label(NMR_setup_top_frame, text= 'Setup',bg='white')
name_window.config(font=font_header)
name_window.grid()

#Make-Up Picture_frame
picure_setup = PhotoImage(file = 'Pictures/NMRsetup.png')
LabelPicture = Label(master = NMR_setup_picture_frame, image=picure_setup, bg ='white')
LabelPicture.grid()
    
#make-up Parameter frame
def NMR_change_values():
    updateGUI('Parameters Changed')
    list_parameters = parameterList2
    entries = [i[0] for i in list_parameters]
    entries_values = [i.get() for i in entries]
    print(entries_values)
    for i, value in enumerate(entries_values):
        if list(value) == []:
            pass
        else:
            if isfloat(value) == True and float(list_parameters[i][4]) != float(value):
                if float(value) == 0:
                    return updateGUI('\tNo changes, entry needs to be non-zero.')
                else:
                    parameterList2[i][4] = float(value)
            else:
                pass          
    for i, parameter in enumerate(parameterList2):
        parameter[1] = Label(NMR_setup_parameter_frame, text = parameter[4], bg = 'gray', width = 20)
        parameter[1].config(font=font_normal, anchor = 'e')
        parameter[1].grid(row = i, column =4)
    
parameterList2 = [['entry1', 'default1', 'Reactor Volume', 'mL', 0.90, 'change1'],
            ['entry2', 'default2', 'Dead Volume 1', 'mL', 0.32,'change2' ],
            ['entry5', 'default5', 'NMR Interval', 'sec', 17 ,'change5'],
            ['entry7', 'default7', 'Stabilization factor', 'x', 1.3,'change7']]
            

for i, v in enumerate(parameterList2):
    parameter = Label(NMR_setup_parameter_frame, text = v[2], bg = 'gray', width = 30)
    parameter.config(font=font_normal)
    parameter.grid(row = i, column =0)

    v[0] = Entry(NMR_setup_parameter_frame, width = 15)
    v[0].grid(row = i, column = 1)

    unit = Label(NMR_setup_parameter_frame, text = v[3], bg ='gray', width= 10)
    unit.config(font=font_normal, anchor = 'w')
    unit.grid(row = i, column = 2)

    v[5] = Button(NMR_setup_parameter_frame, text= 'Change', command = NMR_change_values)
    v[5].grid(row =i, column = 3)
     
    v[1] = Label(NMR_setup_parameter_frame, text = v[4], bg = 'gray', width = 20)
    v[1].config(font=font_normal, anchor = 'e')
    v[1].grid(row = i, column =4)

    unit2 = Label(NMR_setup_parameter_frame, text = v[3], bg ='gray')
    unit2.config(font=font_normal)
    unit2.config(font = font_normal)
    unit2.grid(row = i, column = 5)

extractChemicals()
solutionSummary = Label(NMR_setup_parameter_frame, text = 'Reaction Solution', bg = 'gray', font = font_normal, pady = 20)
solutionSummary.grid(row = i+1, column= 0, columnspan = 2, rowspan = 2 )
solution_button = Button(NMR_setup_parameter_frame, text = 'Reaction solution', command = changeSolution)
solution_button.grid(row = i+1, column= 3)

#maku-up btm-frame

def NMR_Confirm_reactor_parameters ():
    updateGUI('Reactor parameters confirmed')
    confirm_reactorParameters.configure(state = 'disabled')
    for parameterline in parameterList2:
        parameterline[5].configure(state = 'disabled')
        parameterline[0].configure(state = 'readonly')
    tab_control.tab(tab_NMR_Timesweeps, state = 'normal')
    tab_control.select(tab_NMR_Timesweeps)
    confirm_reactorParameters.configure(state = 'disabled')
    
confirm_reactorParameters = Button(NMR_setup_confirm_frame, text = 'Confirm', command = NMR_Confirm_reactor_parameters, height= 3, width = 15, font = font_button)
confirm_reactorParameters.grid()


####TIMESWEEP TAB####
#Create Main frame of Timesweep Tab
NMR_timesweep_top_frame = Frame(tab_NMR_Timesweeps, bg='white', width=1000, height=50, pady=3, padx = 400)
NMR_timesweep_top_frame.grid(row=0, sticky="ew")
NMR_timesweep_picture_frame = Frame(tab_NMR_Timesweeps, bg='white', width=1000, height=300, padx=175, pady=3)
NMR_timesweep_picture_frame.grid(row=1, sticky="nsew")
NMR_timesweep_parameter_frame = Frame(tab_NMR_Timesweeps, bg='gray', width=1000, height=350, pady=3,padx = 3)
NMR_timesweep_parameter_frame.grid(row=3, sticky="ew")
NMR_timesweep_confirm_frame = Frame(tab_NMR_Timesweeps, bg='gray', width=1000, height=50, pady=10, padx = 10)
NMR_timesweep_confirm_frame.grid(row=4, sticky="ew")

#Make-Up Top Frame in Timesweep Tab
NMR_timesweep_header = Label(NMR_timesweep_top_frame, text= 'Timesweeps',bg='white')
NMR_timesweep_header.config(font=font_header)
NMR_timesweep_header.grid()

#Make-Up wGPC_timesweep_picture_frame in Timsweep Tab
NMR_picture_timesweep = PhotoImage(file = 'Pictures\Timesweeps_pictureFrame.png')
LabelPicture = Label(master = NMR_timesweep_picture_frame, image=NMR_picture_timesweep, bg ='white')
LabelPicture.grid()

#Make-Up Parameter_frame_timesweep in Timesweep Tab
NMR_all_ts_info = [] #list where all the timesweeps will be saved

def NMR_insert_timesweep():
    updateGUI('Timesweep added to experiment')

    #delete whitespaces in entry
    NMR_ts_from_en1 = (NMR_ts_from_en.get()).replace(' ', '')
    NMR_ts_to_en1 = (NMR_ts_to_en.get()).replace(' ', '')

    #checks if entry is number
    if isfloat(NMR_ts_from_en.get()) == True and isfloat(NMR_ts_to_en.get()):
        if float(NMR_ts_from_en1) != float(NMR_ts_to_en1) and float(NMR_ts_to_en1) != 0 and float(NMR_ts_from_en1) !=0:

            number_of_added_timesweep2 = len(wGPC_all_ts_info) +1

            number_of_added_timesweep2 = len(NMR_all_ts_info) +1

            reactorvol, NMRinterval = parameterList2[0][4], parameterList2[2][4]
            from_ , to_ = float(NMR_ts_from_en.get()), float(NMR_ts_to_en.get())
            NMR_fr1, NMR_fr2 = float(reactorvol)/float(from_),float(reactorvol)/float(to_)

            NMR_timesweep_info = ['label_{}'.format(number_of_added_timesweep2), 'Timesweep {}: From {} minutes ({} mL/min) to {} minutes ({} mL/min) (NMR interval: {}sec)'.format(number_of_added_timesweep2, from_, round(NMR_fr1, 3), to_, round(NMR_fr2, 3), NMRinterval), from_, to_]
            updateGUI('\tAdded timesweep: {}'.format(NMR_timesweep_info[1]))
            NMR_all_ts_info.append(NMR_timesweep_info)

            for i, ts_info in enumerate(NMR_all_ts_info):
                ts_info[0] = Label(NMR_timesweep_parameter_frame, text = ts_info[1], bg = 'gray', width = 90, font = font_small, anchor = 'w')
                ts_info[0].grid(row = 5+i, columnspan = 6)

            NMR_entryText = DoubleVar()
            NMR_entryText.set(NMR_all_ts_info[-1][-1])
            NMR_ts_from_en.configure(textvariable=NMR_entryText, state= 'readonly')
            NMR_confirm_ts_btm.config(state = 'normal')
            NMR_delete_ts_btm.config(state = 'normal')  
        else:
            updateGUI('\tError: No change, entries cannot be the same')
    else:
        pass

def NMR_delete_timesweep():
    print(len(NMR_all_ts_info) != 0)
    if len(NMR_all_ts_info) != 0:
        updateGUI('Last timesweep deleted')
        updateGUI('\tDeleted timesweep: {}'.format(NMR_all_ts_info[-1][1]))
        NMR_all_ts_info[-1][0].destroy()
        NMR_all_ts_info.pop(-1)
    else:
        pass

    if len(NMR_all_ts_info) == 0:
        NMR_confirm_ts_btm.config(state = 'disabled')
        NMR_delete_ts_btm.config(state = 'disabled')
        NMR_entryText = DoubleVar()
        NMR_ts_from_en.configure(textvariable=NMR_entryText, state= 'normal')
    else:
        NMR_confirm_ts_btm.config(state = 'normal')
        NMR_delete_ts_btm.config(state = 'normal')
        NMR_entryText = DoubleVar()
        NMR_entryText.set(NMR_all_ts_info[-1][-1])
        NMR_ts_from_en.configure(textvariable=NMR_entryText, state= 'readonly')
        pass


NMR_timesweep_parameter_header = Label(NMR_timesweep_parameter_frame, text = "Insert Timesweep Parameters", bg = 'gray', width = 27, font = font_header_bold)
    
NMR_ts_from_lbl = Label(NMR_timesweep_parameter_frame, text = 'From (minutes)', width= 15, bg ='gray', font = font_normal, anchor = 'center')
NMR_ts_from_en = Entry(NMR_timesweep_parameter_frame, width = 5, font= font_entry)

NMR_ts_to_lbl = Label(NMR_timesweep_parameter_frame, text = 'To (minutes)', bg = 'gray', font = font_normal, anchor = 'center')
NMR_ts_to_en = Entry(NMR_timesweep_parameter_frame, width = 5, font=font_entry)

NMR_insert_ts_btm = Button(NMR_timesweep_parameter_frame, text = 'Add', command = NMR_insert_timesweep,font=font_button)
NMR_delete_ts_btm = Button(NMR_timesweep_parameter_frame, text = 'Delete', command = NMR_delete_timesweep, font=font_button, state = 'disabled')

NMR_confirmed_ts = Label(NMR_timesweep_parameter_frame, text = 'List of Timesweeps', bg ='gray', font= font_header_bold, anchor = 'w')

NMR_ts_from_lbl.grid(row = 1, column = 1, columnspan = 2)
NMR_ts_from_en.grid(row = 2, column = 1)
NMR_ts_to_lbl.grid(row = 1, column = 4, columnspan =2)
NMR_ts_to_en.grid(row = 2, column = 4) 
NMR_insert_ts_btm.grid(row = 3, column = 2)
NMR_delete_ts_btm.grid(row = 3, column = 3)
NMR_confirmed_ts.grid(row = 4, column =0)
NMR_timesweep_parameter_header.grid(row = 0, column =1, columnspan = 4)

def NMR_finalize_timesweeps ():
    reactorvol2 = parameterList2[0][4]  
    #f= open("//ad.monash.edu/home/User085/jvan0036/Documents/PhD/Joren/experiment.txt","a")
    for i, timesweep in enumerate(NMR_all_ts_info):
        NMR_fr1, NMR_fr2 = reactorvol2/timesweep[2], reactorvol2/timesweep[3]
        #Create DF with all the parameters
        parametersDF.loc[i, 'Start']= timesweep[2]
        parametersDF.loc[i, 'Stop']= timesweep[3]
        parametersDF.loc[i, 'volume'] = parameterList2[0][4]
        parametersDF.loc[i, 'StartFR'] = NMR_fr1
        parametersDF.loc[i, 'StopFR'] = NMR_fr2
        parametersDF.loc[i, 'dead volume 1'] = parameterList2[1][4]
        parametersDF.loc[i, 'NMR interval'] = parameterList2[2][4]
        parametersDF.loc[i, 'stabilisation time'] = parameterList2[3][4]
        parametersDF.loc[i, 'DeadVolume1(min)'] = parametersDF.loc[i, 'dead volume 1']/parametersDF.loc[i,'StopFR']
        parametersDF.loc[i, 'mode'] = 'NMR'
        parametersDF.loc[i, 'Dead Volume 2'] = 'N.A'
        parametersDF.loc[i, 'Dead Volume 3'] = 'N.A'
        parametersDF.loc[i, 'GPC Interval'] = 'N.A'
        parametersDF.loc[i, 'Dilution FR'] = 'N.A'
        parametersDF.loc[i, 'DeadVolume2(min)'] = 'N.A'
        parametersDF.loc[i, 'DeadVolume3(min)'] = 'N.A'          

    updateGUI('Confirmed timesweep Experiment:\n{}'.format(parametersDF))
    scannumbers = calculateScans.CalculateScans(parametersDF)
    totalscan = scannumbers['Stop Scan NMR'].iloc[-1]
    total_time = (totalscan * parametersDF.loc[0,'NMR interval']) /60
        
    entry1 = parametersDF.iloc[0] #just the first timesweep entry to extract values
    stabili = ((entry1['volume']*entry1['stabilisation time']))
    allDvs = (entry1['dead volume 1']* int(scannumbers.shape[0]))
    ts_number= int(scannumbers.shape[0])
    totalvolume = stabili +(ts_number* allDvs)

    summary_totalTime = Label(NMR_timesweep_confirm_frame, text = 'Total time:             {}min'.format(round(total_time,1)), width = 90, bg= 'gray', anchor = 'w',padx = 10)
    summary_totalTime.grid(row= 1, column= 0)
    summary_totalScans = Label(NMR_timesweep_confirm_frame, text = 'Total NMR scans:         {}'.format(round(totalscan,0)), width = 90, bg= 'gray', anchor = 'w')
    summary_totalScans.grid(row= 2, column= 0)
    summary_totalVolume = Label(NMR_timesweep_confirm_frame, text = 'Volume Needed:       {} mL'.format(round(totalvolume,1)), width = 90, bg= 'gray', anchor = 'w')
    summary_totalVolume.grid(row= 3, column= 0)

    NMR_ts_from_en.configure(state = 'readonly')
    NMR_ts_to_en.configure(state = 'readonly')
    NMR_insert_ts_btm.configure(state = 'disabled')
    NMR_delete_ts_btm.configure(state = 'disabled')
    NMR_confirm_ts_btm.configure(state = 'disabled')

    tab_control.tab(tab_NMR_Conversion, state = 'normal')
    tab_control.select(tab_NMR_Conversion)

    
    if not SolutionDataframe.empty:
        solvent_initmol_entryText = DoubleVar()
        solvent_initmol_entryText.set(float(SolutionDataframe.iloc[3]['moles (mol)']))
        mol_solventEntry_solvent.configure(textvariable = solvent_initmol_entryText)

        monomer_initmol_entryText = DoubleVar()
        monomer_initmol_entryText.set(float(SolutionDataframe.iloc[1]['moles (mol)']))
        mol_monomerEntry_solvent.configure(textvariable = monomer_initmol_entryText)
    
    
    
summary_spacing = Label(NMR_timesweep_confirm_frame, text = ' ', width = 90, bg= 'gray', anchor = 'w', padx = 10)
summary_spacing.grid(row= 1, column= 0)
    
NMR_confirm_ts_btm = Button(NMR_timesweep_confirm_frame, text = 'Confirm', height= 3, width = 15,  command = NMR_finalize_timesweeps, state = 'disabled', font = font_button)
NMR_confirm_ts_btm.grid(row= 1, column =2, rowspan = 3)

NMR_confirmed_ts_spacing = Label(NMR_timesweep_confirm_frame, text = ' ', width = 22, bg ='gray', font = font_normal, anchor = 'w')
NMR_confirmed_ts_spacing.grid(row = 4, column =0)

####### Conversion Tab #######
NMR_top_frame_conv = Frame(tab_NMR_Conversion, bg='white', width=1000, height=50, pady=3, padx = 400)
NMR_top_frame_conv.grid(row=0, sticky="ew")

name_window_conv = Label(NMR_top_frame_conv, text= 'Conversion',bg='white', font = font_header)
name_window_conv.grid()

def confirm_conversion ():
    global conversion_determination
    global mol_init_monomer
    global mol_init_IS

    conversion_determination= v.get()


    if conversion_determination == 1:
        if isfloat(mol_monomerEntry.get()) and isfloat(mol_internal_standardEntry.get()):
            print(mol_monomerEntry.get(), type(mol_monomerEntry.get()))
            mol_init_monomer = float(mol_monomerEntry.get())
            mol_init_IS = float(mol_internal_standardEntry.get())
            Conversion_Label.config(text = 'Ratio Internal Standard/monomer is {}'.format(float(mol_init_IS)/float(mol_init_monomer)))

            mol_internal_standardEntry.configure(state='disabled')
            mol_monomerEntry.configure(state = 'disabled')
            mol_monomerLabel.configure(foreground = 'gray' )
            mol_ISlabel.configure(foreground = 'gray' )
            NMR_confirm_conv_btm.configure(state ='disabled')
            tab_control.tab(tab_NMR_Initialisation, state = 'normal')
            tab_control.select(tab_NMR_Initialisation)
            monomer_radio.configure(state = 'disabled')
            IS_radio.configure(state= 'disabled')
            updateGUI('Conversion will be determined via internal standard peaks (4-hydroxy benzaldehyde; ratio IS/monomer {})'.format(float(mol_init_IS)/float(mol_init_monomer)))
        else:
            Conversion_Label.config(text = 'Entry has to be a number')

    elif conversion_determination == 2:
        mol_internal_standardEntry.configure(state='disabled')
        mol_monomerEntry.configure(state = 'disabled')
        mol_monomerLabel.configure(foreground = 'gray' )
        mol_ISlabel.configure(foreground = 'gray' )
        tab_control.tab(tab_NMR_Initialisation, state = 'normal')
        tab_control.select(tab_NMR_Initialisation)
        NMR_confirm_conv_btm.configure(state ='disabled')
        monomer_radio.configure(state = 'disabled')
        IS_radio.configure(state= 'disabled')
        updateGUI('Conversion will be determined via the monomer peaks (no internal standard)')
 #Here
    elif conversion_determination == 3:
        if isfloat(mol_monomerEntry_solvent.get()) and isfloat(mol_solventEntry_solvent.get()):
            mol_init_monomer_solvent = float(mol_monomerEntry_solvent.get())
            mol_init_solvent = float(mol_solventEntry_solvent.get())
            print(mol_init_monomer_solvent, type(mol_init_monomer_solvent))
            Conversion_Label.config(text = 'Ratio monomer/solvent is {}'.format(float(mol_init_monomer_solvent)/float(mol_init_solvent)))

            mol_internal_standardEntry.configure(state='disabled')
            mol_monomerEntry.configure(state = 'disabled')
            mol_monomerLabel.configure(foreground = 'gray' )
            mol_ISlabel.configure(foreground = 'gray' )
            tab_control.tab(tab_NMR_Initialisation, state = 'normal')
            tab_control.select(tab_NMR_Initialisation)
            NMR_confirm_conv_btm.configure(state ='disabled')
            monomer_radio.configure(state = 'disabled')
            IS_radio.configure(state= 'disabled')

            solvent_radio.configure(state = 'disabled')
            mol_monomerEntry_solvent.configure(state = 'readonly')
            mol_solventEntry_solvent.configure(state = 'readonly')
            updateGUI('Conversion will be determined based on the butyl acetate solvent peak')
        else:
            Conversion_Label.config(text = 'Entry has to be a number')

    conversion_determination = v.get() #1 = internal standard, 2 = monomer, 3 = solvent


    

def IS_selected():
    mol_internal_standardEntry.configure(state = 'normal')
    mol_monomerEntry.configure(state = 'normal')
    Conversion_Label.config(text = 'Internal Standard')
    mol_monomerLabel.configure(foreground = 'black' )
    mol_ISlabel.configure(foreground = 'black' )
    mol_solventlabel_solvent.configure(foreground='gray')
    mol_monomerLabel_solvent.configure(foreground= 'gray')
    mol_solventEntry_solvent.configure(state = 'disabled')
    mol_monomerEntry_solvent.configure(state = 'disabled')
    
def monomer_selected():
    Conversion_Label.config(text = 'Conversion will be calculated with monomer peaks (only MA for now)')
    mol_internal_standardEntry.configure(state='disabled')
    mol_monomerEntry.configure(state = 'disabled')
    mol_monomerLabel.configure(foreground = 'gray' )
    mol_ISlabel.configure(foreground = 'gray' )
    mol_solventlabel_solvent.configure(foreground='gray')
    mol_monomerLabel_solvent.configure(foreground= 'gray')
    mol_solventEntry_solvent.configure(state = 'disabled')
    mol_monomerEntry_solvent.configure(state = 'disabled')


def solvent_selected():
    Conversion_Label.config(text = 'Conversion will be calculated based on solvent')
    mol_internal_standardEntry.configure(state='disabled')
    mol_monomerEntry.configure(state = 'disabled')
    mol_monomerLabel.configure(foreground = 'gray' )
    mol_ISlabel.configure(foreground = 'gray' )
    mol_solventlabel_solvent.configure(foreground='black')
    mol_monomerLabel_solvent.configure(foreground= 'black')
    mol_solventEntry_solvent.configure(state = 'normal')
    mol_monomerEntry_solvent.configure(state = 'normal')
    


v = IntVar()

IS_radio = Radiobutton(tab_NMR_Conversion, text="Internal Standard", font = font_entry, variable=v, value=1, command = IS_selected)
IS_radio.grid()
mol_monomerLabel = Label(tab_NMR_Conversion, text = "Monomer initial (mol)")
mol_monomerLabel.grid()
mol_monomerEntry= Entry(tab_NMR_Conversion)
mol_monomerEntry.grid()
mol_ISlabel = Label(tab_NMR_Conversion, text = "4-hydroxy benzaldehyde initial (mol)")
mol_ISlabel.grid()
mol_internal_standardEntry = Entry(tab_NMR_Conversion)
mol_internal_standardEntry.grid()

monomer_radio = Radiobutton(tab_NMR_Conversion, text="Monomer", font = font_entry, variable=v, value=2, command = monomer_selected)
monomer_radio.grid()

solvent_radio = Radiobutton(tab_NMR_Conversion, text="Solvent (Butyl Acetate)", font = font_entry, variable=v, value=3, command = solvent_selected)
solvent_radio.grid()
mol_monomerLabel_solvent = Label(tab_NMR_Conversion, text = "Monomer initial (mol)")
mol_monomerLabel_solvent.grid()
mol_monomerEntry_solvent= Entry(tab_NMR_Conversion)
mol_monomerEntry_solvent.grid()
mol_solventlabel_solvent = Label(tab_NMR_Conversion, text = "Butyl acetate initial (mol)")
mol_solventlabel_solvent.grid()
mol_solventEntry_solvent = Entry(tab_NMR_Conversion)
mol_solventEntry_solvent.grid()

Conversion_t0_frame = Frame(tab_NMR_Conversion)
Conversion_t0_frame.grid()

Conversion_Label = Label(Conversion_t0_frame, text = 'Choose option')
Conversion_Label.grid(row = 0, column = 1, columnspan = 3)

v.set(1)
IS_selected()

NMR_confirm_conv_btm = Button(Conversion_t0_frame, text = 'Confirm', height= 3, width = 15,  command = confirm_conversion, font = font_button)
NMR_confirm_conv_btm.grid(row= 1, column =2, rowspan = 3)

####### Init Tab ######
#Create Main frame of init Tab
NMR_top_frame_init = Frame(tab_NMR_Initialisation, bg='white', width=1000, height=50, pady=3, padx = 400)
NMR_top_frame_init.grid(row=0, sticky="ew")
NMR_picture_frame_init = Frame(tab_NMR_Initialisation, bg='white', width=1000, height=300, padx=175, pady=3)
NMR_picture_frame_init.grid(row=1, sticky="nsew")
NMR_parameter_frame_init = Frame(tab_NMR_Initialisation, bg='gray', width=1000, height=350, pady=3,padx = 3)
NMR_parameter_frame_init.grid(row=3, sticky="ew")
NMR_btm_frame_init = Frame(tab_NMR_Initialisation, bg='gray', width=1000, height=50, pady=10, padx = 400)
NMR_btm_frame_init.grid(row=4, sticky="ew")

#Make-Up Top Frame in init Tab
name_window_init = Label(NMR_top_frame_init, text= 'Initialisation',bg='white', font = font_header)
name_window_init.grid()

#Make-Up picture_frame_init in Timsweep Tab
picture_init2 = PhotoImage(file = 'Pictures/NMR_init_picture.png')
LabelPicture_init2 = Label(master = NMR_picture_frame_init, image=picture_init2, bg ='white')
LabelPicture_init2.grid(row = 1, column =1)

#Make-Up Parameter_frame_timesweep in ininialisation Tab
NMR_ini_paramterF_header = Label(NMR_parameter_frame_init, text = "Start Initialisation", bg = 'gray', font=font_header_bold, padx = 150)
NMR_ini_paramterF_header.grid(row = 0, column =1, columnspan=2)
#Experiment code
def confirmLabview_NMR():
    ExperimentFolder2 = Path(open(Pathlastexp_textfile, 'r').read().replace("\\", "/"))
    ExperimentFolder2 = Path(check_experimentFoldertxtfile(ExperimentFolder2, code2))
    found = False
    while found == False:
        if ExperimentFolder2.exists () == True:
            labelLabviewInfo2.configure(text = 'Communication folder found')
            found = True
        else:
            labelLabviewInfo2.configure(text = 'Communication folder NOT found.')
            updateGUI('Labview Folder not found')
            print('Experiment Folder not found. Please give the correct Experiment Folder.')
            ExperimentFolder2 = Path(input('>> '))
            labelLabviewInfo2.configure(text = 'Communication folder found')

    labelLabviewInfo2.configure(text = 'Communication folder found')
    SearchCommunicationFolder(ExperimentFolder2)
    experiment_extra.loc[0, 'Mainfolder'] = ExperimentFolder2
    updateGUI('LabView Check: Communication folder found, subfolder created in {}.'.format(ExperimentFolder2))
    labelSpinsolve2.configure(text = 'Name the experiment ({}) in the Spinsolve software.'.format(code2))
    confirmSpinsolve2.configure(state = 'normal')
    HelpSpinsolve2.configure(state = 'normal')
    confirmLabview2.configure(state = 'disabled')
    HelpLabview2.configure(state = 'disabled')

def confirmSpinsolve_NMR():
    labelSpinsolveInfo2.configure(text = 'Spinsolve Check')
    updateGUI('Spinsolve is okay')
    confirmSpinsolve2.configure(state = 'disabled')
    HelpSpinsolve2.configure(state = 'disabled')
    confirmEmail2.configure(state = 'normal')
    AddEmail2.configure(state = 'normal')
    entryEmail2.configure(state = 'normal')
    experiment_extra['Emails'] = [[]]
    
def add_emailadress2():
    emailadress = entryEmail2.get()
    
    experiment_extra.loc[0, 'Emails'].append(emailadress)
    entryEmail2.delete(0, 'end')
    labelEmail2info.configure(text = 'Email adresses : {}'.format(experiment_extra.loc[0, 'Emails']))

def confirm_emailadress2():
    AddEmail2.configure(state = 'disabled')
    entryEmail2.configure(state = 'readonly')
    start_btn2.configure(state = 'normal')
    confirmEmail2.configure(state = 'disabled')


def close(window):
    window.destroy()

def HelpLabView_NMR():
    tab_control.tab(tab_LabView_help, state = 'normal')
    tab_control.select(tab_LabView_help)
    tab_control.tab(tab_NMR_Setup, state = 'disabled')
    tab_control.tab(tab_NMR_Timesweeps, state = 'disabled')
    tab_control.tab(tab_NMR_Initialisation, state = 'disabled')

def HelpSpinsolve_NMR():
    tab_control.tab(tab_Spinsolve_help, state = 'normal')
    tab_control.select(tab_Spinsolve_help)
    tab_control.tab(tab_NMR_Setup, state = 'disabled')
    tab_control.tab(tab_NMR_Timesweeps, state = 'disabled')
    tab_control.tab(tab_NMR_Initialisation, state = 'disabled')

def confirm_code_NMR ():
    global code2
    code2 = code_en2.get()
    code_en2.configure(state = 'readonly')
    NMR_confirm_code.configure(state = 'disabled')

    monomer2 = optionVar.get() #Needs improvemt (for all the monomers)
    monomer_options2.configure(state = 'disabled')

    with open(Temporary_textfile,"a") as f:
        f.write('Code,,')
        f.write(code2)
        f.close()

    updateGUI('Code ({}) and timesweep parameters are communicated to LabVIEW software'.format(code2))

    experiment_extra.loc[0, 'code'] = code2
    monomerDF = pd.read_csv('Monomer_info.csv')

    experiment_extra.loc[0, 'Monomer'] = monomer2
    experiment_extra.loc[0, 'integrals'] = monomerDF[monomerDF['Monomer'] == monomer2].iloc[0,1]
    experiment_extra.loc[0, 'ConversionForumula'] = monomerDF[monomerDF['Monomer'] == monomer2].iloc[0,2]

    parametersDF.to_csv('{}/ExperimentParameters.csv'.format(CommunicationMainFolder))

    labelLabview2.configure(text = 'Open the LabVIEW and start running the software.')
    confirmLabview2.configure(state = 'normal')
    HelpLabview2.configure(state = 'normal')
    return code2
    
code_lbl2 = Label(NMR_parameter_frame_init, text = 'Experiment Code', bg = 'gray', width = 15, font=font_normal)
code_lbl2.grid(row =3, column =0)

code_en2 = Entry(NMR_parameter_frame_init, font= font_entry, width = 30)
code_en2.grid(row =3, column =1)

monomer_lbl2 = Label(NMR_parameter_frame_init, text = 'Monomer', bg = 'gray', font=font_normal)
monomer_lbl2.grid(row =3, column =2)

optionVar2 = StringVar()
optionVar2.set("Other")
    
listmonomers = [monomer for monomer in monomerDF['Monomer']]
monomer_options2 = OptionMenu(NMR_parameter_frame_init, optionVar2, *listmonomers )
monomer_options2.grid(row = 3, column= 3)
#ok Button
NMR_confirm_code = Button(NMR_parameter_frame_init, text ='OK', font= font_button, command = confirm_code_NMR, width=6)
NMR_confirm_code.grid(row =4, column =1, columnspan = 2)
    
labelLabview2 = Label(NMR_parameter_frame_init, text = 'LABVIEW', font= font_normal, bg= 'gray')
labelLabview2.grid(row =5, column = 0, columnspan =2)
confirmLabview2 = Button(NMR_parameter_frame_init, text = 'Ok', font = font_button, command = confirmLabview_NMR, state = 'disabled', width=6)
confirmLabview2.grid(row = 5, column = 3)
HelpLabview2 = Button(NMR_parameter_frame_init, text = 'Help', font = font_button, state = 'disabled', command = HelpLabView_NMR, width=6)
HelpLabview2.grid(row = 5, column = 4)
labelLabviewInfo2 = Label(NMR_parameter_frame_init, text = '', font = font_small, bg= 'gray')
labelLabviewInfo2.grid(row = 6, column = 0, columnspan= 2)

labelSpinsolve2= Label(NMR_parameter_frame_init, text = 'Spinsolve', font= font_normal, bg= 'gray')
labelSpinsolve2.grid(row =9, column = 0, columnspan =2)
confirmSpinsolve2 = Button(NMR_parameter_frame_init, text = 'Ok', font = font_button, state = 'disabled', command = confirmSpinsolve_NMR, width=6)
confirmSpinsolve2.grid(row = 9, column = 3)
HelpSpinsolve2 = Button(NMR_parameter_frame_init, text = 'Help', font = font_button, state = 'disabled', command = HelpSpinsolve_NMR, width=6)
HelpSpinsolve2.grid(row = 9, column = 4)
labelSpinsolveInfo2 = Label(NMR_parameter_frame_init, text = '', font = font_small, bg= 'gray')
labelSpinsolveInfo2.grid(row = 10, column = 0, columnspan= 2)


labelEmail2= Label(NMR_parameter_frame_init, text = 'Email', font= font_normal, bg= 'gray')
labelEmail2.grid(row =11, column = 0, columnspan =1)
entryEmail2= Entry(NMR_parameter_frame_init, text = 'Email', font= font_normal, state = 'readonly', width = 30)
entryEmail2.grid(row =11, column = 1, columnspan =1)
confirmEmail2 = Button(NMR_parameter_frame_init, text = 'Confirm', font = font_button, state = 'disabled', command = confirm_emailadress2, width=6)
confirmEmail2.grid(row = 11, column = 3)
AddEmail2 = Button(NMR_parameter_frame_init, text = 'Add', font = font_button, state = 'disabled', command = add_emailadress2, width=6)
AddEmail2.grid(row = 11, column = 4)
labelEmail2info = Label(NMR_parameter_frame_init, text = '', font = font_small, bg= 'gray')
labelEmail2info.grid(row = 12, column = 0, columnspan= 2)

start_btn2 = Button(NMR_btm_frame_init, text = 'Start', command = startexp, height= 3, width = 15, font = font_button, state = 'disabled')
start_btn2.grid()

tab_control.grid()

root.mainloop()
print('next')