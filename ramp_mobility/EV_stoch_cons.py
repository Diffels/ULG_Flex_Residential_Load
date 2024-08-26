# -*- coding: utf-8 -*-
"""
@author: noedi
    
August 2024
"""

# Import required libraries
import numpy as np
import random 
import calendar
from ramp_mobility.initialise import yearly_pattern 


def EV_stoch_cons(User_list, full_year, year=2024, country='BE', day_type='weekday', disp=True):
    '''
    Function that computes stochastic data (EV daily consumption, daily time and distance) from config_init_.py 
    corresponding to Belgium case. Other files (for other countries) should be properly modified. 
    Inputs:
        - User_list (list of Class User): List of User to simulate, in the default case, there is only 1.
        - full_year (boolean): Simulate over one year or a single day.
        - disp (boolean): Display information relative of stochastic data at each iteration or not.
        - year (int): Year to simulate.
        - country ['AT'...'UK']: Country used in the simulation. Currently only available for 'BE': BELGIUM.
        - day_type ['weekday', 'saturday', 'sunday']: Indicate when simulating on a single day the type.
    Outputs:
        - list_EV_caps (array float): Containing stochastic data, EV daily consumption.
        - list_dists (array float): Containing stochastic data, daily distance.
        - list_times (array float): Containing stochastic data, daily time.
    '''
    
    list_EV_caps=[]
    list_times=[]
    list_dists=[]
        
    if full_year:
        year_behaviour, dummy_days = yearly_pattern(country, year)
    # Defining n_sim depending on arg full_year
        if calendar.isleap(year): 
            n_sim = 366 # leap full year
        else:
            n_sim = 365  # normal full year
    else:
        n_sim = 1
        
    # If full_year-> d = [0...365/366], oth d = 1
    for d in range(n_sim):            
        # Only 1 User created:
        for Us in User_list:
                
            if full_year:
                curr_day = year_behaviour[d] #0, 1, 2
                if curr_day == 0:
                    day_type = 'weekday'
                elif curr_day == 1:
                    day_type = 'saturday'
                elif curr_day == 2:
                    day_type = 'sunday'
            elif day_type != 'weekday':
                print("Day type set as: ",day_type,".")
            else:
                print("Default day type used: weekday.")
            
            # Selecting the appliance linked to to right day type.
            App = [App for App in Us.App_list if App.day_type == day_type]
            if len(App) != 1: raise ValueError("Error in EV_stochastic.py, more than one (or 0) appliance.s linked to the same day type.")
            App = App[0]
            
            random_var_v = random.uniform((1-App.r_v),(1+App.r_v))
            random_var_d = random.uniform((1-App.r_d),(1+App.r_d))

            rand_dist = round(random.uniform(App.dist_tot,int(App.dist_tot*random_var_d))) 
            App.vel = App.func_dist/App.func_cycle * 60 
            rand_vel = np.maximum(20, round(random.uniform(App.vel,int(App.vel*random_var_v)))) #average velocity of the trip, minimum value is 20 km/h to get reasonable values from the power curve
            rand_time = int(round(rand_dist/rand_vel * 60))  #Function to calculate the total time based on total distance and average velocity 
                                                    
            power = (App.Par_power[0] * rand_vel**2 + App.Par_power[1] * rand_vel + App.Par_power[2]) * 12
            power/=1e3
            EV_cap = power*rand_time/60
            #print(">> Power =", power, " [kW]")
            if disp:
                print(">> EV Capacity =", EV_cap, " [kWh]")
                print(">> Distance =", rand_dist, " [km]")
                print(">> Time =", rand_time," [min]")
            
            list_EV_caps.append(EV_cap)
            #list_dists.append(rand_dist)
            #list_times.append(rand_time)
            
    return list_EV_caps

