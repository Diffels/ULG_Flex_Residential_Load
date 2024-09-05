# -*- coding: utf-8 -*-
"""
@authors: noedi
    
August 2024
"""

# Import required modules
import os
from load_profiles import get_profiles, get_inputs
import numpy as np
from plots import make_demand_plot

if __name__ == '__main__':

    config, dwelling_compo = get_inputs()

    nSim=config['nb_Scenarios']

    loads, times, df = get_profiles(config, dwelling_compo)
    
    print("---- Results ----")
    print("Time Horizon: ", config["nb_days"], "day(s).")
    print("Execution time [s]")
    print(f"\tMean: {np.mean(times)}")
    print("Total load [kWh]")
    print(f"\tMean: {round(np.mean(loads), 2)}; STD: {np.std(loads)}")

    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Results.xlsx")
    df.to_excel(file_path)
    
    if config['Plot'] :
        make_demand_plot(df.index, df, title=f"Load profile for {config['nb_Scenarios']} households, for {config['nb_days']} days.")
        #df = df/config['nb_Scenarios']
        #make_demand_plot(df.index, df, title=f"Mean Load profile for 1 household, for {config['nb_days']} days.")