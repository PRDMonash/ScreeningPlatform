from msilib.schema import Font
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
from log_method import setup_logger
from defining_folder import defining_communication_folder, defining_PsswinFolder, defining_NMRFolder
from helpers import isfloat

logger = setup_logger('App')

DRIVE = 'S'
Temporary_textfile, Pathlastexp_textfile, CommunicationMainFolder = defining_communication_folder(os.path.join(os.path.dirname(os.getcwd()),'CommunicationFolder'))
PsswinFolder = defining_PsswinFolder('{}:/Sci-Chem/PRD/GPC 112/2018-March/Projects'.format(DRIVE))
NMRFolder = defining_NMRFolder('C:/PROJECTS/DATA')

FONT_NORMAL = ('Ariel', 15)
FONT_HEADER = ('Courier',30)
FONT_BOTTON = ('Ariel', 10)
FONT_HEADER_BOLD = ('Ariel', 18, 'bold')
FONT_ENTRY = ('Ariel', 17)
FONT_SMALL = ('Ariel', 10)
FONT_SMALL_BOLD = ('Ariel', 10, 'bold')

Labviewscript = 'GPC-NMR Timesweep_GUIversion_version4_lab112_gpcPC.vi'

spinsolveImage = 'Spinsolve.png'      
##### APP ####
root = Tk()
logger.info('Software Openend')
root.title('NMR Platform')
root.geometry('{}x{}'.format(1000, 750))
root.resizable(False, False)
root.wm_iconbitmap('Pictures\Benchtop NMR.ico')

# create tabs
tab_control = ttk.Notebook(root)

tab_welcome = ttk.Frame(tab_control) # Adds Welcome tab
tab_control.add(tab_welcome, text='Welcome')

tab_overview = ttk.Frame(tab_control) # Adds Overview tab (displays log)
tab_control.add(tab_overview, text='Experiment', state ='hidden')

def NMR():
    ''' Enables the tabs for NMR mode'''

    tab_control.tab(tab_NMRGPC_Setup, state = 'hidden')
    tab_control.tab(tab_NMRGPC_Timesweeps, state = 'hidden')
    tab_control.tab(tab_NMRGPC_Conversion, state = 'hidden')
    tab_control.tab(tab_NMRGPC_Initialisation, state = 'hidden')
    
    tab_control.tab(tab_NMR_Setup, state = 'normal')
    tab_control.tab(tab_NMR_Timesweeps, state = 'disabled')
    tab_control.tab(tab_NMR_Initialisation, state = 'disabled')
    tab_control.tab(tab_NMR_Conversion, state = 'disabled')
    tab_control.insert(1, tab_overview, state = 'normal')
    optionNMR_btm.configure(state= 'disabled')
    optionNMRGPC_btm.configure(state= 'disabled')
    tab_control.select(tab_NMR_Setup)
    #updateGUI('Mode: NMR')
    logger.info('Selected mode: NMR')

def NMRGPC():
    ''' Enables the tabs for NMR and GPC mode'''

    tab_control.tab(tab_NMRGPC_Setup, state = 'normal')
    tab_control.tab(tab_NMRGPC_Timesweeps, state = 'disabled')
    tab_control.tab(tab_NMRGPC_Initialisation, state = 'disabled')
    tab_control.tab(tab_NMRGPC_Conversion, state = 'disabled')
    tab_control.insert(1, tab_overview, state = 'normal')
    tab_control.select(tab_NMRGPC_Setup)
    optionNMR_btn.configure(state= 'disabled')
    optionNMRGPC_btn.configure(state= 'disabled')
    #updateGUI('Mode: NMR and GPC')
    logger.info('Selected mode: NMR and GPC')
   
# NMR-GPC tabs
tab_NMRGPC_Setup = ttk.Frame(tab_control)
tab_NMRGPC_Timesweeps = ttk.Frame(tab_control)
tab_NMRGPC_Conversion = ttk.Frame(tab_control)
tab_NMRGPC_Initialisation = ttk.Frame(tab_control)

tab_control.add(tab_NMRGPC_Setup, text = 'Setup', state = 'disabled')
tab_control.add(tab_NMRGPC_Timesweeps, text='Timesweeps', state = 'disabled')
tab_control.add(tab_NMRGPC_Conversion, text='Conversion', state = 'hidden')
tab_control.add(tab_NMRGPC_Initialisation, text='Initialisation', state = 'disabled')

# Only NMR tabs
tab_NMR_Setup = ttk.Frame(tab_control)
tab_NMR_Timesweeps = ttk.Frame(tab_control)
tab_NMR_Conversion = ttk.Frame(tab_control)
tab_NMR_Initialisation = ttk.Frame(tab_control)


tab_control.add(tab_NMR_Setup, text = 'Setup', state = 'hidden')
tab_control.add(tab_NMR_Timesweeps, text='Timesweeps', state = 'hidden')
tab_control.add(tab_NMR_Conversion, text='Conversion', state = 'hidden')
tab_control.add(tab_NMR_Initialisation, text='Initialisation', state = 'hidden')

# Helpers tabs
tab_LabView_help = ttk.Frame(tab_control)
tab_control.add(tab_LabView_help, text = 'LabView Help', state = 'hidden')
tab_Pss_help = ttk.Frame(tab_control)
tab_control.add(tab_Pss_help, text = 'Pss Help', state = 'hidden')
tab_Spinsolve_help = ttk.Frame(tab_control)
tab_control.add(tab_Spinsolve_help, text = 'Spinsolve Help', state = 'hidden')

# Welcome tab
Welcome_top_frame = Frame(tab_welcome, bg='white', pady=30, padx = 400)
Welcome_top_frame.grid(sticky = 'ne')
header_Welcome = Label(Welcome_top_frame, text= 'Welcome',bg='white', font = FONT_HEADER)
header_Welcome.grid()

Welcome_Option_frame = Frame(tab_welcome)
Welcome_Option_frame.grid()
Welcom_option_frame_header = Label(Welcome_Option_frame, text = 'Choose a mode of operation', font = FONT_HEADER_BOLD)
Welcom_option_frame_header.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)
optionNMR_btn = Button(Welcome_Option_frame, text = "NMR", command = NMR,width = 20, height = 3, font = FONT_HEADER_BOLD)
optionNMR_btn.grid(row = 1, column = 0, padx = 10, pady=10)
optionNMRGPC_btn = Button(Welcome_Option_frame, text = "NMR-GPC", command = NMRGPC, width = 20, height = 3, font = FONT_HEADER_BOLD)
optionNMRGPC_btn.grid(row =1, column = 1, padx = 10, pady = 10)

    # Communication folder entry
def update_comfolder():
    global comfolder_path
    filename = filedialog.askdirectory()
    comfolder_path.set(filename)
    defining_communication_folder(filename, update = True)

comfolder_label = Label(Welcome_Option_frame,text="Communication Folder", font = FONT_ENTRY)
comfolder_label.grid(row = 2, column = 0, columnspan = 2, padx = 10, pady = 10)
comfolder_path = StringVar(value =CommunicationMainFolder)
comfolder = Label(Welcome_Option_frame,textvariable=comfolder_path)
comfolder.grid(row=3, column=0, columnspan = 2)
comfolder_btn = Button(Welcome_Option_frame, text="Browse", command=update_comfolder)
comfolder_btn.grid(row=3, column=2)
 
    # NMR folder entry
def update_NMRmainfolder():
    global NMRmainfolder_path
    filename = filedialog.askdirectory()
    NMRmainfolder_path.set(filename)
    defining_NMRFolder(filename, update = True)

    
NMRmainfolder_label = Label(Welcome_Option_frame,text="Spinsolve Folder", font = FONT_ENTRY)
NMRmainfolder_label.grid(row = 4, column = 0, columnspan = 2, padx = 10, pady = 10)
NMRmainfolder_path = StringVar(value = NMRFolder)
NMRmainfolder = Label(Welcome_Option_frame,textvariable=NMRmainfolder_path)
NMRmainfolder.grid(row=5, column=0, columnspan = 2)
NMRmainfolder_btn = Button(Welcome_Option_frame, text="Browse", command=update_NMRmainfolder)
NMRmainfolder_btn.grid(row=5, column=2)

    # GPC folder entry
def update_Psswinmainfolder():
    global Psswinmainfolder_path
    filename = filedialog.askdirectory()
    Psswinmainfolder_path.set(filename)
    defining_NMRFolder(filename, update = True)

Psswinmainfolder_label = Label(Welcome_Option_frame,text="Psswin Folder", font = FONT_ENTRY)
Psswinmainfolder_label.grid(row = 6, column = 0, columnspan = 2, padx = 10, pady = 10)
Psswinmainfolder_path = StringVar(value = PsswinFolder)
Psswinmainfolder = Label(Welcome_Option_frame,textvariable=Psswinmainfolder_path)
Psswinmainfolder.grid(row=7, column=0, columnspan = 2)
Psswinmainfolder_btn = Button(Welcome_Option_frame, text="Browse", command=update_Psswinmainfolder)
Psswinmainfolder_btn.grid(row=7, column=2)

labviewscript_info = Label(Welcome_Option_frame, text = "Labview script", font= FONT_SMALL_BOLD)
labviewscript_info.grid(row = 8, column = 0, columnspan = 2, padx = 10)
script = Label(Welcome_Option_frame, text = Labviewscript, font= FONT_SMALL)
script.grid(row=9, column=0, columnspan = 2)


### NMR  - SETUP TAB ###
#Create Main frame of Setup Tab
NMRGPC_setup_top_frame = Frame(tab_NMRGPC_Setup, bg='white', width=1000, height=50, pady=3, padx = 400)
NMRGPC_setup_top_frame.grid(row=0, sticky = 'ew')

NMRGPC_setup_picture_frame = Frame(tab_NMRGPC_Setup, bg='white', width=1000, height=300, padx=175, pady=3)
NMRGPC_setup_picture_frame.grid(row=1,sticky = 'ew')

NMRGPC_setup_parameter_frame = Frame(tab_NMRGPC_Setup, bg='gray', width=1000, height=350, pady=3)
NMRGPC_setup_parameter_frame.grid(row=2,sticky = 'ew')

NMRGPC_setup_confirm_frame = Frame(tab_NMRGPC_Setup, bg='gray', width=1000, height=50, pady=10, padx = 400)
NMRGPC_setup_confirm_frame.grid(row=4, sticky="ew")

    #Make-Up Top Frame
name_window = Label(NMRGPC_setup_top_frame, text= 'Setup',bg='white')
name_window.config(font=FONT_HEADER)
name_window.grid()

    #Make-Up Picture_frame
NMRGPC_picure_setup = PhotoImage(file = 'Pictures/NMRGPCsetup.png')
NMRGPC_LabelPicture = Label(master = NMRGPC_setup_picture_frame, image= NMRGPC_picure_setup, bg ='white')
NMRGPC_LabelPicture.grid()

#make-up Parameter frame
def change_values():
    logger.info('Parameters Changed')
    list_parameters = parameterList1
    entries = [i[0] for i in list_parameters]
    entries_values = [i.get() for i in entries]

    for i, value in enumerate(entries_values):
        if list(value) == []:
            pass
        else:
            if isfloat(value) == True and float(list_parameters[i][4]) != float(value):
                if float(value) == 0:
                    return logger.warning('\tNo changes, entry needs to be non-zero value.')
                else:
                    parameterList1[i][4] = float(value)
            else:
                pass

    for i, parameter in enumerate(parameterList1):
        parameter[1] = Label(NMRGPC_setup_parameter_frame, text = parameter[4], bg = 'gray', width = 20)
        parameter[1].config(font=FONT_NORMAL, anchor = 'e')
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
    parameter = Label(NMRGPC_setup_parameter_frame, text = v[2], bg = 'gray', width = 30)
    parameter.config(font=FONT_NORMAL)
    parameter.grid(row = i, column =0)

    v[0] = Entry(NMRGPC_setup_parameter_frame, width = 15)
    v[0].grid(row = i, column = 1)

    unit = Label(NMRGPC_setup_parameter_frame, text = v[3], bg ='gray', width= 10)
    unit.config(font=FONT_NORMAL, anchor = 'w')
    unit.grid(row = i, column = 2)

    v[5] = Button(NMRGPC_setup_parameter_frame, text= 'Change', command = change_values)
    v[5].grid(row =i, column = 3)
     
    v[1] = Label(NMRGPC_setup_parameter_frame, text = v[4], bg = 'gray', width = 20)
    v[1].config(font=FONT_NORMAL, anchor = 'e')
    v[1].grid(row = i, column =4)

    unit2 = Label(NMRGPC_setup_parameter_frame, text = v[3], bg ='gray')
    unit2.config(font= FONT_NORMAL)
    unit2.config(font = FONT_NORMAL)
    unit2.grid(row = i, column = 5)

def Confirm_reactor_parameters ():
    logger.info('Reactor parameters confirmed')
    confirm_reactorParameters.configure(state = 'disabled')
    for parameterline in parameterList1:
        parameterline[5].configure(state = 'disabled')
        parameterline[0].configure(state = 'readonly')
    tab_control.tab(tab_NMRGPC_Timesweeps, state = 'normal')
    tab_control.select(tab_NMRGPC_Timesweeps)
    confirm_reactorParameters.configure(state = 'disabled')
    
confirm_reactorParameters = Button(NMRGPC_setup_confirm_frame, text = 'Confirm', command = Confirm_reactor_parameters, height= 3, width = 15, font = FONT_BOTTON)
confirm_reactorParameters.grid()
tab_control.grid()
root.mainloop()