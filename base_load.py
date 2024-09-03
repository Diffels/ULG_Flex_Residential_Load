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
import random
def occ_reshape(occ: np.ndarray, ts: float)->np.ndarray:
    '''
    Function that reshape occupancy profile:
        1. Make it boolean. (1: Active, 2: Sleeping)-> 1: At Home; (3: Not at home)-> 0: Not at home
        2. From 10-min time step into 1-min time step. 
    Inputs
        - occ: former occupancy profile
        - ts: simulation time step [min]
    Outputs
        - new_occ: reshaped new occupancy profile
    '''
    nTS = len(occ) 

    new_occ=np.zeros((nTS-1)*ts)
    # Repeat each occupancy value to match the new resolution
    expanded_occ = np.repeat(occ[:-1], ts)
    # Apply the condition to determine whether the driver is home or not.
    new_occ = np.where(np.isin(expanded_occ, [1, 2]), 1, 0)
    
    return new_occ

def get_inputs():
    '''
    Function that reads the Excel file Config.xlsx containing all necessary inputs for the simulation. 
    '''
    # Reading the input file in current directory
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Config.xlsx")
    out,config_full = read_config(file_path)
    # Appliances instances definition
    dwelling_compo = []
    for i in range(out['dwelling']['nb_compo']):
        dwelling_compo.append(out['dwelling'][f'member{i+1}'])

    '''Create a dictionnary config containing whole simulation configuration'''
    config = {  
                'nb_days': out['sim']['ndays'],                 # Number of days to simulate
                'year': out['sim']['year'],                     # Year of the simulation
                'nb_Scenarios': out['sim']['N'],                # Number of Scenarios
                'ts': out['sim']['ts'],                         # Time Step resolution [min]
                'start_day': out['sim']['start_day'],           # Starting day of the simulation (/!\ start_day+nb_days<365 or 366 if leap.)
                'country': out['sim']['country'],               # Associated country

                'appliances': out['equipment'],                 #

                'flex_mode': out['flex']['type'],               #
                'flex_rate': out['flex']['rate'],               #

                # EV Parameters
                'EV_presence': out['EV']['present'],            # If a EV is present or not.
                'prob_EV_size': [float(prob) for prob in out['EV']['size'].split(',')],                   # EV size prob:  ['large', 'medium', 'small']
                'prob_EV_usage': [float(prob) for prob in out['EV']['usage'].split(',')],                 # EV usage prob: ['short', 'normal', 'long']
                'prob_EV_charger_power': [float(prob) for prob in out['EV']['charger_power'].split(',')], # Power charger station prob: [3.7, 7.4, 11, 22] (kW) 
                'EV_km_per_year': out['EV']['km_per_year']      # Km/y, if 0 does not take into account
                
            }
    
    if out['plt']['plot'] == "True":
        config['Plot'] =True
    else:
        config['Plot'] = False

    if sum(config['prob_EV_size']) != 1: 
        raise ValueError(f"Probabilities associated to the EV size are incorrect. {config['prob_EV_size']}")
    if sum(config['prob_EV_usage']) != 1 and config['EV_km_per_year'] == 0: 
        raise ValueError(f"Probabilities associated to the EV usage are incorrect. {config['prob_EV_usage']}")
    if sum(config['prob_EV_charger_power']) != 1: 
        raise ValueError(f"Probabilities associated to the charger powers are incorrect. {config['prob_EV_charger_power']}")
    
    
    return config, dwelling_compo


def get_profiles(config, dwelling_compo):
    '''
    Function that computes the different load profiles.

    Inputs:
        - config (dict): dictionnay that contains all the inputs defined in Config.xlsx
        - dwelling_compo (list): list containing the dwelling composition 
    
    It returns the load profiles (dataframe) and the execution time.        
    '''
    times = np.zeros(config['nb_Scenarios'])

    nminutes = config['nb_days'] * 1440 + 1
    P = np.zeros((config['nb_Scenarios'], nminutes))
    for i in range(config['nb_Scenarios']):
        start_time = time.time()
        family = Household_mod(f"Scenario {i}",members = dwelling_compo, selected_appliances = config['appliances']) # print put in com 
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
        if pd.notna(config['flex_mode']) : 
            flex_window = flexibility_window(df[config['appliances'].keys()], family.occ_m, config['flex_mode'], flexibility_rate= config['flex_rate'])
        if config['EV_presence']/100 >= random.random():
            # Reshaping of occupancy profile 
            occupancy = occ_reshape(family.occ_m, config['ts'])
            # Determining EV parameter:
            sizes=['small', 'medium', 'large']
            config['EV_size'] = np.random.choice(sizes, p=config['prob_EV_size'])
            usages=['short', 'normal', 'long']
            config['EV_usage'] =  np.random.choice(usages, p=config['prob_EV_size'])
            powers=[3.7, 7.4, 11, 22] #kW
            config['EV_charger_power'] =  np.random.choice(powers, p=config['prob_EV_charger_power'])
            # Running EV module
            load_profile=EV_run(occupancy,config)
            EV_profile = pd.DataFrame({'EVCharging':load_profile})
            EV_flex = pd.DataFrame({'EVCharging':load_profile, 'Occupancy':occupancy})

            if 'EVCharging' not in df.columns:
                df['EVCharging'] =  EV_profile*1000
            else :
                df['EVCharging'] = df['EVCharging'] + EV_profile['EVCharging']*1000
        
        P[i,:] = family.P
        end_time = time.time()
        execution_time = end_time - start_time
        times[i] = execution_time
        print(f"Simulation {i+1}/{config['nb_Scenarios']} is done. Execution time: {execution_time} s.") 

    P = np.array(P)
    
    total_elec = np.sum(P)
    average_total_elec = total_elec/config['nb_Scenarios']
    
    #df = df/config['nb_Scenarios']

    df = index_to_datetime(df, config['year'],config['ts'])
    
    return average_total_elec.sum()/60/1000, times, df

import datetime as dt

def index_to_datetime(df, year, ts):
    init_date = dt.datetime(year, 1,1,0,0)
    dates = []
    for i in range(len(df)):
        dates.append(init_date+dt.timedelta(minutes=i))
    df['DateTime'] = dates
    df = df.set_index('DateTime')
    df10min = df.resample(str(ts)+'min').mean()
    return df10min
