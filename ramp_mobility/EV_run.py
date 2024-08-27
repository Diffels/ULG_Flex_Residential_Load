# -*- coding: utf-8 -*-
"""
@author: noedi
    
August 2024
"""

# Import required modules
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from ramp_mobility.EV_stoch_cons import EV_stoch_cons
from ramp_mobility.EV_occ_daily_profile import EV_occ_daily_profile
from ramp_mobility.config_init_ import config_init_
from typing import Any



def EV_run(occupancy: np.ndarray[Any, np.dtype[np.bool_]], config: dict)-> pd.DataFrame:
    '''
    Code based on ramp-mobility library that compute stochastic Electrical 
    Vehicle load profile for predefined types of user, on yearly or daily basis.
    The profile is sctochastically linked to an occupancy behaviour in 
    EV_occ_daily_profile.py and from a stochastic EV consumption given by ramp-mobility
    in EV_stoch_cons.py. 

    The config variable is a dictionnary containing whole configuration used in the simulation. 
    config = {'nb_days'-'start_day'-'countries'-'year'-'EV_disp'-'statut'-'working'-'car'
            'day_type'-'day_period'-'main'-'func'-'tot_users'-'User_list'}

    Please refer to the file main.py/base_load.py for further explanations.
    '''

    '''CONFIGURATION'''
    nb_days = config['nb_days']
    start_day = config['start_day']
    countries = config['country']
    year = config['year']
    EV_disp = config['EV_disp']
    statut = config['EV_statut']
    car = config['EV_size']
    day_period = 'main' # default
    func = 'personal'   # default
    tot_users = config['EV_nb_drivers']
    User_list = config['User_list']
    
    for c in countries:
        if c != 'BE': raise ValueError("Model is currently only working for Belgium.")
        
        User_list = config_init_(statut, car, day_period, func, tot_users, User_list, nb_days, year=year)
    
        EV_cons = EV_stoch_cons(User_list, nb_days, year=year, country=c, disp=EV_disp, start_day=start_day)
        
        SOC, bin_charg, EV_refilled, load_profile = EV_occ_daily_profile(EV_cons, occupancy, SOC_init=0.9, disp=EV_disp)
        
        df_load_profile = pd.DataFrame(load_profile)
        df_load_profile.to_excel('EV_load_profile.xlsx', index=False)

    return df_load_profile  
    