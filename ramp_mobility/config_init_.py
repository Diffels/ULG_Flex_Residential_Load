# -*- coding: utf-8 -*-
"""
Imported from ramp-mobility:
    https://github.com/RAMP-project/RAMP-mobility/tree/master
    (previously called ../BE.py)
    
Modified by noedi
August 2024
"""

# Import required libraries
from ramp_mobility.core import User
import numpy as np
import pandas as pd
import copy
import os


'''
File that defines the function used to convert the associated database and parameters into 
python variables for: Belgium. The User and Appliance (EV) are also created according to given arguments.
'''

def config_init_(statut: str, car: str, day_period: str, func: str, tot_users: int, User_list: list, nb_days: int, year=2016)->list:
    
    # Print configuration in the console.
    print("------ EV Configuration ------")
    print("One user was implemented, with the following parameters:")
    print("- Working profile:", statut)
    print("- Car size:", car)
    print("- Day period:", day_period)
    print("- Function:", func)
    print(f"For a {nb_days}-day(s) simulation.\n")
            
    #Define Country
    country = 'BE'
        
    #Variabilities 
    r_w = {}
    
    P_var = 0.1 #random in power
    r_d   = 0.3 #random in distance
    r_v   = 0.3 #random in velocity
    
    #Variabilites in functioning windows 
    r_w['working'] = 0.25
    r_w['student'] = 0.25
    r_w['inactive'] = 0.2
    r_w['free time'] = 0.2
    
    #Occasional use 
    occasional_use = {}
    
    occasional_use['weekday'] = 1
    occasional_use['saturday'] = 0.6
    occasional_use['sunday'] = 0.5
    occasional_use['free time'] = 0.15 # Modified from former file.
    # Previously: occasional_use['free time'] = {'weekday': 0.15, 'weekend': 0.3} #1/7, meaning taking car for free time once a week
    
    #Calibration parameters for the Velocity - Power Curve [kW]
    Par_P_EV = {}
    
    Par_P_EV['small']  = [0.26, -13, 546] # Parametrisation for relation velocity - Power source?
    Par_P_EV['medium'] = [0.3, -14, 600]
    Par_P_EV['large']  = [0.35, -15.2, 620]
    
    #Battery capacity [kWh]
    Battery_cap = {}
    
    Battery_cap['small']  = 37
    Battery_cap['medium'] = 60
    Battery_cap['large']  = 100
    
    # For the data coming from the JRC Survey, a dictionary is defined to assign each country to the neighbouring one
    # these data are: d_tot, d_min, t_func, trips distribution by time
    country_dict = {'AT':'DE', 'CH':'DE', 'CZ':'DE', 'DK':'DE', 'FI':'DE', 'HU':'DE', 'NL':'DE', 'NO':'DE','SE':'DE', 'SK':'DE',
                    'PT':'ES',
                    'BE':'FR', 'LU':'FR',
                    'EL':'IT', 'HR':'IT', 'MT':'IT', 'SI':'IT',
                    'IE':'UK',
                    'BG':'PL', 'CY':'PL', 'EE':'PL', 'LT':'PL', 'LV':'PL', 'RO':'PL'}
    
    # Files with the inputs to be loaded 
    
    script_dir = os.path.dirname(os.path.realpath(__file__))
    inputfolder = os.path.join(script_dir, "..", "database")
    
    # Selection of the equivalent country from the dictionary defined above
    if country in set(country_dict.values()):
        country_equivalent = country 
    else:
        country_equivalent = country_dict[country]
    
    #Composition of the population by percentage share
    pop_file = os.path.join(inputfolder, "pop_share.csv") 
    pop_data = pd.read_csv(pop_file, header=0, index_col=0)
    
    # Share of the type of vehicles in the country
    vehicle_file = os.path.join(inputfolder, "vehicle_share.csv")
    vehicle_data = pd.read_csv(vehicle_file, header=0, index_col=0)

    # Total daily distance [km]
    d_tot_file = os.path.join(inputfolder, "d_tot.csv")
    d_tot_data = pd.read_csv(d_tot_file, header=0, index_col=0)

    # Distance by trip [km]
    d_min_file = os.path.join(inputfolder, "d_min.csv")
    d_min_data = pd.read_csv(d_min_file, header=0, index_col=[0, 1])

    # Functioning time by trip [min]
    t_func_file = os.path.join(inputfolder, "t_func.csv")
    t_func_data = pd.read_csv(t_func_file, header=0, index_col=[0, 1])

    # Functioning windows
    window_file = os.path.join(inputfolder, "windows.csv")
    window_data = pd.read_csv(window_file, header=[0, 1], index_col=[0, 1, 2])
    window_data = window_data * 60  # Convert hourly to minutes
    window_data = window_data.astype(int)

    # Trips distribution by time
    trips = {}
    for day in ['weekday', 'saturday', 'sunday']:
        file = os.path.join(inputfolder, f"trips_by_time_{day}.csv")
        trips[day] = pd.read_csv(file, header=0)
        trips[day] = trips[day][country_equivalent] / 100
    
    
    #Composition of the population by percentage share
    pop_sh = {}
    
    for us in ['working', 'student', 'inactive']:
        pop_sh[us] = pop_data.loc[country, us]
    
    #Share of the type of vehicles in the country
    vehicle_sh = {}
    
    for size in ['small', 'medium', 'large']:
        vehicle_sh[size] = vehicle_data.loc[country, size]
    
    # Total daily distance 
    d_tot = {}
    
    d_tot['weekday']  = d_tot_data.loc[country_equivalent, 'weekday']
    d_tot['saturday'] = d_tot_data.loc[country_equivalent, 'weekend']
    d_tot['sunday']   = d_tot_data.loc[country_equivalent, 'weekend']
    
    # Distance by trip
    d_min = {}
    
    for day in ['weekday', 'saturday', 'sunday']:    
        d_min[day] = {}
        for travel_type in ['business', 'personal']:
            d_min[day][travel_type] = d_min_data[country_equivalent][travel_type][day]
        d_min[day]['mean']  = round(np.array([d_min[day][k] for k in d_min[day]]).mean())
            
    # Functioning time by trip [min]
    t_func = {}
    
    for day in ['weekday', 'saturday', 'sunday']:    
        t_func[day] = {}
        for travel_type in ['business', 'personal']:
            t_func[day][travel_type] = t_func_data[country_equivalent][travel_type][day]    
        t_func[day]['mean']  = round(np.array([t_func[day][k] for k in t_func[day]]).mean())
    
    # Functioning windows 
    if country in window_data.columns.get_level_values(0):    
        country_window = country
    else: 
        print('\n[WARNING] There are no specific functioning windows defined for the selected country, standard windows will be used. \nEdit the "windows.csv" file to add specific functioning windows.\n')
        country_window = 'Standard'
        
    window = {}
    
    window['working']   = {'main':      [[window_data[country_window]['Start']['Working']['Main'][1],       window_data[country_window]['End']['Working']['Main'][1]],  
                                        [window_data[country_window]['Start']['Working']['Main'][2],       window_data[country_window]['End']['Working']['Main'][2]]], 
                        'free time': [[window_data[country_window]['Start']['Working']['Free time'][1],  window_data[country_window]['End']['Working']['Free time'][1]],   
                                        [window_data[country_window]['Start']['Working']['Free time'][2],  window_data[country_window]['End']['Working']['Free time'][2]], 
                                        [window_data[country_window]['Start']['Working']['Free time'][3],  window_data[country_window]['End']['Working']['Free time'][3]]]}
    window['student']   = {'main':      [[window_data[country_window]['Start']['Student']['Main'][1],       window_data[country_window]['End']['Student']['Main'][1]],  
                                        [window_data[country_window]['Start']['Student']['Main'][2],       window_data[country_window]['End']['Student']['Main'][2]]],                                     
                        'free time': [[window_data[country_window]['Start']['Student']['Free time'][1],  window_data[country_window]['End']['Student']['Free time'][1]],    
                                        [window_data[country_window]['Start']['Student']['Free time'][2],  window_data[country_window]['End']['Student']['Free time'][2]],
                                        [window_data[country_window]['Start']['Student']['Free time'][3],  window_data[country_window]['End']['Student']['Free time'][3]]]}
    window['inactive']  = {'main':      [[window_data[country_window]['Start']['Inactive']['Main'][1],      window_data[country_window]['End']['Inactive']['Main'][1]]], 
                        'free time': [[window_data[country_window]['Start']['Inactive']['Free time'][1], window_data[country_window]['End']['Inactive']['Free time'][1]],   
                                        [window_data[country_window]['Start']['Inactive']['Free time'][2], window_data[country_window]['End']['Inactive']['Free time'][2]]]}
    
    #Re-format functioning windows to calculare the Percentage of travels in functioning windows 
    wind_temp = copy.deepcopy(window)
    for key in wind_temp.keys():
        for act in ['main', 'free time']:
            wind_temp[key][act] = [item for sublist in window[key][act] for item in sublist]
            wind_temp[key][act] = [(x / 60) for x in wind_temp[key][act]]
    
    # Definition of Users 
    
    user = User(name=statut+'-'+car, us_pref=0, n_users=int(round(tot_users)))
    User_list.append(user)
    
    # Definition of Appliances: One App for each day type.
    day_types = ['weekday', 'saturday', 'sunday']
    
    for d in day_types:
        appliance = user.Appliance(user, n=1, Par_power=Par_P_EV[car], Battery_cap = Battery_cap[car], 
                                P_var = P_var, w = 1, d_tot = d_tot[d],
                                r_d = r_d, t_func = t_func[d][func], r_v = r_v, d_min = d_min[d][func], 
                                fixed = 'no', fixed_cycle = 0, occasional_use = occasional_use[d], flat = 'no', 
                                pref_index = 0, wd_we_type = 0, P_series = False, day_type=d)
    
        if statut == 'inactive':
            if day_period == 'main':
                appliance.windows(w1=window['inactive']['main'][0], r_w=r_w['inactive'])
            elif day_period == 'free time':
                appliance.windows(w1=window['inactive']['free time'][0],
                                w2=window['inactive']['free time'][1], r_w=r_w['free time'])
            else:
                raise ValueError("Error: day period is neither 'main' or 'free time'. (BE.py - 234)")
        elif statut == 'working' or statut == 'student':
            if day_period == 'main':
                appliance.windows(w1=window[statut]['main'][0], 
                                w2=window[statut]['main'][1], r_w=r_w[statut])
            elif day_period == 'free time':
                appliance.windows(w1=window[statut]['free time'][0],
                                w2=window[statut]['free time'][1], 
                                w3=window[statut]['free time'][2], r_w=r_w['free time'])
            else:
                raise ValueError("Error: day period is neither 'main' or 'free time'. (BE.py - 244)")
        else:
            raise ValueError("Error: statut is neither 'working', 'inactive' or 'free time'. (BE.py - 246)")
    
    return User_list
    

