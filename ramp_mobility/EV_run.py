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
    country = config['country']
    year = config['year']
    car = config['EV_size']
    usage = config['EV_usage']
    charger_pow = config['EV_charger_power'] 
    
    Driver = config_init_(car, usage, country)

    EV_cons, EV_dist, EV_time = EV_stoch_cons(Driver, nb_days, year=year, country=country, start_day=start_day)

    SOC, bin_charg, EV_refilled, load_profile = EV_occ_daily_profile(EV_cons, occupancy, Driver, charger_pow, SOC_init=0.9)
    
    df_load_profile = pd.DataFrame({'EVCharging' :load_profile})
    df_load_profile.to_excel('EV_load_profile.xlsx', index=False)

    return df_load_profile  
    