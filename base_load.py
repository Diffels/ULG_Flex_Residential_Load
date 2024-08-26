import os
import sys
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from Household_mod import Household_mod
from plots import make_demand_plot
from read_config import read_config
from Flexibility import flexibility_window, from_10_to_1min_basis



if __name__ == '__main__':
    #Simulation for 1 dwelling
    #Reading the input file
    out,config_full = read_config("C:\Master 3\Job été\MRL-Wallonia\Config.xlsx")
    nb_days = out['sim']['ndays']
    year = out['sim']['year']
    NB_Scenarios = out['sim']['N']

    EV_profile = pd.read_excel("C:\Master 3\Job été\MRL-Wallonia\EV_load_profile.xlsx")

    dwelling_compo = []
    for i in range(out['dwelling']['nb_compo']):
        dwelling_compo.append(out['dwelling'][f'member{i+1}'])
    #family = Household_mod("Example household", nb_people = 4,selected_appliances = special_appliances)
    appliances = [x for x in out['equipment'].keys() if out['equipment'][x] == True]


    flex_mode = out['flex']['type']
    flex_rate = out['flex']['rate']

    EV_presence = out['EV']['present']
    EV_size = out['EV']['size']
    EV_statut = out['EV']['statut']

    nminutes = nb_days * 1440 + 1
    P = np.zeros((NB_Scenarios, nminutes))
    for i in range(NB_Scenarios):
        family = Household_mod(f"Scenario {i}",members = dwelling_compo, selected_appliances = appliances)
        #family = Household_mod(f"Scenario {i}")
        family.simulate(year = year, ndays = nb_days)
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
        if pd.notna(flex_mode) and appliances: 
            flex_window = flexibility_window(df[appliances], family.occ_m, flex_mode, flexibility_rate= flex_rate)
        
        if EV_presence == 'Yes':
            print("Hello Didou")#Pour récup l'occupation suffit de mettre family.occ_m

        P[i,:] = family.P

    P = np.array(P)
    df = df.drop(df.index[-1])
    df['EVCharging'] = EV_profile*1000
    total_elec = np.sum(P)
    average_total_elec = total_elec/NB_Scenarios
    df = df/NB_Scenarios
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

    #make_demand_plot(df[:100000].index, df[:100000], title=f"Average Consumption for {NB_Scenarios} scenarios")