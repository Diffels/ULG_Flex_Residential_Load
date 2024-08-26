# -*- coding: utf-8 -*-
"""
@author: noedi

August 2024
"""

# Import required modules
from EV_run import EV_run
import pandas as pd
import numpy as np

''' CONFIGURATION '''

config = {
    'full_year': True,    # True: Sim for whole year; False: Sim for one day.    
    'countries': ['BE'],  # Associated country
    'year': 2025,         # Associated year
    'plot_frame': 1440*5, # Window for plotting the profile. Set to 0 to avoid plot.
    'statut': 'student',  # Working Statut: ['working', 'student', 'inactive']
    'car': 'medium',      # EV size:  ['large', 'medium', 'small']
    'day_type': 'weekday',# Day type: ['weekday', 'saturday', 'sunday'] for single day sim. Holiday is considered as sunday.
    'day_period': 'main', # Period of the day: ['main', 'free time']
    'func': 'business',   # Car type: ['business', 'personal'] corresp. to column in t_func.csv
    'tot_users': 1,       # Number of user to define. For this model=1.
    'User_list': [],      # List containing all users.
    'file_path': 'occupancy_profile_full_year.xlsx' # Data file containing occupancy profile.
}

# 10 min Time Step
df_occ_10min = pd.read_excel(config['file_path'])
Driver_occ_10min = df_occ_10min['Merged']
# 1 min Time Step
nTS = len(Driver_occ_10min)
fileTS=10
if not config['full_year'] and nTS > 144:
    raise ValueError("Occupancy file larger than one day. Declare full_year as True.")
    
Driver_athome=np.zeros((nTS-1)*fileTS)

# Repeat each occupancy value 10 times to match the 1-min resolution
expanded_occ = np.repeat(Driver_occ_10min[:-1], fileTS)
# Apply the condition to determine whether the driver is home or not.
# 1: Active; 2: Sleeping; 3: Not at home
Driver_athome = np.where(np.isin(expanded_occ, [1, 2]), 1, 0)

EV_run(Driver_athome, config)