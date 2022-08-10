import math
import pandas as pd
from code_extra.log_method import setup_logger

logger = setup_logger('CalculateScans')

def CalculateNumberOfScans(volume: float, flowrate:float, nmr_interval:float) -> int:
    '''
    Calculates the number of scans based on volume, flowrate and nmr_interval
    '''
    time = volume / flowrate            # time to pass volume in min (mL / (mL/min))
    n = int((time*60) / nmr_interval)   # amount of scans per given time (time in seconds / nmr_interval in seconds)
    return n

def CalculateNumberOfInjections(stop_min:float, GPC_interval_sec:float) -> int:
    '''Calculates the number of injections for a timesweep based on timesweep to_min and GPC interval (sec)'''
    time_sec = stop_min * 60
    max_injections = math.ceil((time_sec / GPC_interval_sec))
    logger.debug('The timesweep to {} min (= {} sec) will have {} (+1 at start) GPC injections at a GPC interval of {} min.'.format(stop_min, time_sec, max_injections, GPC_interval_sec/60))
    
    return max_injections

def _calculate_reactiontimes(stop_min:float, GPC_interval:float, scans:int) -> list:
    '''Calculates the reaction times of the GPC injections'''
    list_of_injections = []
    for i in range(scans):
        list_of_injections.append(i*GPC_interval)
    list_of_injections.append(stop_min*60) #adds last one
    logger.debug('Reaction times (sec) of injections ({} in total): {}'.format(len(list_of_injections), list_of_injections))
    return list_of_injections

def _calculate_restimes (start_min, stop_min, reactiontimes, volume, mode = 'NMR', info = False):
    f1 = volume/start_min
    f2 = volume/stop_min
    
    tres_times = []
    for treaction in reactiontimes:
        tres = round((( volume / f1 ) + (treaction * (1 - (f2 / f1)))/60), 4)
        tres_times.append(tres)
    
    if info:
        print('{}: The residence times (total of {}): \n\t{}'.format(mode, len(tres_times), tres_times))
    
    return tres_times



def GPCinjections(volume, start_min, stop_min, NMR_interval, GPC_interval, GPC_injections_dict):
    '''delete?'''
    n_scans_nmr =_ScansForStabilisation(stop_min, NMR_interval, volume, info = False)
    reaction_times_nmr =_calculate_reactiontimes(stop_min, NMR_interval, n_scans_nmr, info = False)
    tres_times_nmr = _calculate_restimes(start_min, stop_min, reaction_times_nmr, volume)

    n_scans_gpc =_ScansForStabilisation(stop_min, GPC_interval*60, volume, mode = 'GPC', info=False)
    reaction_times_gpc =_calculate_reactiontimes(stop_min, GPC_interval*60, n_scans_gpc, mode = 'GPC', info = False)
    tres_times_gpc = _calculate_restimes(start_min, stop_min, reaction_times_gpc, volume, mode = 'GPC', info= False)

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

  

def CalculateScans(dataframe_experiment: pd.DataFrame, mode = 'NMR')-> pd.DataFrame:
    '''
    Calculates the scan numbers from the parameters file.

    Parameters:
    -----------
    dataframe_experiment: pd.DataFrame
        pandas dataframe with paramters of experiment
    mode: str
        mode of operation, NMR (default) or GPCandNMR 
    
    Returns
    --------
    overviewscansDF: pd.DataFrame
        dataframe with the start and stop scans of the experiment
    
    '''
    overviewscansDF = pd.DataFrame()

    #data acquisition starts after stabilization, so does the calculations
    scan = 0
    startscanGPC = 0
    
    #loops over every timesweep
    for ts in range((dataframe_experiment.shape[0])): #number of timesweeps (zero-indexed)
        logger.debug('Timesweep {}'.format(ts+1))
        volume, stopflowrate, dilutionFR, Vdead1, Vdead2, Vdead3, NMRinterval, GPCinterval, to_min = dataframe_experiment.loc[ts, ['Volume', 'StopFR', 'DilutionFR','DeadVolume1', 'DeadVolume2', 'DeadVolume3', 'NMRInterval', 'GPCInterval', 'Stop_min']]
        
        overviewscansDF.loc[ts, 'Start entry'] = scan
        startscanGPC = scan 
        
        scans_of_deadvolume1 = CalculateNumberOfScans(Vdead1, stopflowrate, NMRinterval) # number of scans for dead volume 1
        start_scan = scan
        scan = start_scan + scans_of_deadvolume1 #new scan number
        logger.debug('Dead Volume 1 ({} mL) at flowrate {} mL/min takes {} scans (NMR interval of {} sec); from scan {} to scan {}.'.format(Vdead1, stopflowrate, scans_of_deadvolume1, NMRinterval, start_scan, scan))
        overviewscansDF.loc[ts, 'Start Scan NMR'] = scan
        
        scans_of_reactor = CalculateNumberOfScans(volume, stopflowrate, NMRinterval)
        start_scan = scan
        scan = start_scan + scans_of_reactor + 1 #zero including
        overviewscansDF.loc[ts, 'Stop Scan NMR'] = scan
        logger.debug('Reactor volume ({} mL) at flowrate {} mL/min takes {} scans (NMR interval of {} sec); from scan {} to scan {}.'.format(volume, stopflowrate, scans_of_reactor, NMRinterval, start_scan, scan))

        if mode == "GPCandNMR":
            logger.debug('Mode Of Operation: {}'.format(mode))

            scans_of_deadvolume1_and_2 = CalculateNumberOfScans(Vdead1+Vdead2, stopflowrate, NMRinterval)
            scans_of_deadvolume3 = CalculateNumberOfScans(Vdead3, dilutionFR, NMRinterval)
            scanGPC = startscanGPC + scans_of_deadvolume1_and_2 + scans_of_deadvolume3
            overviewscansDF.loc[ts, 'Start Scan GPC'] = scanGPC

            logger.debug('Dead Volume 1 and 2 ({} mL + {} mL = {} mL) at flowrate {} mL/min PLUS Dead Volume 3 ({} mL) at dilution flowrate {} mL/min takes {} scans (NMR interval of {} sec); from scan {} to scan {}.'.format(Vdead1, Vdead2, Vdead1+Vdead2, stopflowrate, Vdead3, dilutionFR, scans_of_reactor, NMRinterval, startscanGPC, scanGPC))
            
            number_of_injections = CalculateNumberOfInjections(to_min, GPCinterval*60)
            injections = _calculate_reactiontimes(to_min, GPCinterval*60, number_of_injections)

            GPCsamples = int(len(injections))

            time = (GPCsamples -1) *GPCinterval #corrected time for GPC timesweep (minus one because one at the beginning of the timesweep)
            scansGPCtimesweep = int(time*(60/NMRinterval)) #amount of scans for the timesweep
            stopGPC = scanGPC + scansGPCtimesweep
            logger.debug('GPC Timesweep ({} min; {} injections) takes {} scans (NMR interval of {} sec); from scan {} to scan {}.'.format(time, GPCsamples, scansGPCtimesweep, NMRinterval, scanGPC, stopGPC))
            
            overviewscansDF.loc[ts, 'Stop Scan GPC'] = int(stopGPC)
            overviewscansDF.loc[ts, 'GPC Samples'] =  int(GPCsamples)
            scan = stopGPC +1 #new start scan
        
        else:
            overviewscansDF.loc[ts, 'Start Scan GPC'] = 'N.A.'
            overviewscansDF.loc[ts, 'Stop Scan GPC'] = 'N.A.'
            scan +=1

    logger.info('OverviewScansDF:\n{}'.format(overviewscansDF))
    return overviewscansDF
    
    