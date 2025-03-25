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
from Flexibility import flexibility_window
from ramp_mobility.EV_run import EV_run
from Space_heating import theoretical_model_dynamic
from heating_2 import run_space_heating
import time
import random
import json
import datetime as dt
import xarray as xr
from constant import StaticLoad
import matplotlib.pyplot as plt
from StROBe.Data.Appliances import set_appliances


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

def get_profiles(config, dwelling_compo):
    '''
    Function that computes the different load profiles.

    Inputs:
        - config (dict): Dictionnay that contains all the inputs defined in Config.xlsx
        - dwelling_compo (list): Containing the dwelling composition.
    
    Outputs: 
        - df (pd.DataFrame): Dataframe containing the results, ie for each time step, the consumption of each
        appliance.
        - times (np.ndarray): Execution time for each simulation.
        - loads (np.ndarray): Total load during the simulation.
    '''
    times = np.zeros(config['nb_households'])

    nminutes = config['nb_days'] * 1440 + 1
    P = np.zeros((config['nb_households'], nminutes))

    appliances_list = list(config['appliances'].keys())
    appliances_list.extend(['Hot Water', 'EV_charging', 'PAC'])
    print(appliances_list)
    for i in range(config['nb_households']):
        start_time = time.time()
        family = Household_mod(f"Scenario {i}", selected_appliances = config['appliances']) # print put in com 
        #family = Household_mod(f"Scenario {i}",members = dwelling_compo, selected_appliances = config['appliances']) # print put in com 
        #family = Household_mod(f"Scenario {i}")
        family.simulate(year = config['year'], ndays = config['nb_days']) # print in com
        df = pd.DataFrame(family.app_consumption)
        if config['Hot_Water_Boiler'] >= random.random():
            hot_water = hot_water_elec_consumption(pd.DataFrame({'mDHW':family.mDHW}), config['year'],config["Hot_water_Boiler_power"])
            df['Hot Water'] = hot_water.tolist()
        if config['PAC_presence'] == True:
            print("Pac")
            #---Space Heating -------------
            shsetting_data = family.sh_day
            heating_consumption = run_space_heating(shsetting_data, config['nb_days'])*1000 #return an array with powers in kW every 10min, times 1000 to have the results in Watts

            heating_cons_duplicate = [elem for elem in heating_consumption for _ in range(10)]   # To go from 10 to 1 min time step
            heating_cons_duplicate = pd.Series(heating_cons_duplicate)/4                         #divided by the COP of conventional heat pump 
            df['Heating'] = df.get('Heating', 0) + heating_cons_duplicate
            #------------------------------

        if pd.notna(config['flex_mode']) : 
            print("flex")
            sa = [x for x in config["appliances"].keys() if x in df.columns]
            flex_window = flexibility_window(df[sa], family.occ_m, config['flex_mode'], flexibility_rate= config['flex_rate'])
            flex_window.rename(columns=lambda col: f"flex_{col}", inplace=True)
            appliances_list.extend([f'flex_{x}' for x in config['appliances'].keys()])

        r = random.random()
        if config['EV_presence'] >= r:
            print("EV")
            # Reshaping of occupancy profile 
            occupancy = occ_reshape(family.occ_m, 10)
            # Determining EV parameter:
            sizes=['small', 'medium', 'large']
            config['EV_size'] = np.random.choice(sizes, p=config['prob_EV_size'])
            usages=['short', 'normal', 'long']
            config['EV_usage'] =  np.random.choice(usages, p=config['prob_EV_usage'])
            powers=[3.7, 7.4, 11, 22] #kW
            config['EV_charger_power'] =  np.random.choice(powers, p=config['prob_EV_charger_power'])
            # Running EV module
            load_profile, n_charge_not_home =EV_run(occupancy,config)
            EV_profile = pd.DataFrame({'EVCharging':load_profile})
            #EV_flex = pd.DataFrame({'EVCharging':load_profile, 'Occupancy':occupancy})

            if 'EVCharging' not in df.columns:
                df['EVCharging'] =  EV_profile*1000
            else :
                df['EVCharging'] = df['EVCharging'] + EV_profile['EVCharging']*1000
        
        P[i,:] = family.P
        end_time = time.time()
        execution_time = end_time - start_time
        times[i] = execution_time
        print(f"Simulation {i+1}/{config['nb_households']} is done. Execution time: {execution_time} s.")  
        StaticLoad_pres = [col for col in StaticLoad if col in df.columns]
        df.loc[:, 'Base Load'] = df[StaticLoad_pres].sum(axis=1)
        df.drop(columns=StaticLoad_pres, inplace=True)
        df = index_to_datetime(df, config['year'],config['plot_ts'])
        
        if config['CSV folder'] :
            total = df.drop(columns=['EVCharging','Heating', 'Hot Water']).sum(axis=1)/1000
            df_tot = pd.DataFrame({"mult":total,
                                   'EVCharging': df['EVCharging']/1000,
                                   'Heating':df['Heating']/1000,
                                   'Hot Water':df['Hot Water']/1000})
            df_tot.to_csv(os.path.join(config['CSV folder'],f'LoadShape_{i+1}.csv'))

        df = pd.concat([df, flex_window], axis=1)
        for col in appliances_list:
            if col not in df.columns:
                df[col]=0
                if pd.notna(config['flex_mode']) and col in config['appliances'].keys():
                    df[f'flex_{col}']=0
        if  pd.notna(config['flex_mode']) : 
            for y in [f'flex_{x}' for x in config['appliances'].keys()]:
                df.loc[df[y]<0.5, y]=0
                df.loc[df[y]>=0.5, y]=1



        data_array = xr.DataArray(df, dims=['index', 'columns'], coords={'columns': df.columns}) 
        
        if i == 0 :
            dataset =  xr.Dataset({f'House {i}': data_array})
        else :
            dataset[f'House {i}'] = data_array
    dataset.coords['index'] = df.index

    P = np.array(P)
    
    total_elec = np.sum(P)
    average_total_elec = total_elec/config['nb_households']
    loads=average_total_elec.sum()/60/1000
    
    #df = df/config['nb_households']
    return loads, times, dataset

def index_to_datetime(df, year, ts):
    init_date = dt.datetime(year, 1,1,0,0)
    dates = []
    for i in range(len(df)):
        dates.append(init_date+dt.timedelta(minutes=i))
    df['DateTime'] = dates
    df = df.set_index('DateTime')
    df10min = df.resample(str(ts)+'min').mean()
    return df10min

def index_to_datetime_no_mean(df, year, ts):
    init_date = dt.datetime(year, 1,1,0,0)
    dates = []
    dates = pd.date_range(start=f'{year}-01-01', periods=len(df), freq="15T")
    """for i in range(len(df)):
        dates.append(init_date+dt.timedelta(minutes=i*ts))"""
    df['DateTime'] = dates
    df = df.set_index('DateTime')
    return df


def limit_power(power_per_time, max_power):
    """
    Add ramprate ? Unusefull for me

    This function takes as arguments the power needed to heat the domestical heat water for each timesteps of the simulation and the maximal power that could
    be delivered by the electrical boiler 

    It returns a vector of the electrical boiler load

    """
    power_per_time = np.array(power_per_time)
    over_power = 0
    j=0
    
    for i in range(len(power_per_time)):
        actual_power = power_per_time[i]
        if i > j or j ==0:
            j=i
        if j <=len(power_per_time)-1: 
            while actual_power > max_power : 
                j=j+1
                if j >len(power_per_time)-1: 
                    power_per_time[i] = max_power
                    break

                if power_per_time[j] < max_power:
                    actual_power = actual_power+power_per_time[j]-max_power 
                    if actual_power > max_power:
                        power_per_time[j] = max_power
                    else : 
                        power_per_time[j]= actual_power
                        power_per_time[i] = max_power
                        j=j-1
        else :
            if actual_power > max_power :
                over_power = over_power + actual_power - max_power
                power_per_time[i] = max_power
    if over_power > 0:
        print(f'{over_power/60e3} kWh of hot water energy should be added next day')
    return power_per_time
def hot_water_elec_consumption(mDHW,year, max_power):
    T_initial = 14 # Température de l'eau froide (en °C)
    T_final = 60   # Température de consigne (en °C)
    efficiency = 0.9  # Efficacité du chauffe-eau (en fraction)
    specific_heat = 4186  # Capacité thermique spécifique de l'eau (J/kg°C)
    rho = 1 #kg/L
    mDHW['Power'] = mDHW['mDHW'] * rho  *(T_final-T_initial)*specific_heat#[J]
    mDHW['Power'] = mDHW['Power']/(efficiency*3.6e3)#Wh pour chaque minutes
    mDHW['Power'] = mDHW['Power']*60 #kW
    #Power of the electrical boiler is limited to 5 kW 
    limited_Boiler_power = max_power * 1e3#kW
    mDHW['Power_limited'] = limit_power(mDHW['Power'], limited_Boiler_power)

   
    init_date = dt.datetime(year, 1,1,0,0)
    dates = []

    for i in range(len(mDHW)):
        dates.append(init_date+dt.timedelta(minutes=i))
    mDHW['DateTime'] = dates
    mDHW = mDHW.set_index('DateTime')
    """daily_consumption = mDHW.resample('D').sum().reset_index()"""
    return mDHW['Power_limited'][:-1]
def three_phases_load(loads) : 

    phases = ['phase 1', 'phase 2', 'phase 3']
    if 'Heating' in loads.columns:
        loads_without_heating = loads.drop(columns = ['Heating'])
    assigned_phases = np.random.choice(phases, size=loads_without_heating.shape[1], p=[1/3, 1/3, 1/3])

    split_values = loads['Heating'] / 3

    sum_phase_1 = loads_without_heating.loc[:, assigned_phases == 'phase 1'].sum(axis=1)+split_values
    sum_phase_2 = loads_without_heating.loc[:, assigned_phases == 'phase 2'].sum(axis=1)+split_values
    sum_phase_3 = loads_without_heating.loc[:, assigned_phases == 'phase 3'].sum(axis=1)+split_values

    loads_3phases = pd.DataFrame(
        {
            'Phase 1' : sum_phase_1,
            'Phase 2' : sum_phase_2,
            'Phase 3' : sum_phase_3
        }
    )
    import matplotlib.pyplot as plt
    loads_3phases = loads_3phases.fillna(0)
    loads_3phases.plot()
    plt.show()
    return loads_3phases

def simulate(file_path, disp=True):
    '''
    Simulation with a .json file.
    Input:
        - file (str): .json file path describing the configuration of the simulation.
        - disp (bool): Displaying informations about the simulation. 
    Outputs: 
        - df (pd.DataFrame): Dataframe containing the results, ie for each time step, the consumption of each
        appliance.
    '''
    with open(file_path, 'r', encoding="utf-8") as file: # 'utf-8' to avoid "é" issues
        config = json.load(file)  # Load the JSON data into a Python dictionary

    dwelling_compo = []
    for i in range(config['dwelling_nb_compo']):
        dwelling_compo.append(config[f'dwelling_member{i+1}'])

    if sum(config['prob_EV_size']) != 1: 
        raise ValueError(f"Probabilities associated to the EV size are incorrect. {config['prob_EV_size']}")
    if sum(config['prob_EV_usage']) != 1 and config['EV_km_per_year'] == 0: 
        raise ValueError(f"Probabilities associated to the EV usage are incorrect. {config['prob_EV_usage']}")
    if sum(config['prob_EV_charger_power']) != 1: 
        raise ValueError(f"Probabilities associated to the charger powers are incorrect. {config['prob_EV_charger_power']}")
    
    loads, times, dataset = get_profiles(config, dwelling_compo)
    
    if config['Write Excel']:
        file_path = config['Excel File']
        with pd.ExcelWriter(file_path) as writer:
            for idx in dataset.data_vars:
                subset = dataset[idx].to_pandas()
                subset = index_to_datetime_no_mean(subset, config['year'], config['plot_ts'])
                subset.to_excel(writer, sheet_name=idx)
    df = pd.DataFrame(0, index= range(0,len(dataset['index'].values)), columns=dataset['columns'].values)
   
    if config['Write Tot csv']:
        for var in dataset.data_vars :
            data_var = dataset[var].to_pandas()  
            df += data_var.fillna(0)
        df = df.set_index(dataset['index'].values)
        df['Total'] = df.sum(axis=1)
        df.to_csv(config['CSV file'], index = False)
    if disp: 
        print("---- Results ----")
        print("Time Horizon: ", config["nb_days"], "day(s).")
        print("Execution time [s]")
        print(f"\tMean: {np.mean(times)}")
        print("Total load [kWh]")
        print(f"\tMean: {round(np.mean(loads), 2)}; STD: {np.std(loads)}")
    if config['three_phases'] :   
        loads = three_phases_load(df) 
    
    if config['plot']:
        make_demand_plot(df.index, df, title=f"Load profile for {config['nb_households']} households, for {config['nb_days']} days.")
