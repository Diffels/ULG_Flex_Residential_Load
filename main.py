# -*- coding: utf-8 -*-
"""
@authors: noedi
    
August 2024
"""

# Import required modules
import os
from base_load import get_profiles, get_inputs
import time
import numpy as np
from plots import make_demand_plot

if __name__ == '__main__':

    config, dwelling_compo, appliances = get_inputs()

    nSim=config['nb_Scenarios']

    loads, times, df = get_profiles(config, dwelling_compo, appliances)
    print("---- Results ----")
    print("\t Execution time [s]")
    print(f"\t\tMean: {np.mean(times)}; STD: {np.std(times)}")
    print("\t Total load per week [kWh]")
    print(f"\t\tMean: {np.mean(loads)}; STD: {np.std(loads)}")
    print("\t Total load per year [GWh]")
    print(f"\t\tMean: {np.mean(loads*52/1e3)}; STD: {np.std(loads*52/1e3)}")

    file_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Results.xlsx")
    if config['Plot'] :
        make_demand_plot(df[:100000].index, df[:100000], title=f"Average Consumption for {config['nb_Scenarios']} scenarios")