import pandas as pd
import os

# List of list with entry values for GUI
# [entry (for entry field) , default, parameter name, unit, default value, change (for button)]
SETUP_DEFAULT_VALUES_NMR = [['entry1', 'default1', 'Reactor Volume', 'mL', 0.90, 'change1'],
            ['entry2', 'default2', 'Dead Volume 1', 'mL', 0.32,'change2' ],
            ['entry3', 'default3', 'Dead Volume 2', 'mL', 0.17 ,'change3'],
            ['entry4', 'default4', 'Dead Volume 3', 'mL', 0.17 ,'change4'],
            ['entry5', 'default5', 'NMR Interval', 'sec', 17 ,'change5'],
            ['entry6', 'default6', 'GPC Interval', 'minutes', 3 ,'change6'],
            ['entry7', 'default7', 'Stabilization factor', 'x', 1.3,'change7'],
            ['entry8', 'default8', 'Dilution Flowrate', 'mL/min', 1.5,'change8']]

FONTS = {'FONT_NORMAL':('Ariel', 15),
    'FONT_HEADER' : ('Courier',30),
    'FONT_BOTTON' : ('Ariel', 10),
    'FONT_HEADER_BOLD' : ('Ariel', 18, 'bold'),
    'FONT_ENTRY': ('Ariel', 17),
    'FONT_SMALL' : ('Ariel', 10),
    'FONT_SMALL_BOLD' : ('Ariel', 10, 'bold')}

col_names = ['Start_min','Stop_min', 'Volume', 'StartFR','StopFR', 'StabilisationTime', 'DeadVolume1', 'DeadVolume2', 'DeadVolume3','NMRInterval','GPCInterval' ,'DilutionFR', 'DeadVolume1(min)', 'DeadVolume2(min)', 'DeadVolume3(min)' , 'Mode']
TIMESWEEP_PARAMETERS = pd.DataFrame(columns = col_names)

DRIVE = 'S'
FOLDERS = {'COMMUNICATION': os.path.join(os.path.dirname(os.getcwd()),'CommunicationFolder'),
            'GPC' : '{}:/Sci-Chem/PRD/GPC 112/2018-March/Projects'.format(DRIVE),
            'NMR' : 'C:/PROJECTS/DATA'}