# -*- coding: utf-8 -*-
"""
@author: noedi
    
August 2024
"""

# Import required modules
import pandas as pd
import matplotlib.pyplot as plt

from EV_stoch_cons import EV_stoch_cons
from EV_occ_daily_profile import EV_occ_daily_profile
from config_init_ import config_init_

'''
Code based on ramp-mobility library that compute stochastic Electrical 
Vehicle load profile for predefined types of user, on yearly or daily basis.
The profile is sctochastically linked to an occupancy behaviour in 
EV_occ_daily_profile.py and from a stochastic EV consumption given by ramp-mobility
in EV_stoch_cons.py. 

The config variable is a dictionnary containing whole configuration used in the simulation. 
config = {'full_year'-'countries'-'year'-'plot_frame'-'statut'-'working'-'car'
          'day_type'-'day_period'-'main'-'func'-'tot_users'-'User_list'-'file_path'}

Please refer to the file main.py for further explanations.
'''

def EV_run(occupancy, config):
    
    '''CONFIGURATION'''
    full_year = config['full_year']
    countries = config['countries']
    year = config['year']
    plot_frame = config['plot_frame']
    statut = config['statut']
    car = config['car']
    day_type = config['day_type']
    day_period = config['day_period']
    func = config['func']
    tot_users = config['tot_users']
    User_list = config['User_list']
    
    for c in countries:
        if c != 'BE': raise ValueError("Model is currently only working for Belgium.")
                    
        User_list = config_init_(statut, car, day_period, func, tot_users, User_list, full_year, year=year)
    
        EV_cons = EV_stoch_cons(User_list, full_year, year=year, country=c, day_type=day_type, disp=False)
        
        SOC, bin_charg, EV_refilled, load_profile = EV_occ_daily_profile(EV_cons, occupancy, SOC_init=0.9, disp=True)
        
        df_load_profile = pd.DataFrame(load_profile)
        df_load_profile.to_excel('EV_load_profile.xlsx', index=False)
        
        if plot_frame:
            if not full_year: 
                plot_frame=1440-1
            x_axis=range(plot_frame)
            #plt.plot(x_axis, Driver_athome, color='tab:blue', label='Occupancy')
            plt.plot(x_axis, load_profile[0:plot_frame], color='tab:green', alpha=0.6, label='SOC')
            plt.plot(x_axis, EV_refilled[0:plot_frame], color='tab:red', alpha=0.6, label='Battery Refilled')
            plt.title("Occupancy and State of Charge.")
            plt.yticks([0.0, 0.25, 0.5, 0.75, 0.9, 1.0])
            plt.xlabel("Time [min]")
            plt.legend()
            plt.grid(True)
            #plt.savefig("SOC_plot.svg")
            plt.show()  
    