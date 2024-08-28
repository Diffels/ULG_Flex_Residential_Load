# -*- coding: utf-8 -*-
"""
@authors: noedi
    
August 2024
"""

# Import required modules
from base_load import get_profiles
import time
import numpy as np

if __name__ == '__main__':

    nSim=30

    loads = np.zeros(nSim)
    times = np.zeros(nSim)
    
    for sim in range(nSim):
        start_time = time.time()
        tot_load = get_profiles()
        end_time = time.time()
        execution_time = end_time - start_time
        loads[sim]=tot_load
        times[sim]=execution_time
        print(f"Simulation {sim+1}/{nSim} is done. Execution time: {execution_time} s.")

print("---- Results ----")
print("\t Execution time [s]")
print(f"\t\tMean: {np.mean(times)}; STD: {np.std(times)}")
print("\t Total load per week [kWh]")
print(f"\t\tMean: {np.mean(loads)}; STD: {np.std(loads)}")
print("\t Total load per year [GWh]")
print(f"\t\tMean: {np.mean(loads*52/1e3)}; STD: {np.std(loads*52/1e3)}")