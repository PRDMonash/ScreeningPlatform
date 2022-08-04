from msilib.schema import Font
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
from log_method import setup_logger
from defining_folder import defining_communication_folder, defining_PsswinFolder, defining_NMRFolder
from helpers import isfloat
from Constants import SETUP_DEFAULT_VALUES_NMR, FONTS


logger = setup_logger('App')

DRIVE = 'S'
Temporary_textfile, Pathlastexp_textfile, CommunicationMainFolder = defining_communication_folder(os.path.join(os.path.dirname(os.getcwd()),'CommunicationFolder'))
PsswinFolder = defining_PsswinFolder('{}:/Sci-Chem/PRD/GPC 112/2018-March/Projects'.format(DRIVE))
NMRFolder = defining_NMRFolder('C:/PROJECTS/DATA')

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
header_Welcome = Label(Welcome_top_frame, text= 'Welcome',bg='white', font = FONTS['FONT_HEADER'])
header_Welcome.grid()

Welcome_Option_frame = Frame(tab_welcome)
Welcome_Option_frame.grid()
Welcom_option_frame_header = Label(Welcome_Option_frame, text = 'Choose a mode of operation', font = FONTS['FONT_HEADER_BOLD'])
Welcom_option_frame_header.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)
optionNMR_btn = Button(Welcome_Option_frame, text = "NMR", command = NMR,width = 20, height = 3, font = FONTS['FONT_HEADER_BOLD'])
optionNMR_btn.grid(row = 1, column = 0, padx = 10, pady=10)
optionNMRGPC_btn = Button(Welcome_Option_frame, text = "NMR-GPC", command = NMRGPC, width = 20, height = 3, font = FONTS['FONT_HEADER_BOLD'])
optionNMRGPC_btn.grid(row =1, column = 1, padx = 10, pady = 10)

    # Communication folder entry
def update_comfolder():
    global comfolder_path
    filename = filedialog.askdirectory()
    comfolder_path.set(filename)
    defining_communication_folder(filename, update = True)

comfolder_label = Label(Welcome_Option_frame,text="Communication Folder", font = FONTS['FONT_ENTRY'])
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

    
NMRmainfolder_label = Label(Welcome_Option_frame,text="Spinsolve Folder", font = FONTS['FONT_ENTRY'])
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

Psswinmainfolder_label = Label(Welcome_Option_frame,text="Psswin Folder", font = FONTS['FONT_ENTRY'])
Psswinmainfolder_label.grid(row = 6, column = 0, columnspan = 2, padx = 10, pady = 10)
Psswinmainfolder_path = StringVar(value = PsswinFolder)
Psswinmainfolder = Label(Welcome_Option_frame,textvariable=Psswinmainfolder_path)
Psswinmainfolder.grid(row=7, column=0, columnspan = 2)
Psswinmainfolder_btn = Button(Welcome_Option_frame, text="Browse", command=update_Psswinmainfolder)
Psswinmainfolder_btn.grid(row=7, column=2)

labviewscript_info = Label(Welcome_Option_frame, text = "Labview script", font= FONTS['FONT_SMALL_BOLD'])
labviewscript_info.grid(row = 8, column = 0, columnspan = 2, padx = 10)
script = Label(Welcome_Option_frame, text = Labviewscript, font= FONTS['FONT_SMALL'])
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
NMRGPC_setup_confirm_frame.grid(row=3, sticky="ew")

    #Make-Up Top Frame
name_window = Label(NMRGPC_setup_top_frame, text= 'Setup',bg='white')
name_window.config(font=FONTS['FONT_HEADER'])
name_window.grid()

    #Make-Up Picture_frame
NMRGPC_picure_setup = PhotoImage(file = 'Pictures/NMRGPCsetup.png')
NMRGPC_LabelPicture = Label(master = NMRGPC_setup_picture_frame, image= NMRGPC_picure_setup, bg ='white')
NMRGPC_LabelPicture.grid()

    #Make-up Parameter frame
def change_values():
    """
    Changes the values of the setup (NMR mode)
    Note: press any 'change' button and all parameters change
    """
    list_parameters = SETUP_DEFAULT_VALUES_NMR
    entries_values = [i[0].get() for i in list_parameters] # i[0] are the entry fields of the GUI; .get() extracts the values
    logger.debug(entries_values)
    

    for i, value in enumerate(entries_values):
        parameter = SETUP_DEFAULT_VALUES_NMR[i][2] # extracts the parameter
        if list(value) == []: # if no entry, pass
            pass
        else:
            if isfloat(value) == True and float(list_parameters[i][4]) != float(value): # if number is a float (no string) and new value is not the same as old value
                if float(value) == 0: #parameter cannot be zero
                    return logger.warning('No changes, entry needs to be non-zero value.')
                else:
                    old_parameter = SETUP_DEFAULT_VALUES_NMR[i][4]
                    SETUP_DEFAULT_VALUES_NMR[i][4] = float(value) # Changes the old value to the given new value
                    logger.info('{} changed from {} to {}'.format(parameter,old_parameter, SETUP_DEFAULT_VALUES_NMR[i][4]))
            else:
                pass

    for i, parameter in enumerate(SETUP_DEFAULT_VALUES_NMR):
        parameter[1] = Label(NMRGPC_setup_parameter_frame, text = parameter[4], bg = 'gray', width = 20) # changes value in GUI
        parameter[1].config(font=FONTS['FONT_NORMAL'], anchor = 'e')
        parameter[1].grid(row = i, column =4)
    

    # Creates the list of parameters (see Constants file), where index is the row number
for i, entry_values in enumerate(SETUP_DEFAULT_VALUES_NMR):
    parameter = Label(NMRGPC_setup_parameter_frame, text = entry_values[2], bg = 'red', width = 30) # parameter name in column 0
    parameter.config(font=FONTS['FONT_NORMAL'])
    parameter.grid(row = i, column =0)

    entry_values[0] = Entry(NMRGPC_setup_parameter_frame, width = 15)   # entry in column 1
    entry_values[0].grid(row = i, column = 1)

    unit = Label(NMRGPC_setup_parameter_frame, text = entry_values[3], bg ='red', width= 10) # unit in column 2
    unit.config(font=FONTS['FONT_NORMAL'], anchor = 'w') #anchor the left of the label (west)
    unit.grid(row = i, column = 2)

    entry_values[5] = Button(NMRGPC_setup_parameter_frame, text= 'Change', command = change_values) # botton (with text change) in column 3
    entry_values[5].grid(row =i, column = 3)
     
    entry_values[1] = Label(NMRGPC_setup_parameter_frame, text = entry_values[4], bg = 'red', width = 20) # default value in column 4
    entry_values[1].config(font=FONTS['FONT_NORMAL'], anchor = 'e') #anchor to the right of the label (east)
    entry_values[1].grid(row = i, column =4)

    unit2 = Label(NMRGPC_setup_parameter_frame, text = entry_values[3], bg ='gray') # again unit in column 5
    unit2.config(font= FONTS['FONT_NORMAL'])
    unit2.grid(row = i, column = 5)

def Confirm_reactor_parameters ():
    logger.info('Reactor parameters confirmed')
    confirm_reactorParameters.configure(state = 'disabled')
    for parameterline in SETUP_DEFAULT_VALUES_NMR: # once confirmed, do not allow further changes by disabling button
        parameterline[5].configure(state = 'disabled') # button disabled
        parameterline[0].configure(state = 'readonly') # entry readonly
    tab_control.tab(tab_NMRGPC_Timesweeps, state = 'normal') # unlock next tab
    tab_control.select(tab_NMRGPC_Timesweeps) # select next tab
    confirm_reactorParameters.configure(state = 'disabled') # disable confirm botton
    
    # Make-up confirm frame
confirm_reactorParameters = Button(NMRGPC_setup_confirm_frame, text = 'Confirm', command = Confirm_reactor_parameters, height= 3, width = 15, font = FONTS['FONT_BOTTON'])
confirm_reactorParameters.grid()

tab_control.grid()
root.mainloop()