# -*- coding: utf-8 -*-
"""
@author: duchmax
    
August 2024
"""

# Import required module
from StROBe.Data.Appliances import set_appliances

defaultcolors = {'Base Load':'#7fe5ca', 
                 'WasherDryer':'#ffb2c8', 
                 'TumbleDryer':'#d5b0fc',
                 'DishWasher':'#ffd0ac',
                 'HeatPumpPower':'#daf3bf', 
                 'DomesticHotWater':'#8be9f9',
                 'EVCharging':'#ffcbff',
                 'BatteryConsumption':'#b0b6fc',
                 'HotWater':'#048b9a',
                 'WashingMachine': '#ffffbe'}

special_appliances = ['DishWasher','WasherDryer','TumbleDryer','WashingMachine', 'EVCharging']

StaticLoad = [x for x in set_appliances if (set_appliances[x]['type'] == 'appliance' and x not in special_appliances)]

