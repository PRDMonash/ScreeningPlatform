from time import time
import pandas as pd
import os
from code_extra.log_method import setup_logger
import math

logger = setup_logger('Experiment DF')

class ExperimentDF():
    def __init__(self, path_csv) -> None:
        if not os.path.exists(os.path.dirname(path_csv)):
            logger.warning('{} does not exists, cannot make experiment DF'.format(os.path.dirname(path_csv)))
        logger.info('ExperimentDF object created for {}'.format(path_csv))
        self.path_csv = path_csv

    def __DF_to_dict(self, df):
        diction = {}
        for entry in range(len(df)):
            entry_dic = {}
            for column in df.columns:
                entry_dic.update({column:df.iloc[entry][column]})
            diction.update({entry:entry_dic})
        return diction
    def _ScansForStabilisation(self, stop_min, NMR_interval, volume, mode = 'NMR', info = False):
        time_sec = stop_min * 60
        max_scans = math.ceil((time_sec / NMR_interval))
        scans = 'scans'
        if mode == 'GPC':
            scans = 'injections'

        if info:
            print('{}: Stalizing a reactor of {}mL at tres of {} will take {} {} (for a {} sec interval)'.format(mode, volume, stop_min, max_scans,scans, NMR_interval))
        return max_scans
    
    def _calculate_reactiontimes(self, stop_min, NMR_interval, scans, mode = 'NMR', info = False):
        l = []
        for i in range(scans):
            l.append(i*NMR_interval)
        l.append(stop_min*60)

        if info:
            print('{}: The reaction times (total of {}): \n\t{}'.format(mode, len(l), l))

        return l
    def _calculate_restimes (eelf, start_min, stop_min, reactiontimes, volume, mode = 'NMR', info = False):
        f1 = volume/start_min
        f2 = volume/stop_min
        
        tres_times = []
        for treaction in reactiontimes:
            tres = round((( volume / f1 ) + (treaction * (1 - (f2 / f1)))/60), 4)
            tres_times.append(tres)
        
        if info:
            print('{}: The residence times (total of {}): \n\t{}'.format(mode, len(tres_times), tres_times))
        
        return tres_times

    def _GPCinjections(self, volume, start_min, stop_min, NMR_interval, GPC_interval, GPC_injections_dict):
        n_scans_nmr = self._ScansForStabilisation(stop_min, NMR_interval, volume, info = False)
        reaction_times_nmr = self._calculate_reactiontimes(stop_min, NMR_interval, n_scans_nmr, info = False)
        tres_times_nmr = self._calculate_restimes(start_min, stop_min, reaction_times_nmr, volume)

        n_scans_gpc = self._ScansForStabilisation(stop_min, GPC_interval*60, volume, mode = 'GPC', info=False)
        reaction_times_gpc = self._calculate_reactiontimes(stop_min, GPC_interval*60, n_scans_gpc, mode = 'GPC', info = False)
        tres_times_gpc = self._calculate_restimes(start_min, stop_min, reaction_times_gpc, volume, mode = 'GPC', info= False)

        sample = (len(GPC_injections_dict)) + 1
                                                                
        for tres_gpc in tres_times_gpc:                                                    # loop over every res time of GPC
            for tres_nmr_index in range(len(tres_times_nmr)):                               # loop over index of res times of NMR and compare
                a, b = float(tres_times_nmr[tres_nmr_index]), float(tres_times_nmr[tres_nmr_index+1])   
                tres_gpc = float(tres_gpc)                                                  # take the two consecutive NMR res
                if tres_gpc > a and tres_gpc < b:                                           # if tres_GPC is between them...
                    if tres_gpc - a > b - tres_gpc:                                         # see which one is closed and define that tres_NMR as tres_GPC
                        tres_df = b                                                         
                    else:
                        tres_df = a
                    #print('{} min: GPC injection ({} min)'.format(tres_df, tres_gpc))
                    GPC_injections_dict.update({sample: [tres_gpc, tres_df]})
                    sample +=1
                    break 
                elif tres_gpc == a:
                    tres_df = a                                                         # if tres_GPC is same as tres_NMR, mostly for first injectoin
                    #print('{} min: GPC injection ({})'.format(tres_df, tres_gpc))
                    GPC_injections_dict.update({sample: [tres_gpc, tres_df]})
                    sample +=1 
                    break
                elif tres_gpc == b: 
                    tres_df = b                                                        # # if tres_GPC is same as tres_NMR, mostly for last injectoin
                    #print('{} min: GPC injection ({})'.format(tres_df, tres_gpc))
                    GPC_injections_dict.update({sample: [tres_gpc, tres_df]})
                    sample +=1
                    break

        return GPC_injections_dict

    def create_experimentDF(self, scans:pd.DataFrame, parameters:pd.DataFrame):
        
        #transform to dictianaries, easier to work with (in my opininon)
        timesweeps = self.__DF_to_dict(parameters)
        scans = self.__DF_to_dict(scans)
        number_of_timesweeps = len(timesweeps)

        mode = timesweeps[0]['Mode']

        # Create list of columns for the Dataframe
        columnsDF = ['Scannumber','Timesweep', 'Status', 'conversion', 'treaction','tres' ]
        nmr_interval = timesweeps[0]['NMRInterval']


        if mode == 'GPCandNMR':
            columnsDF = columnsDF + ['GPC_number', 'Mn', 'Mw', 'D', 'tres_GPC']   # adds the GPC columns

            #convert the tres GPC entry from a string of a list to a proper list
            #experiment DF is as long as the last GPC scan
            gpc_number = 1
            stopScan = 'Stop Scan GPC'

            inj_dict = {}
            volume = timesweeps[0]['Volume']
            nmr_interval = timesweeps[0]['NMRInterval']
            gpc_interval = timesweeps[0]['GPCInterval']

            for i in range(len(timesweeps)):
                start_min = timesweeps[i]['Start_min']
                stop_min = timesweeps[i]['Stop_min']
                inj_dict = self._GPCinjections(volume, start_min, stop_min, nmr_interval, gpc_interval, inj_dict)

        #initialize DataFrame
        experimentDF = pd.DataFrame(columns= columnsDF)

        #starts with first entry of timesweep 
        timesweep_number = 0
        last_stop_scan = int(scans[number_of_timesweeps-1][stopScan])

        for i in range(last_stop_scan):
            
            #adds scan number to DF; if scannumber i > as the last scannumber of the timesweep --> new timesweep entry (by timesweep_number +1)
            experimentDF.loc[i, 'Scannumber'] = int(i)
            if i < scans[timesweep_number][stopScan]:
                pass
            else:
                timesweep_number +=1

            # Adds timesweep number in DF; zero-indexed (so +1)
            experimentDF.loc[i, 'Timesweep'] = timesweep_number +1

            # if scan is between start and stop scan of timesweep --> treat as timesweep data by adding tres (+1 to include Stop Scan NMR)
            if i in range(int(scans[timesweep_number]['Start Scan NMR']), int(scans[timesweep_number]['Stop Scan NMR'])+1):
                
                # Maximum residence time of timesweep is the stop time of the timeswweep
                max_tres = timesweeps[timesweep_number]['Stop_min']
                
                # Status is Timesweep
                experimentDF.loc[i, 'Status'] = 'Timesweep'

                #treaction starts at 0 and adds 1 at end  of loop
                experimentDF.loc[i, 'treaction'] = int(treaction)

                # Extracts values to calculate tres (see 'Rapid Kinetic Screening via Transient Timesweep Experiments in Continuous Flow Reactors' for details on calculations)
                volume = timesweeps[timesweep_number]['Volume']
                f1 = timesweeps[timesweep_number]['StartFR']
                f2 = timesweeps[timesweep_number]['StopFR']
            
                tres = round((( volume / f1 ) + (treaction * (1 - (f2 / f1)))/60), 4)
                
                # If calcuated tres > max tres --> tres is the max tres
                if tres> max_tres:
                    tres = max_tres
                    treaction = int(tres*60)

                # treaction and tres in DF
                experimentDF.loc[i, 'treaction'] = int(treaction)
                experimentDF.loc[i, 'tres'] = tres

                if mode == 'GPCandNMR':
                    #extract the tres of NMR timesweep for the GPC injections
                    tres_GPC = [float(i[1]) for i in list(inj_dict.values())]
                    
                    #if the calculated tres in the list of tres_gpc injections --> GPC data expected; i is still scan number
                    if float(tres) in tres_GPC:
                        for GPC_column in ['Mn', 'Mw', 'D']:
                            experimentDF.loc[i, GPC_column] = 'GPC expected'
                        experimentDF.loc[i, 'GPC_number'] = gpc_number
                        experimentDF.loc[i, 'tres_GPC'] = [float(i[0]) for i in list(inj_dict.values())][gpc_number-1]

                        # For next GPC sample
                        gpc_number +=1 

                # reaction time for next scan
                treaction += nmr_interval

            #if scan not between start scan and stop scan --> status is 'No' and treaction back to 0 for next timesweep
            else:
                experimentDF.loc[i, 'Status'] = 'No'
                treaction = 0

        #Saves DF in software folder
        experimentDF.to_csv(self.path_csv)
        logger.info('Dataframe created and saved as {}'.format(self.path_csv))
        
        return experimentDF