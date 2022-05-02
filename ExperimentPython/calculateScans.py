import math
import pandas as pd


def CalculateNumberOfScans(volume, flowrate, nmr_interval):
    time = volume / flowrate        # time to pass volume in min (mL / (mL/min))
    n = int((time*60) / nmr_interval)    # amount of scans per given time (time in seconds / nmr_interval in seconds)
    return n

def _ScansForStabilisation(stop_min, NMR_interval, volume, mode = 'NMR', info = False):
    time_sec = stop_min * 60
    max_scans = math.ceil((time_sec / NMR_interval))
    scans = 'scans'
    if mode == 'GPC':
        scans = 'injections'

    if info:
        print('{}: Stalizing a reactor of {}mL at tres of {} will take {} {} (for a {} sec interval)'.format(mode, volume, stop_min, max_scans,scans, NMR_interval))
    return max_scans

def _calculate_reactiontimes(stop_min, NMR_interval, scans, mode = 'NMR', info = False):
    l = []
    for i in range(scans):
        l.append(i*NMR_interval)
    l.append(stop_min*60)

    if info:
        print('{}: The reaction times (total of {}): \n\t{}'.format(mode, len(l), l))

    return l

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

'''
overviewscansDF = pd.DataFrame()
VOLUME = 1
NMR_INTERVAL = 15
GPC_INTERVAL = 3 # in min
GPC_injections_dic = {}
timesweeps = {0:[2,5], 1:[5,12], 2:[12,30]}

timesweeps_FR = {i : [VOLUME/j[0], VOLUME/j[1]] for i,j in timesweeps.items()}

Vdead1, Vdead2, Vdead3 = 0.4, 0.26, 0.157
dilutionFR = 1.5
'''

def CalculateScans_test(dataframe_experiment):
    scan = 0
    startscanGPC = 0
    for ts, FRs in timesweeps_FR.items():
        print('\n')
        print('startscan: {}'.format(scan))
        startflowrate, stopflowrate = FRs[0], FRs[1]

        
        overviewscansDF.loc[ts, 'Start entry'] = scan
        startscanGPC = scan
        
        scan = scan + CalculateNumberOfScans(Vdead1, stopflowrate, NMR_INTERVAL)
        overviewscansDF.loc[ts, 'Start Scan NMR'] = scan
        
        scan = scan + CalculateNumberOfScans(VOLUME, stopflowrate, NMR_INTERVAL) + 1 #zero including
        overviewscansDF.loc[ts, 'Stop Scan NMR'] = scan
        print('Stop Scan: {}'.format(scan))

        if mode == "GPCandNMR":
            print('Start scan GPC: {}'.format(startscanGPC))
            scanGPC = startscanGPC + CalculateNumberOfScans(Vdead1+Vdead2, stopflowrate, NMR_INTERVAL) + CalculateNumberOfScans(Vdead3, dilutionFR, NMR_INTERVAL)
            overviewscansDF.loc[ts, 'Start Scan GPC'] = scanGPC

            a = _ScansForStabilisation(VOLUME /stopflowrate, GPC_INTERVAL*60, VOLUME, mode = 'GPC', info = True)
            injections = _calculate_reactiontimes(VOLUME /stopflowrate, GPC_INTERVAL*60, a, mode = 'GPC', info = True)

            GPCsamples = int(len(injections))

            time = (GPCsamples -1) *GPC_INTERVAL #corrected time for GPC timesweep (minus one because one at the beginning of the timesweep)
            scansGPCtimesweep = time*(60/NMR_INTERVAL) #amount of scans for the timesweep
            print(scansGPCtimesweep)
            stopGPC = scanGPC + scansGPCtimesweep

            overviewscansDF.loc[ts, 'Stop Scan GPC'] = stopGPC
            overviewscansDF.loc[ts, 'GPC Samples'] =  GPCsamples
            print(stopGPC)
            scan = stopGPC +1
        
        else:
            overviewscansDF.loc[ts, 'Start Scan GPC'] = 'N.A.'
            print(scan)
            scan +=1

    return overviewscansDF    

def CalculateScans(dataframe_experiment, mode = 'NMR'):
    overviewscansDF = pd.DataFrame()
    scan = 0
    startscanGPC = 0
    for ts in range((dataframe_experiment.shape[0])): #number of timesweeps
        #print('\n')
        volume, stopflowrate, dilutionFR, Vdead1, Vdead2, Vdead3, NMRinterval, GPCinterval, startflowrate = dataframe_experiment.loc[ts, ['volume', 'StopFR', 'Dilution FR','dead volume 1', 'Dead Volume 2', 'Dead Volume 3', 'NMR interval', 'GPC Interval', 'StartFR']]
        #print('startscan: {}'.format(scan))
        
        overviewscansDF.loc[ts, 'Start entry'] = scan
        startscanGPC = scan
        
        scan = scan + CalculateNumberOfScans(Vdead1, stopflowrate, NMRinterval)
        overviewscansDF.loc[ts, 'Start Scan NMR'] = scan
        
        scan = scan + CalculateNumberOfScans(volume, stopflowrate, NMRinterval) + 1 #zero including
        overviewscansDF.loc[ts, 'Stop Scan NMR'] = scan
        #print('Stop Scan: {}'.format(scan))

        if mode == "GPCandNMR":
            print('mode: {}'.format(mode))
            #print('Start scan GPC: {}'.format(startscanGPC))
            scanGPC = startscanGPC + CalculateNumberOfScans(Vdead1+Vdead2, stopflowrate, NMRinterval) + CalculateNumberOfScans(Vdead3, dilutionFR, NMRinterval)
            overviewscansDF.loc[ts, 'Start Scan GPC'] = scanGPC

            a = _ScansForStabilisation(volume /stopflowrate, GPCinterval*60, volume, mode = 'GPC', info = False)
            injections = _calculate_reactiontimes(volume /stopflowrate, GPCinterval*60, a, mode = 'GPC', info = False)

            GPCsamples = int(len(injections))

            time = (GPCsamples -1) *GPCinterval #corrected time for GPC timesweep (minus one because one at the beginning of the timesweep)
            scansGPCtimesweep = int(time*(60/NMRinterval)) #amount of scans for the timesweep
            stopGPC = scanGPC + scansGPCtimesweep
            
            print('stop scan gpc: {}'.format(stopGPC))
            overviewscansDF.loc[ts, 'Stop Scan GPC'] = int(stopGPC)
            overviewscansDF.loc[ts, 'GPC Samples'] =  int(GPCsamples)
            scan = stopGPC +1
        
        else:
            overviewscansDF.loc[ts, 'Start Scan GPC'] = 'N.A.'
            overviewscansDF.loc[ts, 'Stop Scan GPC'] = 'N.A.'
            scan +=1
    print('OverviewScansDF: {}'.format(overviewscansDF))
    return overviewscansDF
    
    
#print(overviewscansDF)
"""
for times in timesweeps.values():
    injections = GPCinjections(VOLUME, times[0], times[1], NMR_INTERVAL, GPC_INTERVAL, GPC_injections_dic)
print(injections)

df = input('>> ')
scans = CalculateScans(df)
"""