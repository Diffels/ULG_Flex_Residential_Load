# -*- coding: utf-8 -*-
"""
@authors: duchmax, noedi
    
August 2024
"""

# Import required modules
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from Household_mod import Household_mod
from plots import make_demand_plot
from read_config import read_config
from Flexibility import flexibility_window
from ramp_mobility.EV_run import EV_run
import time

def occ_reshape(occ: np.ndarray, ts: float)->np.ndarray:
    '''
    Function that reshape occupancy profile:
        1. Make it boolean. (1: Active, 2: Sleeping)-> 1: At Home; (3: Not at home)-> 0: Not at home
        2. From 10-min time step into 1-min time step. 
    Inputs
        - occ: former occupancy profile
        - ts: simulation time step [h]
    Outputs
        - new_occ: reshaped new occupancy profile
    '''
    nTS = len(occ) 
    #TODO
    #prevTS=round(ts*60) # Previous Time Step in [min]
    prevTS=10

    new_occ=np.zeros((nTS-1)*prevTS)
    # Repeat each occupancy value to match the new resolution
    expanded_occ = np.repeat(occ[:-1], prevTS)
    # Apply the condition to determine whether the driver is home or not.
    new_occ = np.where(np.isin(expanded_occ, [1, 2]), 1, 0)
    
    return new_occ

def get_inputs():
        # Reading the input file in current directory
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Config.xlsx")
    out,config_full = read_config(file_path)
    # Appliances instances definition
    dwelling_compo = []
    for i in range(out['dwelling']['nb_compo']):
        dwelling_compo.append(out['dwelling'][f'member{i+1}'])

    appliances = [x for x in out['equipment'].keys() if out['equipment'][x] == True]

    '''Create a dictionnary config containing whole simulation configuration'''
    config = {  
                'nb_days': out['sim']['ndays'],             # Number of days to simulate
                'year': out['sim']['year'],                 # Year of the simulation
                'nb_Scenarios': out['sim']['N'],            # Number of Scenarios
                'ts': out['sim']['ts'],                     # Time Step resolution [h]
                'start_day': out['sim']['start_day'],       # Starting day of the simulation (/!\ start_day+nb_days<365 or 366 if leap.)
                'country': out['sim']['country'],         # Associated country

                'appliances': appliances,                   #

                'flex_mode': out['flex']['type'],           #
                'flex_rate': out['flex']['rate'],           #

                # EV Parameters
                'EV_presence': out['EV']['present'],        # If a EV is present or not.
                'EV_size': out['EV']['size'],               # EV size:  ['large', 'medium', 'small']
                'EV_disp': False, #out['EV']['disp'],       #TODO Flag for displaying some useful information regarding EV profile simulation.
                'EV_usage': 'normal', #out['EV']['usage']   #TODO ['short', 'normal', 'long']
                'EV_charger_power': 3.7, #out['EV']['usage] #TODO un float en kW
                'User_list': [],                            # List containing all users.

                'Plot' : out['plt']['plot']
            }
    return config, dwelling_compo, appliances
'''
CREATE FUNCTION THEN CREATE FILE main.py THAT CALLS IT?
'''
def get_profiles(config, dwelling_compo, appliances):
    '''
    [...] Summary [...]
    Inputs
        - 
    Outputs
        -
    '''
    times = np.zeros(config['nb_Scenarios'])

    nminutes = config['nb_days'] * 1440 + 1
    P = np.zeros((config['nb_Scenarios'], nminutes))
    for i in range(config['nb_Scenarios']):
        start_time = time.time()
        family = Household_mod(f"Scenario {i}",members = dwelling_compo, selected_appliances = appliances) # print put in com 
        #family = Household_mod(f"Scenario {i}")
        family.simulate(year = config['year'], ndays = config['nb_days']) # print in com
        if i == 0:
            df = pd.DataFrame(family.app_consumption)
        else : 
            for key, value in family.app_consumption.items():
                if key in df.columns:
                    df[key] += value
                else :
                    df[key] = value
        if pd.notna(config['flex_mode']) and appliances: 
            flex_window = flexibility_window(df[appliances], family.occ_m, config['flex_mode'], flexibility_rate= config['flex_rate'])
        
        if config['EV_presence'] == 'Yes':
            # Reshaping of occupancy profile 
            occupancy = occ_reshape(family.occ_m, config['ts'])
            print(occupancy[0])
            # Running EV module
            EV_profile=EV_run(occupancy,config)

        P[i,:] = family.P
        end_time = time.time()
        execution_time = end_time - start_time
        times[i]=execution_time
        print(f"Simulation {i+1}/{config['nb_Scenarios']} is done. Execution time: {execution_time} s.") 

    P = np.array(P)
    df = df.drop(df.index[-1])
    df['EVCharging'] = EV_profile*1000
    total_elec = np.sum(P)
    average_total_elec = total_elec/config['nb_Scenarios']
    df = df/config['nb_Scenarios']

    return average_total_elec.sum()/60/1000, times, df

if __name__ == '__main__':
    pass