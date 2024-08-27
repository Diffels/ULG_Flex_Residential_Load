# -*- coding: utf-8 -*-
"""
@authors: duchmax, noedi
    
August 2024
"""

# Import required modules
import os
import pandas as pd
import numpy as np
from Household_mod import Household_mod
from plots import make_demand_plot
from read_config import read_config
from Flexibility import flexibility_window
from ramp_mobility.EV_run import EV_run


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

'''
CREATE FUNCTION THEN CREATE FILE main.py THAT CALLS IT?
'''
def get_profiles():
    '''
    [...] Summary [...]
    Inputs
        - 
    Outputs
        -
    '''
    pass

if __name__ == '__main__':
    # Reading the input file in current directory
    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Config.xlsx")
    out,config_full = read_config(file_path)
    # Appliances instances definition
    dwelling_compo = []
    for i in range(out['dwelling']['nb_compo']):
        dwelling_compo.append(out['dwelling'][f'member{i+1}'])
    #family = Household_mod("Example household", nb_people = 4,selected_appliances = special_appliances)
    appliances = [x for x in out['equipment'].keys() if out['equipment'][x] == True]

    '''Create a dictionnary config containing whole simulation configuration'''
    config = {  
                'nb_days': out['sim']['ndays'],             # Number of days to simulate
                'year': out['sim']['year'],                 # Year of the simulation
                'nb_Scenarios': out['sim']['N'],            # Number of Scenarios
                'ts': out['sim']['ts'],                     # Time Step resolution [h]
                'start_day': out['sim']['start_day'],       # Starting day of the simulation (/!\ start_day+nb_days<365 or 366 if leap.)
                'country': [out['sim']['country']],         # Associated country

                'appliances': appliances,                   #

                'flex_mode': out['flex']['type'],           #
                'flex_rate': out['flex']['rate'],           #

                # EV Parameters
                'EV_presence': out['EV']['present'],        # If a EV is present or not.
                'EV_size': out['EV']['size'],               # EV size:  ['large', 'medium', 'small']
                'EV_statut': out['EV']['statut'],           # Working Statut: ['working', 'student', 'inactive']
                'EV_disp': out['EV']['disp'],               # Flag for displaying some useful information regarding EV profile simulation.
                'EV_nb_drivers': out['EV']['nb_drivers'],   # Number of user to define. For this model=1.
                'User_list': [],                            # List containing all users.
            }


    nminutes = config['nb_days'] * 1440 + 1
    P = np.zeros((config['nb_Scenarios'], nminutes))
    for i in range(config['nb_Scenarios']):
        family = Household_mod(f"Scenario {i}",members = dwelling_compo, selected_appliances = appliances)
        #family = Household_mod(f"Scenario {i}")
        family.simulate(year = config['year'], ndays = config['nb_days'])
        if i == 0:
            """occupancy = dict()
            for j in range(len(dwelling_compo)):
                occupancy.update({dwelling_compo[j]:family.occ[j]})
            occupancy = pd.DataFrame(occupancy)
            occupancy['Merged'] = family.occ_m
            occupancy.to_excel('C:\Master 3\Job été\MRL-Wallonia\occupancy_profile.xlsx')"""
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
            # Running EV module
            EV_profile=EV_run(occupancy,config)

        P[i,:] = family.P

    P = np.array(P)
    df = df.drop(df.index[-1])
    df['EVCharging'] = EV_profile*1000
    total_elec = np.sum(P)
    average_total_elec = total_elec/config['nb_Scenarios']
    df = df/config['nb_Scenarios']

    # May we delete this? 
    """print(' - Total load is %s kWh' % str(average_total_elec.sum()/60/1000))
    print("total Wash machine elec consumptoon is %s" % str(df['WashingMachine'].sum()/60/1000))
    print("total DishWasher elec consumptoonis %s" % str(df['DishWasher'].sum()/60/1000))
    print("total WhasherDryer elec consumptoon is %s"% str(df['WasherDryer'].sum()/60/1000))
    print("total TrumbleDryer elec consumptoon is %s"% str(df['TumbleDryer'].sum()/60/1000))"""
    """average_total_elec = total_elec/NB_Scenarios
    df = df/NB_Scenarios
    power = pd.DataFrame({"Power" : average_total_elec})
    power.plot()
    df.to_excel("mean_load_profile_100.xlsx")
    plt.title("Aggregated load curve")
    plt.xlabel("Timestep (5min timestep) [hour]")
    plt.ylabel("Load [W]")
    plt.legend()
    plt.grid(True)
    plt.show()"""

    make_demand_plot(df[:100000].index, df[:100000], title=f"Average Consumption for {config['nb_Scenarios']} scenarios")