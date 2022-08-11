from pathlib import Path
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
import os
import pandas as pd

from code_extra.log_method import setup_logger
from code_extra.defining_folder import defining_communication_folder, defining_PsswinFolder, defining_NMRFolder, SearchExperimentFolder
from code_extra.helpers import isfloat
from code_extra.Constants import SETUP_DEFAULT_VALUES_NMR, FONTS, TIMESWEEP_PARAMETERS, FOLDERS
from code_extra.calculateScans import CalculateScans

from code_extra.precheck import check_files, check_Emailconnection
from code_extra.start_experiment import starting


check_files()
email_check = check_Emailconnection()

logger = setup_logger('App')

Temporary_textfile, Pathlastexp_textfile, CommunicationMainFolder = defining_communication_folder(FOLDERS['COMMUNICATION'])
PsswinFolder = defining_PsswinFolder(FOLDERS['GPC'])
NMRFolder = defining_NMRFolder(FOLDERS['NMR'])

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
    tab_control.tab(tab_NMRGPC_Initialisation, state = 'normal')
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
    

def extractChemicals():
    """
    Extracts the chemicals; lists needs to be global to be accessed within the popup
    """
    global RAFTlist
    global solventlist
    global initiatorlist
    global monomerlist
    global chemicals 

    chemicals = pd.read_csv('Files/Chemicals.csv')
    
    #extracts all chemicals by class
    RAFTlist = chemicals[chemicals["class"]=='RAFT']
    solventlist = chemicals[chemicals["class"]=='solvent']
    initiatorlist = chemicals[chemicals["class"]=='initiator']
    monomerlist = chemicals[chemicals["class"]=='monomer']

global SolutionDataframe
SolutionDataframe = pd.DataFrame()

def changeSolution():
    def confirmSolution():
        #get all the selected chemicals from the menu fields
        finalMonomer, finalSolvent, finalRAFT, finalInitiator = optionsMonomer.get(), optionsSolvent.get(), optionsRAFT.get(), optionsinitiator.get() 
        logger.debug('Selected Chemicals: {}, {}, {}, {}'.format(finalMonomer, finalSolvent, finalRAFT, finalInitiator))

        # extract all values from the entries and checks for floats (no strings); closes window if no string
        list_entries = [gramRAFT, graminitiator, mLMonomer, mLsolvent]
        for entry in list_entries:
            if not isfloat(entry.get()):
                logger.debug('One of the entries ({}) was a not a float'.format(entry.get()))
                solution_popup.destroy()
                return None
        #get full pandas.Series (from list extracted from csv file) of chemical where abbreviation is finalChemical (from selected chemical in GUI)
        monomer = (monomerlist[monomerlist['abbreviation']==finalMonomer]) 
        solvent = (solventlist[solventlist['abbreviation']==finalSolvent])
        raft = (RAFTlist[RAFTlist['abbreviation']==finalRAFT])
        initiator = (initiatorlist[initiatorlist['abbreviation']==finalInitiator])
        #logger.debug('Full names of chemicals: {}, {}, {}, {}'.format(monomer, solvent, raft, initiator)) #thse are pandas.core.frame.DataFrame
        #logger.debug('Should be type pandas.core.frame.DataFrame. Real type: {}'.format(type(raft)))

        global SolutionDataframe
        SolutionDataframe = pd.concat([raft, monomer, initiator, solvent], ignore_index = True) #make one dataframe from selected chemicals


        #extract entries () and add them to dataframe (new columns are created (mass (g) and volume (mL)) )
        SolutionDataframe.loc[SolutionDataframe['class'] == 'RAFT', 'mass (g)'] = float(gramRAFT.get())
        SolutionDataframe.loc[SolutionDataframe['class'] == 'monomer', 'volume (mL)'] = float(mLMonomer.get())
        SolutionDataframe.loc[SolutionDataframe['class'] == 'initiator', 'mass (g)'] = float(graminitiator.get())
        SolutionDataframe.loc[SolutionDataframe['class'] == 'solvent', 'volume (mL)'] = float(mLsolvent.get())

        #convert volume to mass where needed
        SolutionDataframe.loc[SolutionDataframe['class'] == 'monomer', 'mass (g)'] = float(mLMonomer.get()) * float(SolutionDataframe.loc[SolutionDataframe['class'] == 'monomer', 'density'])
        SolutionDataframe.loc[SolutionDataframe['class'] == 'solvent', 'mass (g)'] = float(mLsolvent.get()) * float(SolutionDataframe.loc[SolutionDataframe['class'] == 'solvent', 'density'])

        #moles in dataframe for all chemicals
        SolutionDataframe['moles (mol)'] = SolutionDataframe['mass (g)'] / SolutionDataframe['molecular mass']
        #molar in dataframe for all entries
        total_volume = SolutionDataframe['volume (mL)'].sum()
        SolutionDataframe['Molar (M)'] = SolutionDataframe['moles (mol)'] / (total_volume/1000)
        #eq in dataframe for all entries
        molesRAFT = float(SolutionDataframe.loc[SolutionDataframe['class']=='RAFT', 'moles (mol)'])
        SolutionDataframe['eq'] = [i/molesRAFT for i in SolutionDataframe['moles (mol)']]
        
        #create summary string
        #Format --> Monomer:Raft:ini xx:1:xxx (xxxx g/mol); xM Monomer; Solvent
        raft = SolutionDataframe.iloc[0]
        monomer = SolutionDataframe.iloc[1]
        initiator = SolutionDataframe.iloc[2]
        solvent = SolutionDataframe.iloc[3]

        Mn_100 = raft['molecular mass'] + (monomer['molecular mass']*monomer['eq']) #Mn for 100% conversion
        
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
        logger.info('Reaction Solution confirmed: {}'.format(summaryString.replace('\n','')))
        SolutionDataframe.to_csv(os.path.join(CommunicationMainFolder, 'code_Solution.csv'))
        logger.info('code_Solution.csv saved in Communication folder ({})'.format(CommunicationMainFolder))
        

    solution_popup = Toplevel()
    solution_popup.title('Reaction Solution')

    popuptitle = Label(solution_popup, text = 'Reaction Solution', font = FONTS['FONT_HEADER'], padx=15)
    popuptitle.grid(row=0, column = 0, columnspan= 3)
    #monomer
    mLMonomer = Entry(solution_popup) # Entry in Column 1
    mLMonomer.grid(row=1, column = 1)

    optionsMonomer = StringVar()
    optionsMonomer.set('MA')
    MenuMonomer = OptionMenu(solution_popup, optionsMonomer, *monomerlist['abbreviation']) #Menu in Column 0
    MenuMonomer.grid(row = 1, column= 0)

    monomerlabel = Label(solution_popup, text = 'mL') # Unit in column 2
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

    Confirmsolution2 = Button(solution_popup, text = 'Confirm', command = confirmSolution, font = FONTS['FONT_BOTTON']) # Upon Confirmation --> confirmSolution()
    Confirmsolution2.grid(row=5, column = 1)

     
extractChemicals()
solutionSummary1 = Label(NMRGPC_setup_parameter_frame, text = 'Reaction Solution', bg = 'gray', font = FONTS['FONT_NORMAL'], pady = 20)
solutionSummary1.grid(row = i+1, column= 0, columnspan = 2, rowspan = 2 ) #row i + 1; i last row from parameters
solution_button1 = Button(NMRGPC_setup_parameter_frame, text = 'Reaction solution', command = changeSolution)
solution_button1.grid(row = i+1, column= 3)

    # Make-up confirm frame
confirm_reactorParameters = Button(NMRGPC_setup_confirm_frame, text = 'Confirm', command = Confirm_reactor_parameters, height= 3, width = 15, font = FONTS['FONT_BOTTON'])
confirm_reactorParameters.grid()

####TIMESWEEP TAB####
#Create Main frame of Timesweep Tab
NMRGPC_timesweep_top_frame = Frame(tab_NMRGPC_Timesweeps, bg='white', width=1000, height=50, pady=3, padx = 400)
NMRGPC_timesweep_top_frame.grid(row=0, sticky="ew")
NMRGPC_timesweep_picture_frame = Frame(tab_NMRGPC_Timesweeps, bg='white', width=1000, height=300, padx=175, pady=3)
NMRGPC_timesweep_picture_frame.grid(row=1, sticky="nsew")
NMRGPC_timesweep_parameter_frame = Frame(tab_NMRGPC_Timesweeps, bg='gray', width=1000, height=350, pady=3,padx = 3)
NMRGPC_timesweep_parameter_frame.grid(row=3, sticky="ew")
NMRGPC_timesweep_confirm_frame = Frame(tab_NMRGPC_Timesweeps, bg='gray', width=1000, height=50, pady=10, padx = 10)
NMRGPC_timesweep_confirm_frame.grid(row=4, sticky="ew")

#Make-Up Top Frame in Timesweep Tab
NMRGPC_timesweep_header = Label(NMRGPC_timesweep_top_frame, text= 'Timesweeps',bg='white')
NMRGPC_timesweep_header.config(font=FONTS['FONT_HEADER'])
NMRGPC_timesweep_header.grid()

#Make-Up NMRGPC_timesweep_picture_frame in Timsweep Tab
picture_timesweep = PhotoImage(file = 'Pictures\Timesweeps_pictureFrame.png')
LabelPicture = Label(master = NMRGPC_timesweep_picture_frame, image=picture_timesweep, bg ='white')
LabelPicture.grid()

#Make-Up Parameter_frame_timesweep in Timesweep Tab
NMRGPC_all_ts_info = [] #list where all the timesweeps will be saved

#extracts reactorvolume, NMR interval and GPC interval from confirmed setup parameters 
reactorvol = SETUP_DEFAULT_VALUES_NMR[0][4]
NMRinterval1 = SETUP_DEFAULT_VALUES_NMR[4][4]
GPCinterval1= SETUP_DEFAULT_VALUES_NMR[5][4]

def insert_timesweep():
    '''
    Called by insert button in timesweep tab
    '''
    #delete whitespaces in entry
    ts_from_en1 = (ts_from_en.get()).replace(' ', '')
    ts_to_en1 = (ts_to_en.get()).replace(' ', '')

    #checks if entry is number
    if isfloat(ts_from_en.get()) == True and isfloat(ts_to_en.get()):
        if float(ts_from_en1) != float(ts_to_en1) and float(ts_to_en1) != 0 and float(ts_from_en1) !=0: # Checks for non-zero entries and non-identical
            number_of_added_timesweep = len(NMRGPC_all_ts_info) +1 #if 0 timesweeps, added timesweep will have number 1

            from_ , to_ = float(ts_from_en.get()), float(ts_to_en.get())
            fr1, fr2 = float(reactorvol)/float(from_),float(reactorvol)/float(to_) #calculate flowrates

            # Creates list with [the label for the GUI, and the content of the label as string, from_minutes, to_minutes]
            timesweep_info = ['label_{}'.format(number_of_added_timesweep), 'Timesweep {}: From {} minutes ({} mL/min) to {} minutes ({} mL/min) (NMR interval: {}sec, GPC interval: {}min)'.format(number_of_added_timesweep, from_, round(fr1, 3), to_, round(fr2, 3), NMRinterval1, GPCinterval1), from_, to_]
            logger.debug(timesweep_info)
            logger.info('Timesweep added: {}'.format(timesweep_info[1]))
            NMRGPC_all_ts_info.append(timesweep_info) #list of lists e.g. [[label_1, text_1] , [label_2, text_2]]

            for i, ts_info in enumerate(NMRGPC_all_ts_info): # Creates 'List of Timesweeps'
                ts_info[0] = Label(NMRGPC_timesweep_parameter_frame, text = ts_info[1], bg = 'gray', width = 90, font = FONTS['FONT_SMALL'], anchor = 'w')
                ts_info[0].grid(row = 5+i, columnspan = 5)

                #to_minute of timesweep i is from_minute of timesweep i+1
                entryText = DoubleVar()
                entryText.set(NMRGPC_all_ts_info[-1][-1])
                logger.debug('This is the to_minutes varialbe of the last entred timesweep : {}'.format(NMRGPC_all_ts_info[-1][-1]))
                ts_from_en.configure(textvariable=entryText, state= 'readonly')

            confirm_ts_btm.config(state = 'normal')
            delete_ts_btm.config(state = 'normal')
        else:
            logger.warning('Error: No change, entries cannot be the same')
    else:
        pass

def delete_timesweep():
    logger.debug('length of timesweeps is not 0: {}'.format(len(NMRGPC_all_ts_info) != 0))
    if len(NMRGPC_all_ts_info) != 0:
        logger.info('TImesweep deleted: {}'.format(NMRGPC_all_ts_info[-1][1]))
        NMRGPC_all_ts_info[-1][0].destroy() #destroys 'label' of last timesweep
        NMRGPC_all_ts_info.pop(-1) #deletes full entry in timesweep list
    else:
        pass

    #after removing the only one timesweep, disable delete button and fill from_entry with 0
    if len(NMRGPC_all_ts_info) == 0:
        confirm_ts_btm.config(state = 'disabled')
        delete_ts_btm.config(state = 'disabled')
        entryText = DoubleVar()
        ts_from_en.configure(textvariable=entryText, state= 'normal')

    # fill the from_entry with to_value of last timesweep
    else:
        entryText = DoubleVar()
        entryText.set(NMRGPC_all_ts_info[-1][-1])
        ts_from_en.configure(textvariable=entryText, state= 'readonly')
        pass


tsparam_header = Label(NMRGPC_timesweep_parameter_frame, text = "Insert Timesweep Parameters", bg = 'gray', width = 27)
tsparam_header.config(font= FONTS['FONT_HEADER_BOLD'])
tsparam_header.grid(row = 0, column =1, columnspan = 4)
    
ts_from_lbl = Label(NMRGPC_timesweep_parameter_frame, text = 'From (minutes)', width= 15, bg ='gray', font = FONTS['FONT_NORMAL'], anchor = 'center')
ts_from_lbl.grid(row = 1, column = 1, columnspan = 2)

ts_from_en = Entry(NMRGPC_timesweep_parameter_frame, width = 5, font= FONTS['FONT_ENTRY'])
ts_from_en.grid(row = 2, column = 1)

ts_to_lbl = Label(NMRGPC_timesweep_parameter_frame, text = 'To (minutes)', bg = 'gray', font = FONTS['FONT_NORMAL'], anchor = 'center')
ts_to_lbl.grid(row = 1, column = 4, columnspan =2)

ts_to_en = Entry(NMRGPC_timesweep_parameter_frame, width = 5, font=FONTS['FONT_ENTRY'])
ts_to_en.grid(row = 2, column = 4)

insert_ts_btm = Button(NMRGPC_timesweep_parameter_frame, text = 'Add', command = insert_timesweep,font= FONTS['FONT_BOTTON'])
insert_ts_btm.grid(row = 3, column = 2)

delete_ts_btm = Button(NMRGPC_timesweep_parameter_frame, text = 'Delete', command = delete_timesweep, font= FONTS['FONT_BOTTON'], state = 'disabled')
delete_ts_btm.grid(row = 3, column = 3)

confirmed_ts = Label(NMRGPC_timesweep_parameter_frame, text = 'List of Timesweeps', bg ='gray')
confirmed_ts.config(font= FONTS['FONT_HEADER_BOLD'], anchor ='w')
confirmed_ts.grid(row = 4, column =0)


def finalize_timesweeps ():

    reactorvol = SETUP_DEFAULT_VALUES_NMR[0][4]
        
    for i, timesweep in enumerate(NMRGPC_all_ts_info):
        fr1, fr2 = reactorvol/timesweep[2], reactorvol/timesweep[3]
        #Create DF with all the parameters
        TIMESWEEP_PARAMETERS.loc[i, 'Start_min']= timesweep[2]
        TIMESWEEP_PARAMETERS.loc[i, 'Stop_min']= timesweep[3]
        TIMESWEEP_PARAMETERS.loc[i, 'Volume'] = SETUP_DEFAULT_VALUES_NMR[0][4]
        TIMESWEEP_PARAMETERS.loc[i, 'StartFR'] = fr1
        TIMESWEEP_PARAMETERS.loc[i, 'StopFR'] = fr2
        TIMESWEEP_PARAMETERS.loc[i, 'DeadVolume1'] = SETUP_DEFAULT_VALUES_NMR[1][4]
        TIMESWEEP_PARAMETERS.loc[i, 'DeadVolume2'] = SETUP_DEFAULT_VALUES_NMR[2][4]
        TIMESWEEP_PARAMETERS.loc[i, 'DeadVolume3'] = SETUP_DEFAULT_VALUES_NMR[3][4]
        TIMESWEEP_PARAMETERS.loc[i, 'NMRInterval'] = SETUP_DEFAULT_VALUES_NMR[4][4]
        TIMESWEEP_PARAMETERS.loc[i, 'GPCInterval'] = SETUP_DEFAULT_VALUES_NMR[5][4]
        TIMESWEEP_PARAMETERS.loc[i, 'StabilisationTime'] = SETUP_DEFAULT_VALUES_NMR[6][4]
        TIMESWEEP_PARAMETERS.loc[i, 'DilutionFR'] = SETUP_DEFAULT_VALUES_NMR[7][4]
        TIMESWEEP_PARAMETERS.loc[i, 'DeadVolume1(min)'] = TIMESWEEP_PARAMETERS.loc[i, 'DeadVolume1']/TIMESWEEP_PARAMETERS.loc[i,'StopFR']
        TIMESWEEP_PARAMETERS.loc[i, 'DeadVolume2(min)'] = TIMESWEEP_PARAMETERS.loc[i,'DeadVolume1']/TIMESWEEP_PARAMETERS.loc[i ,'StopFR']
        TIMESWEEP_PARAMETERS.loc[i, 'DeadVolume3(min)'] = TIMESWEEP_PARAMETERS.loc[i,'DeadVolume1']/TIMESWEEP_PARAMETERS.loc[i,'DilutionFR']
        TIMESWEEP_PARAMETERS.loc[i, 'Mode'] = 'GPCandNMR'

        TIMESWEEP_PARAMETERS.to_csv(os.path.join(CommunicationMainFolder, 'code_Parameters.csv'))
        logger.info('code_Paramters.csv saved in communication folder ({})'.format(CommunicationMainFolder))

                
    logger.info('Confirmed timesweep Experiment:\n{}'.format(TIMESWEEP_PARAMETERS))
    scannumbers = CalculateScans(TIMESWEEP_PARAMETERS, mode = 'GPCandNMR')
    
    scannumbers.to_csv(os.path.join(CommunicationMainFolder, 'code_Scans.csv'))
    logger.info('code_Scans.csv saved in communication folder ({})'.format(CommunicationMainFolder))

    totalscan = scannumbers['Stop Scan GPC'].iloc[-1]
    total_time = (totalscan * TIMESWEEP_PARAMETERS.loc[0,'NMRInterval']) /60
    totalgpc = sum([scannumbers['GPC Samples'].iloc[i] for i in range(int(scannumbers.shape[0]))])
        
    entry1 = TIMESWEEP_PARAMETERS.iloc[0]
    stabili = ((entry1['Volume']*entry1['StabilisationTime']))
    allDvs = (((entry1['DeadVolume1'] + entry1['DeadVolume2']+ entry1['DeadVolume3']) * int(scannumbers.shape[0])))
    ts_number= int(scannumbers.shape[0])
    totalvolume = stabili +(ts_number* allDvs)

    summary_1 = Label(NMRGPC_timesweep_confirm_frame, text = 'Total time:             {}min'.format(round(total_time,1)), width = 90, bg= 'gray', anchor = 'w',padx = 10)
    summary_1.grid(row= 1, column= 0)
    summary_2 = Label(NMRGPC_timesweep_confirm_frame, text = 'Total NMR scans:         {}'.format(round(totalscan,0)), width = 90, bg= 'gray', anchor = 'w')
    summary_2.grid(row= 2, column= 0)
    summary_3 = Label(NMRGPC_timesweep_confirm_frame, text = 'Total GPC samples:       {}'.format(round(totalgpc,0)), width = 90, bg= 'gray', anchor = 'w')
    summary_3.grid(row= 3, column= 0)
    summary_4 = Label(NMRGPC_timesweep_confirm_frame, text = 'Volume Needed:       {} mL'.format(round(totalvolume,1)), width = 90, bg= 'gray', anchor = 'w')
    summary_4.grid(row= 4, column= 0)

    logger.info('Experiment will take {} minutes; +/- {} mL reaction solution is needed.'.format(total_time, totalvolume))
    ts_from_en.configure(state = 'readonly')
    ts_to_en.configure(state = 'readonly')
    insert_ts_btm.configure(state = 'disabled')
    delete_ts_btm.configure(state = 'disabled')
    confirm_ts_btm.configure(state = 'disabled')


    tab_control.tab(tab_NMRGPC_Conversion, state = 'normal')
    tab_control.select(tab_NMRGPC_Conversion)

    
summary_1 = Label(NMRGPC_timesweep_confirm_frame, text = ' ', width = 90, bg= 'gray', anchor = 'w', padx = 10)
summary_1.grid(row= 1, column= 0)
    
confirm_ts_btm = Button(NMRGPC_timesweep_confirm_frame, text = 'Confirm', height= 3, width = 15,  command = finalize_timesweeps, state = 'disabled', font = FONTS['FONT_BOTTON'])
confirm_ts_btm.grid(row= 1, column =2, rowspan = 3)

####### Conversion Tab GPC #######
NMRGPC_top_frame_conv = Frame(tab_NMRGPC_Conversion, bg='white', width=1000, height=50, pady=3, padx = 400)
NMRGPC_top_frame_conv.grid(row=0, sticky="ew")

name_window_conv = Label(NMRGPC_top_frame_conv, text= 'Conversion',bg='white', font = FONTS['FONT_HEADER'])
name_window_conv.grid()

def confirm_conversion_NMRGPC ():
    global conversion_determination
    global mol_init_monomer
    global mol_init_IS

    conversion_determination= Conversion_option_NMRGPC.get()
    # 1 = Internal standard, 2 = monomer peaks , 3 = solvent

    if conversion_determination == 1: #confirm for Internal Standard
        if isfloat(mol_monomerEntry_NMRGPC.get()) and isfloat(mol_internal_standardEntry_NMRGPC.get()): # Mols must be given to calculate ratio and conversion
            mol_init_monomer = float(mol_monomerEntry_NMRGPC.get())
            mol_init_IS = float(mol_internal_standardEntry_NMRGPC.get())
            Conversion_Label_NMRGPC.config(text = 'Ratio Internal Standard/monomer is {}'.format(float(mol_init_IS)/float(mol_init_monomer)))

            mol_internal_standardEntry_NMRGPC.configure(state='disabled')
            mol_monomerEntry_NMRGPC.configure(state = 'disabled')
            mol_monomerLabel_NMRGPC.configure(foreground = 'gray' )
            mol_ISlabel_NMRGPC.configure(foreground = 'gray' )
            confirm_conv_btm_NMRGPC.configure(state ='disabled')
            tab_control.tab(tab_NMRGPC_Initialisation, state = 'normal')
            tab_control.select(tab_NMRGPC_Initialisation)
            monomer_radio_NMRGPC.configure(state = 'disabled')
            IS_radio_NMRGPC.configure(state= 'disabled')
            logger.info('Conversion will be determined via internal standard peaks (4-hydroxy benzaldehyde; ratio IS/monomer {})'.format(float(mol_init_IS)/float(mol_init_monomer)))
        else:
            Conversion_Label_NMRGPC.config(text = 'Entry has to be a number')

    elif conversion_determination == 2: # Confirm for monomer peaks
        mol_internal_standardEntry_NMRGPC.configure(state='disabled')
        mol_monomerEntry_NMRGPC.configure(state = 'disabled')
        mol_monomerLabel_NMRGPC.configure(foreground = 'gray' )
        mol_ISlabel_NMRGPC.configure(foreground = 'gray' )
        tab_control.tab(tab_NMRGPC_Initialisation, state = 'normal')
        tab_control.select(tab_NMRGPC_Initialisation)
        confirm_conv_btm_NMRGPC.configure(state ='disabled')
        monomer_radio_NMRGPC.configure(state = 'disabled')
        IS_radio_NMRGPC.configure(state= 'disabled')
        logger.info('Conversion will be determined via the monomer peaks (no internal standard)')
    
    elif conversion_determination == 3: # Confirm for solvent (butyl acetate)
        if len(SolutionDataframe) == 0:
            logger.warning('Solution data is not given!')
            changeSolution()
            return
        if 'Butyl Acetate' in list(SolutionDataframe['name']):
            mol_internal_standardEntry_NMRGPC.configure(state='disabled')
            mol_monomerEntry_NMRGPC.configure(state = 'disabled')
            mol_monomerLabel_NMRGPC.configure(foreground = 'gray' )
            mol_ISlabel_NMRGPC.configure(foreground = 'gray' )
            tab_control.tab(tab_NMRGPC_Initialisation, state = 'normal')
            tab_control.select(tab_NMRGPC_Initialisation)
            confirm_conv_btm_NMRGPC.configure(state ='disabled')
            monomer_radio_NMRGPC.configure(state = 'disabled')
            IS_radio_NMRGPC.configure(state= 'disabled')
            logger.info('Conversion will be determined via solvent (butyl acetate) + monomer peak')
        else:
            Conversion_Label_NMRGPC.config(text = 'Solvent is not Butyl Acetate.')


    conversion_determination = Conversion_option_NMRGPC.get() #1 = internal standard, 2 = monomer, 3 = solvent

def IS_selected_NMRGPC():
    '''If internal standard option is selected'''
    mol_internal_standardEntry_NMRGPC.configure(state = 'normal')
    mol_monomerEntry_NMRGPC.configure(state = 'normal')
    Conversion_Label_NMRGPC.config(text = 'Internal Standard')
    mol_monomerLabel_NMRGPC.configure(foreground = 'black' )
    mol_ISlabel_NMRGPC.configure(foreground = 'black' )
    
def monomer_selected_NMRGPC():
    '''If monomer option is selected, IS entry fields are disabled'''
    Conversion_Label_NMRGPC.config(text = 'Conversion will be calculated with monomer peaks (only MA for now)')
    mol_internal_standardEntry_NMRGPC.configure(state='disabled')
    mol_monomerEntry_NMRGPC.configure(state = 'disabled')
    mol_monomerLabel_NMRGPC.configure(foreground = 'gray' )
    mol_ISlabel_NMRGPC.configure(foreground = 'gray' )

def solvent_selected_NMRGPC():
    '''If solvent option is selected, IS entry fields are disabled'''
    Conversion_Label_NMRGPC.config(text = 'Conversion will be calculated based on the solvent+monomer peak (butyl acetate)')
    mol_internal_standardEntry_NMRGPC.configure(state='disabled')
    mol_monomerEntry_NMRGPC.configure(state = 'disabled')
    mol_monomerLabel_NMRGPC.configure(foreground = 'gray' )
    mol_ISlabel_NMRGPC.configure(foreground = 'gray' )

Conversion_option_NMRGPC = IntVar()

IS_radio_NMRGPC = Radiobutton(tab_NMRGPC_Conversion, text="Internal Standard", font = FONTS['FONT_ENTRY'], variable=Conversion_option_NMRGPC, value=1, command = IS_selected_NMRGPC)
IS_radio_NMRGPC.grid()
mol_monomerLabel_NMRGPC = Label(tab_NMRGPC_Conversion, text = "Monomer initial (mol)")
mol_monomerLabel_NMRGPC.grid()
mol_monomerEntry_NMRGPC= Entry(tab_NMRGPC_Conversion)
mol_monomerEntry_NMRGPC.grid()
mol_ISlabel_NMRGPC = Label(tab_NMRGPC_Conversion, text = "4-hydroxy benzaldehyde initial (mol)")
mol_ISlabel_NMRGPC.grid()
mol_internal_standardEntry_NMRGPC = Entry(tab_NMRGPC_Conversion)
mol_internal_standardEntry_NMRGPC.grid()

monomer_radio_NMRGPC = Radiobutton(tab_NMRGPC_Conversion, text="Monomer", font = FONTS['FONT_ENTRY'], variable=Conversion_option_NMRGPC, value=2, command = monomer_selected_NMRGPC)
monomer_radio_NMRGPC.grid()

solvent_radio_NMRGPC = Radiobutton(tab_NMRGPC_Conversion, text="Solvent (Butyl Acetate)", font = FONTS['FONT_ENTRY'], variable=Conversion_option_NMRGPC, value=3, command = solvent_selected_NMRGPC)
solvent_radio_NMRGPC.grid()

Conversion_info_frame_NMRGPC = Frame(tab_NMRGPC_Conversion)
Conversion_info_frame_NMRGPC.grid()

Conversion_Label_NMRGPC = Label(Conversion_info_frame_NMRGPC, text = 'Choose option')
Conversion_Label_NMRGPC.grid(row = 0, column = 1, columnspan = 3)

confirm_conv_btm_NMRGPC = Button(Conversion_info_frame_NMRGPC, text = 'Confirm', height= 3, width = 15,  command = confirm_conversion_NMRGPC, font = FONTS['FONT_BOTTON'])
confirm_conv_btm_NMRGPC.grid(row= 1, column =2, rowspan = 3)

####### Init Tab ######
experiment_extra = pd.DataFrame(columns = ['code', 'Mainfolder','GPCfolder', 'Timesweepfolder', 'Infofolder','Softwarefolder', 'Rawfolder', 'Plotsfolder'])

#Create Main frame of init Tab
NMRGPC_top_frame_init = Frame(tab_NMRGPC_Initialisation, bg='white', width=1000, height=50, pady=3, padx = 400)
NMRGPC_top_frame_init.grid(row=0, sticky="ew")
NMRGPC_picture_frame_init = Frame(tab_NMRGPC_Initialisation, bg='white', width=1000, height=300, padx=175, pady=3)
NMRGPC_picture_frame_init.grid(row=1, sticky="nsew")
NMRGPC_parameter_frame_init = Frame(tab_NMRGPC_Initialisation, bg='gray', width=1000, height=350, pady=3,padx = 3)
NMRGPC_parameter_frame_init.grid(row=3, sticky="ew")
NMRGPC_btm_frame_init = Frame(tab_NMRGPC_Initialisation, bg='gray', width=1000, height=50, pady=10, padx = 400)
NMRGPC_btm_frame_init.grid(row=4, sticky="ew")

#Make-Up Top Frame in init Tab
name_window_init = Label(NMRGPC_top_frame_init, text= 'Initialisation',bg='white', font = FONTS['FONT_HEADER'])
name_window_init.grid()

#Make-Up picture_frame_init in Timsweep Tab
picture_init = PhotoImage(file = 'Pictures\Init_picture.png')
LabelPicture_init = Label(master = NMRGPC_picture_frame_init, image=picture_init, bg ='white')
LabelPicture_init.grid(row = 1, column =1)

#Make-Up Parameter_frame_timesweep in ininialisation Tab
tsparam = Label(NMRGPC_parameter_frame_init, text = "Start Initialisation", bg = 'gray', font=FONTS['FONT_HEADER_BOLD'], padx = 150)
tsparam.grid(row = 0, column =1, columnspan=2)
#Experiment code

def check_experimentFoldertxtfile(expfolder, exp_code):
    directory_code = os.path.basename(expfolder).split('_')[-1]
    if not directory_code == exp_code:
        logger.warning('It seems that the code given by LabView ({}) does not match the real code ({}). Please give the correct Experiment Folder'.format(directory_code, exp_code))
        experimentfolder = input('>> ')
        return experimentfolder
    return expfolder

def confirmLabview():
    '''
    Confirms if LabView is started
    '''
    global ExperimentFolder
    global experiment_extra

    if not os.path.exists(Pathlastexp_textfile):
        logger.warning('Text file ({}) were experiment folder is saved does not exists.'.format(Pathlastexp_textfile))

    ExperimentFolder = Path((open(Pathlastexp_textfile, 'r').read().replace("\\", "/")))
    logger.debug('Experiment folder communicated by LabView: {}'.format(ExperimentFolder))

    ExperimentFolder = Path(check_experimentFoldertxtfile(ExperimentFolder, code))

    ExperimentFolder_SDRIVE = str(ExperimentFolder)
    try:
        ExperimentFolder_SDRIVE = ExperimentFolder_SDRIVE.replace('Z', 'S', 1)
        ExperimentFolder_SDRIVE = Path(ExperimentFolder_SDRIVE)
    except:
        pass

    found = False
    while found == False:
        if ExperimentFolder.exists():
            labelLabviewInfo.configure(text = 'Experiment folder found ({})'.format(ExperimentFolder))
            logger.info('Experiment folder found as {}'.format(ExperimentFolder))
            found = True
        elif ExperimentFolder_SDRIVE.exists():
            ExperimentFolder = ExperimentFolder_SDRIVE
            logger.info('Experiment folder found as {} (changed to S drive)'.format(ExperimentFolder))
            labelLabviewInfo.configure(text = 'Experiment folder found ({})'.format(ExperimentFolder))
            found = True
        else:
            labelLabviewInfo.configure(text = 'Experiment folder NOT found.')
            logger.warning('Experiment Folder given by LabView ({}) not found. Please give the correct Experiment Folder.'.format(ExperimentFolder))
            ExperimentFolder = Path(input('>> '))

    experiment_extra.loc[0, 'Mainfolder'] = ExperimentFolder
    experiment_extra = SearchExperimentFolder(ExperimentFolder,CommunicationMainFolder, experiment_extra, mode = 'GPCandNMR')

    labelPss.configure(text = 'Open the PSSwin software and name the experiment ({}.txt).'.format(code))
    confirmPss.configure(state = 'normal')
    HelpPss.configure(state = 'normal')
    confirmLabview.configure(state = 'disabled')
    HelpLabview.configure(state = 'disabled')

def confirmPss():
    labelPssInfo.configure(text = 'Pss Check')
    logger.info('Psswin is okay')
    labelSpinsolve.configure(text = 'Name the experiment ({}) in the Spinsolve software.'.format(code))
    confirmPss.configure(state = 'disabled')
    HelpPss.configure(state = 'disabled')
    confirmSpinsolve.configure(state = 'normal')
    HelpSpinsolve.configure(state = 'normal')

def confirmSpinsolve():
    labelSpinsolveInfo.configure(text = 'Spinsolve Check')
    logger.info('Spinsolve is okay')
    confirmSpinsolve.configure(state = 'disabled')
    HelpSpinsolve.configure(state = 'disabled')
    confirmEmail.configure(state = 'normal')
    AddEmail.configure(state = 'normal')
    entryEmail.configure(state = 'normal')
    experiment_extra['Emails'] = [[]]
    labelEmailinfo.configure(text = 'Optional: Data will be send via email at the end of the experiment')
    if not email_check:
        confirm_emailadress()
        labelEmailinfo.configure(text = 'Email function not in use. Connection could not be made.')

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
    tab_control.tab(tab_NMRGPC_Setup, state = 'disabled')
    tab_control.tab(tab_NMRGPC_Timesweeps, state = 'disabled')
    tab_control.tab(tab_NMRGPC_Initialisation, state = 'disabled')

def HelpPss():
    tab_control.tab(tab_Pss_help, state = 'normal')
    tab_control.select(tab_Pss_help)
    tab_control.tab(tab_NMRGPC_Setup, state = 'disabled')
    tab_control.tab(tab_NMRGPC_Timesweeps, state = 'disabled')
    tab_control.tab(tab_NMRGPC_Initialisation, state = 'disabled')

def HelpSpinsolve():
    tab_control.tab(tab_Spinsolve_help, state = 'normal')
    tab_control.select(tab_Spinsolve_help)
    tab_control.tab(tab_NMRGPC_Setup, state = 'disabled')
    tab_control.tab(tab_NMRGPC_Timesweeps, state = 'disabled')
    tab_control.tab(tab_NMRGPC_Initialisation, state = 'disabled')


def confirm_code ():
    '''
    Extracts code from entry field and writes it in temporary text file (as 'Code,,code') in Communication folder. Can now be read by LabView.
    '''
    global code
    code = code_en.get()
    code_en.configure(state = 'readonly')
    NMRGPC_confirm_code.configure(state = 'disabled')

    with open(Temporary_textfile,"a") as f:
        f.write('Code,,')
        f.write(code)
        f.close()

    logger.info('Code ({}) and timesweep parameters are communicated to LabVIEW software'.format(code))

    experiment_extra.loc[0, 'code'] = code

    labelLabview.configure(text = 'Open the LabVIEW and start running the software.')
    confirmLabview.configure(state = 'normal')
    HelpLabview.configure(state = 'normal')
    return code
    
code_lbl = Label(NMRGPC_parameter_frame_init, text = 'Experiment Code', bg = 'gray', width = 15, font=FONTS['FONT_NORMAL'])
code_lbl.grid(row =3, column =0)

code_en = Entry(NMRGPC_parameter_frame_init, font= FONTS['FONT_ENTRY'], width = 30)
code_en.grid(row =3, column =1)
    
#ok Button for code
NMRGPC_confirm_code = Button(NMRGPC_parameter_frame_init, text ='OK', font= FONTS['FONT_BOTTON'], command = confirm_code, width = 6)
NMRGPC_confirm_code.grid(row =4, column =1, columnspan = 2)
    
labelLabview = Label(NMRGPC_parameter_frame_init, text = 'LABVIEW', font= FONTS['FONT_NORMAL'], bg= 'gray')
labelLabview.grid(row =5, column = 0, columnspan =2)
confirmLabview = Button(NMRGPC_parameter_frame_init, text = 'OK', font = FONTS['FONT_BOTTON'], command = confirmLabview, state = 'disabled', width = 6)
confirmLabview.grid(row = 5, column = 3)
HelpLabview = Button(NMRGPC_parameter_frame_init, text = 'Help', font = FONTS['FONT_BOTTON'], state = 'disabled', command = HelpLabView, width = 6)
HelpLabview.grid(row = 5, column = 4)
labelLabviewInfo = Label(NMRGPC_parameter_frame_init, text = '', font = FONTS['FONT_SMALL'], bg= 'gray')
labelLabviewInfo.grid(row = 6, column = 0, columnspan= 2)

labelPss = Label(NMRGPC_parameter_frame_init, text = 'PSS', font= FONTS['FONT_NORMAL'], bg= 'gray')
labelPss.grid(row =7, column = 0, columnspan =2)
confirmPss = Button(NMRGPC_parameter_frame_init, text = 'OK', font = FONTS['FONT_BOTTON'], state= 'disabled', command = confirmPss, width = 6)
confirmPss.grid(row = 7, column = 3)
HelpPss = Button(NMRGPC_parameter_frame_init, text = 'Help', font = FONTS['FONT_BOTTON'], state = 'disabled', command = HelpPss, width = 6)
HelpPss.grid(row = 7, column = 4)
labelPssInfo = Label(NMRGPC_parameter_frame_init, text = '', font = FONTS['FONT_SMALL'], bg= 'gray')
labelPssInfo.grid(row = 8, column = 0, columnspan= 2)

labelSpinsolve = Label(NMRGPC_parameter_frame_init, text = 'Spinsolve', font= FONTS['FONT_NORMAL'], bg= 'gray')
labelSpinsolve.grid(row =9, column = 0, columnspan =2)
confirmSpinsolve = Button(NMRGPC_parameter_frame_init, text = 'OK', font = FONTS['FONT_BOTTON'], state = 'disabled', command = confirmSpinsolve, width = 6)
confirmSpinsolve.grid(row = 9, column = 3)
HelpSpinsolve = Button(NMRGPC_parameter_frame_init, text = 'Help', font = FONTS['FONT_BOTTON'], state = 'disabled', command = HelpSpinsolve, width = 6)
HelpSpinsolve.grid(row = 9, column = 4)
labelSpinsolveInfo = Label(NMRGPC_parameter_frame_init, text = '', font = FONTS['FONT_SMALL'], bg= 'gray')
labelSpinsolveInfo.grid(row = 10, column = 0, columnspan= 2)

labelEmail= Label(NMRGPC_parameter_frame_init, text = 'Email', font= FONTS['FONT_NORMAL'], bg= 'gray')
labelEmail.grid(row =11, column = 0, columnspan =1)
entryEmail= Entry(NMRGPC_parameter_frame_init, text = 'Email', font= FONTS['FONT_SMALL'], state = 'readonly', width = 30)
entryEmail.grid(row =11, column = 1, columnspan =1)
confirmEmail = Button(NMRGPC_parameter_frame_init, text = 'Confirm', font = FONTS['FONT_BOTTON'], state = 'disabled', command = confirm_emailadress, width = 6)
confirmEmail.grid(row = 11, column = 3)
AddEmail = Button(NMRGPC_parameter_frame_init, text = 'Add', font = FONTS['FONT_BOTTON'], state = 'disabled', command = add_emailadress, width = 6)
AddEmail.grid(row = 11, column = 4)
labelEmailinfo = Label(NMRGPC_parameter_frame_init, text = '', font = FONTS['FONT_SMALL'], bg= 'gray')
labelEmailinfo.grid(row = 12, column = 0, columnspan= 2)

def startexp():
    root.destroy()

    startfile = open(Temporary_textfile, 'w') 
    startfile.write('start')
    startfile.close()

    logger.info('Experiment started by operator. Start sign is communicated to LabView.')

    starting(ExperimentFolder)

start_btn = Button(NMRGPC_btm_frame_init, text ='Start', font = FONTS['FONT_HEADER_BOLD'] ,state = 'disabled', command = startexp)
start_btn.grid()

#Make-up page
top_frame_exp = Frame(tab_overview, bg='white', width=1000, height=50, pady=3, padx = 400)
parameter_frame_exp = Frame(tab_overview, bg='gray', width=1000, height=350, pady=3)
top_frame_exp.grid(row=0, sticky="ew")
parameter_frame_exp.grid(row=1, sticky="ew")

#Make-Up Top Frame in exp Tab
name_window_exp = Label(top_frame_exp, text= 'Experiment',bg='white', font = FONTS['FONT_HEADER'])
name_window_exp.grid()
tab_control.grid()
root.mainloop()