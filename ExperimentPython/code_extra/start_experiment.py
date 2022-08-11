from code_extra.log_method import setup_logger

logger = setup_logger('Start Experiment')

def WaitstabilisationTime():
    '''Calculates stabilisation time (for first timesweep) and waits time (sleep)
    '''
    #extracts StartFR (flowrate from first timesweep), reactor volume and stabilisation factor from parameters dataframe and calculates waiting time
    start, volume, stabilisationfactor = parametersDF.loc[0,'StartFR'], parametersDF.loc[0,'volume'], parametersDF.loc[0,'stabilisation time']
    waiting_time = (volume * stabilisationfactor) / start #in minutes


    logger.info('After stabilisation ({} min), start spinsolve and set the following integration borders in the spectra: {}'.format(waiting_time, experiment_extra.loc[0, 'integrals']))
    
    waiting_timesec= waiting_time *60 #for sleep function!!

def starting(experimentFolder):
    logger.info('Experiment begins!')
    print(experimentFolder)

    