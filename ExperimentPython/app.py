from tkinter import *
from tkinter import ttk
import logging
from log_method import setup_logger

logger = setup_logger('App')


FONT_NORMAL = ('Ariel', 15)
FONT_HEADER = ('Courier',30)
FONT_BOTTON = ('Ariel', 10)
FONT_HEADER_BOLD = ('Ariel', 18, 'bold')
FONT_ENTRY = ('Ariel', 17)
FONT_SMALL = ('Ariel', 10)
FONT_SMALL_BOLD = ('Ariel', 10, 'bold')

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
    optionNMR_btm.configure(state= 'disabled')
    optionNMRGPC_btm.configure(state= 'disabled')
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
Welcome_Option_frame = Frame(tab_welcome)
Welcome_Option_frame.grid()
Welcom_option_frame_header = Label(Welcome_Option_frame, text = 'Choose a mode of operation', font = FONT_HEADER_BOLD)
Welcom_option_frame_header.grid(row = 0, column = 0, columnspan = 2, padx = 10, pady = 10)
optionNMR_btm = Button(Welcome_Option_frame, text = "NMR", command = NMR,width = 20, height = 3, font = FONT_HEADER_BOLD)
optionNMR_btm.grid(row = 1, column = 0, padx = 10, pady=10)
optionNMRGPC_btm = Button(Welcome_Option_frame, text = "NMR-GPC", command = NMRGPC, width = 20, height = 3, font = FONT_HEADER_BOLD)
optionNMRGPC_btm.grid(row =1, column = 1, padx = 10, pady = 10)


tab_control.grid()
root.mainloop()