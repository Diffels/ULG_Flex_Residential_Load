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


def config_init_(car: str, usage: str, country: str)->object:
    '''
    Description
    Function that initialize the simulation with a bunch of parameters dans constants for Belgium.
    The user (driver) class contains 3 appliances, each representing a EV linked to a type day. 
    (weekday, saturday, sunday).
    Inputs:
        - car (str): EV size ['small', 'medium', 'large']
        - usage (str): Driver usage ['short', 'normal', 'long']
        - country (str): Simulation country, currently only working with 'BE' (Belgium). 
    Output:
        - user (obj class User): the User class that represents the main driver for the simulation.  
    '''
                
    if country != 'BE': raise ValueError("Model is currently only working for Belgium.")

    P_var = 0.1 #random in power
    r_d   = 0.3 #random in distance
    r_v   = 0.3 #random in velocity
    
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

    # Percentage of mean distance travelled by EV
    Usage_car_mean = {}

    Usage_car_mean['short'] = 0.5
    Usage_car_mean['normal'] = 1
    Usage_car_mean['long'] = 2

    # Percentage of min distance travelled by EV
    Usage_car_min = {}

    Usage_car_min['short'] = 0.5
    Usage_car_min['normal'] = 1
    Usage_car_min['long'] = 2

    # Percentage of mean time travelled by EV
    Usage_car_time = {}

    Usage_car_time['short'] = 0.5
    Usage_car_time['normal'] = 1
    Usage_car_time['long'] = 2
    
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

    # Total daily distance [km]
    d_tot_file = os.path.join(inputfolder, "d_tot.csv")
    d_tot_data = pd.read_csv(d_tot_file, header=0, index_col=0)

    # Distance by trip [km]
    d_min_file = os.path.join(inputfolder, "d_min.csv")
    d_min_data = pd.read_csv(d_min_file, header=0, index_col=[0, 1])

    # Functioning time by trip [min]
    t_func_file = os.path.join(inputfolder, "t_func.csv")
    t_func_data = pd.read_csv(t_func_file, header=0, index_col=[0, 1])

    # Total daily distance 
    d_tot = {}

    d_tot['weekday']  = d_tot_data.loc[country_equivalent, 'weekday']
    d_tot['saturday'] = d_tot_data.loc[country_equivalent, 'weekend']
    d_tot['sunday']   = d_tot_data.loc[country_equivalent, 'weekend']

    # Distance by trip
    d_min = {}
    
    for day in ['weekday', 'saturday', 'sunday']:    
        d_min[day] = {}
        for travel_type in ['personal']:
            d_min[day] = d_min_data[country_equivalent][travel_type][day]
            
    # Functioning time by trip [min]
    t_func = {}
    
    for day in ['weekday', 'saturday', 'sunday']:    
        t_func[day] = {}
        for travel_type in ['personal']:
            t_func[day] = t_func_data[country_equivalent][travel_type][day]    

    # Definition of Users
    if isinstance(usage, int):
        name=f'Km/year ({usage})'
    else:
        name=usage

    user = User(name=name+'-'+car, n_users=1)
    
    
    # Definition of Appliances: One App for each day type.
    day_types = ['weekday', 'saturday', 'sunday']
    
    App=[]
    for d in day_types:
        if not isinstance(usage, int):
            dist_tot = d_tot[d] * Usage_car_mean[usage]
            dist_min = d_min[d] * Usage_car_min[usage]
            time_func = t_func[d] * Usage_car_time[usage]
        else:
            kmPerDay = usage/365
            ratio = kmPerDay/d_tot[d]
            dist_tot = kmPerDay
            dist_min = kmPerDay*0.2
            time_func = t_func[d]*ratio         

        appliance = user.Appliance(user, n=1, Par_power=Par_P_EV[car], Battery_cap = Battery_cap[car], 
                                P_var = P_var, w = 1, d_tot = dist_tot,
                                r_d = r_d, t_func = time_func, r_v = r_v, d_min = dist_min, day_type=d)
        App.append(appliance)
    
    user.App_list = App
    return user
    

