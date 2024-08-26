# -*- coding: utf-8 -*-

# Import required modules
import sys
import matplotlib.pyplot as plt

sys.path.append('../')
from EV_stoch_cons import EV_stoch_cons

'''
See main.py, this file is used to show the stochasticity plots.
'''

# Inputs definition

full_year = True  # Choose if simulating the whole year (True) or not (False), if False, the console will ask how many days should be simulated.
countries = ['BE']

tab_EV_caps=[]
tab_dists=[]
tab_times=[]

for c in countries:
    inputfile = f'Europe/{c}'
    simulation_name = ''

    # Define country and year to be considered when generating profiles
    country = f'{c}'
    year = 2016

    for i in range(1):
        EV_cap, dist, time = EV_stoch_cons(inputfile, country, year, full_year)
        tab_EV_caps.append(EV_cap)
        tab_dists.append(dist)
        tab_times.append(time)


def plot_stoch(data, title, xlabel, ylabel, bins=30, c='blue'):
    # Checking if data is a table.
    if len(data) > 0 and isinstance(data[0], list):
        maximums=[]
        minimums=[]
        means=[]
        # Transposing the matrix to get columns
        transposed_data = list(zip(*data))
        for column in transposed_data:
            maximums.append(max(column))
            minimums.append(min(column))
            means.append(sum(column)/len(column))
            
        x_axis=range(len(means))
        plt.figure(figsize=(10, 6))
        plt.plot(x_axis, means, color=c)
        plt.plot(x_axis, maximums, color=c, alpha=0.7)
        plt.plot(x_axis, minimums, color=c, alpha=0.7)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.show()
        
    else:
        x_axis=range(len(data))
        plt.figure(figsize=(10, 6))
        plt.plot(x_axis, data, color=c)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.grid(True)
        plt.show()

plot_stoch(tab_EV_caps, "Stochastic EV Capacities during a year (1 sim)", "Days", "Capacity [kWh]", bins=30, c='tab:blue')
    
#plot_stoch(EV_cap, 'Stochastic EV Capacities during a year', 'Time [day]', 'Capacity (kWh)', c='tab:blue')

#plot_stoch(dist, 'Stochastic Distances during a year', 'Time [day]', 'Distance (km)', c='tab:orange')

#plot_stoch(time, 'Stochastic Durations during a year', 'Time [day]', 'Duration (min)', c='tab:green')
