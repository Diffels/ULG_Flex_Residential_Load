# -*- coding: utf-8 -*-
"""
@author: noedi
    
September 2024
"""

#Not OPTIMAL BECAUSE IT ALWAYS COMPUTE BOTH PROGRAM AT EACH CALL
from scipy.interpolate import CubicSpline
import matplotlib.pyplot as plt
import numpy as np

'''
Description file

'''

def TumbleDryer(plot=True):
    '''
    Source:
    '''
    P = [0.5, 0.5]

    # Program 1
    P1_x = np.array(range(5, 65, 5))
    P1_y = np.array([700, 1700, 1750, 1850, 1980, 1950, 2000, 1950, 2000, 1900, 1600, 500])
    cs = CubicSpline(P1_x, P1_y)
    P1_x_interp = np.linspace(min(P1_x), max(P1_x), len(P1_y)*5)
    P1_y_interp = cs(P1_x_interp)

    # Program 4
    P4_x = np.array(range(5, 115, 5))
    P4_y = np.array([700, 1700, 1800, 1900, 2020, 1950, 1700, 1800, 1300, 200, 200, 400, 2200, 500, 750, 1250, 400, 1700, 500, 1100, 2750, 1200])  # y-values (power in watts)
    cs = CubicSpline(P4_x, P4_y)
    P4_x_interp = np.linspace(min(P4_x), max(P4_x), len(P4_y)*5)
    P4_y_interp = cs(P4_x_interp)

    if plot:
        # Plot the results
        plt.plot(P1_x, P1_y, 'o', color='orange')
        plt.plot(P1_x_interp, P1_y_interp, '-', label='Program 1', color='tab:orange')  

        plt.plot(P4_x, P4_y, 'o', label='Data Points', color='orange')
        plt.plot(P4_x_interp, P4_y_interp, '-', label='Program 4', color='tab:blue')
    
        plt.xlabel('Time [min]')
        plt.ylabel('Power [W]')
        plt.grid(True)
        plt.legend()
        plt.title('Cubic Spline Interpolation of Tumble Dryer Power Consumption')
        plt.show()

    rand_choice = np.random.choice([1, 4], p=P)
    if rand_choice == 1:
        return (P1_x_interp, P1_y_interp)
    else:
        return (P4_x_interp, P4_y_interp)


def WashingMachine(plot=True):
    '''
    Source:
    '''
    P = [0.5, 0.5]

    # # Program 1
    P1_x = np.array(range(5, 145, 5))
    P1_y = np.array([300, 250, 250, 550, 500, 1200, 550, 150, 125, 100, 250, 150, 100, 1000, 1480, 1000, 1500, 100, 150, 100, 100, 150, 100, 500, 250, 400, 1450, 1070])
    cs = CubicSpline(P1_x, P1_y)
    P1_x_interp = np.linspace(min(P1_x), max(P1_x), len(P1_y)*5)
    P1_y_interp = cs(P1_x_interp)

    # Program 4
    P4_x = np.array(range(5, 220, 5))
    P4_y = np.array([200, 1, 200, 100, 300, 250, 100, 2250, 1050, 100, 120, 120, 120, 200, 120, 550, 1, 400, 1450, 120, 120, 120, 120, 120, 120, 500, 250, 700, 2900, 2200, 1, 120, 120, 120, 250, 120, 1, 550, 120, 1, 1450, 550, 120])  # y-values (power in watts)
    cs = CubicSpline(P4_x, P4_y, bc_type='natural')
    P4_x_interp = np.linspace(min(P4_x), max(P4_x), len(P4_y)*5)
    P4_y_interp = cs(P4_x_interp)
    P4_y_interp = np.clip(P4_y_interp, a_min=1, a_max=None)

    print(len(P4_y_interp))
    print(215/5)
    if plot:
        # Plot the results
        plt.plot(P1_x, P1_y, 'o', color='orange')
        plt.plot(P1_x_interp, P1_y_interp, '-', label='Program 1', color='tab:orange')  

        plt.plot(P4_x, P4_y, 'o', label='Data Points', color='orange')
        plt.plot(P4_x_interp, P4_y_interp, '-', label='Program 4', color='tab:blue')
    
        plt.xlabel('Time [min]')
        plt.ylabel('Power [W]')
        plt.grid(True)
        plt.legend()
        plt.title('Cubic Spline Interpolation of Washing Machine Power Consumption')
        plt.show()

    rand_choice = np.random.choice([1, 4], p=P)
    if rand_choice == 1:
        return (P1_x_interp, P1_y_interp)
    else:
        return (P4_x_interp, P4_y_interp)


if __name__ == '__main__':
    TumbleDryer()
    WashingMachine()
