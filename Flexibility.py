# -*- coding: utf-8 -*-
"""
@author: duchmax
    
August 2024
"""

# Import required modules
import numpy as np
from StROBe.Data.Appliances import set_appliances
import datetime as dt

def flexibility_window(app_profile, occ_m, flex_type, year = 2015, flexibility_rate =None):
    """Takes as arguments :
     - the appliance consumption profile,
     - the occupation merged profile of the house,
     - the flexibility rate (if given)

     Return a:
     - Flexibility window for all the selected appliances
    """
    occ_min = from_10_to_1min_basis(occ_m) 
    
    flex_window = app_profile.copy()
    flex_window[:] = 0 
    
    if flex_type in "Based on occupation " : 
        for app in app_profile.columns:
            # On localise les plages de fonctionnement des appliances
            working_indices = np.where(app_profile[app]>set_appliances[app]["standby_power"])
            if len(working_indices[0])>0 : 
                start_indices = working_start(working_indices)#on récup tous les indices de départ de programme
                for starting in start_indices : 
                    low_indice,upper_indice = based_on_occupation_window(occ_min, starting)#on récupére l'intervalle d'occupation pour chaque départ de programme
                    flex_window.loc[low_indice:upper_indice, app] = [1] * (upper_indice- low_indice+1) #Toutes les valeurs dans la plage de flexibilité sont set à 1
    elif flex_type in "Weekly flexible" :
        #Les appareils ménagés sont pleinement flexible. On va donc renvoyer uniquement une plage d'une semaine à chaque fois (si on considère la flexibilité sur 1 semaine)
        #On doit donc savoir quel jours de la semaine la simulation démarre 
        flex_window[:] = 1
        first_day = dt.date(year, 1, 1)
        # Obtenez le jour de la semaine (0 = Lundi, 6 = Dimanche)
        day_of_week = first_day.weekday()
        #Pour la première semaine on est pas sûr que c'est une semaine complète donc 
        week_of_the_year = first_day.isocalendar()[1]
        i=0
        number_of_minutes = np.shape(app_profile)[0]
        while i <= number_of_minutes:
            if week_of_the_year == 1 :
                if number_of_minutes> (7-day_of_week)*1440+1:
                    i = (7-day_of_week)*1440
                    flex_window.loc[i, :] = 0
                    i=i+1
                    week_of_the_year = week_of_the_year+1
            else: 
                if number_of_minutes> (week_of_the_year-1)*7*1440 + (7-day_of_week)*1440+1:#first week+nb_minutes of i weeks
                    i =(week_of_the_year-1)*7*1440 + (7-day_of_week)*1440
                    flex_window.loc[i, :] = 0
                    i=i+1
                    week_of_the_year = week_of_the_year+1
                else:
                    break
    elif flex_type in "Daily flexible":
        flex_window[:] = 1
        i = 0
        number_of_minutes = np.shape(app_profile)[0]
        while i+1440 <= number_of_minutes:
            i = i+1440
            flex_window.loc[i, :] = 0
    elif flex_type in "Hours window":
        if flexibility_rate == None :
            return TypeError("The number of maximum hours for shifting is not given") 
        else : 
            for app in app_profile.columns:
            # On localise les plages de fonctionnement des appliances
                working_indices = np.where(app_profile[app]>set_appliances[app]["standby_power"])
                if len(working_indices[0])>0 : 
                    start_indices = working_start(working_indices)#on récup tous les indices de départ de programme
                    for starting in start_indices : 
                        low_indice,upper_indice = hourly_window(len(occ_min), starting,int(flexibility_rate))#on récupére l'intervalle d'occupation pour chaque départ de programme
                        if upper_indice == len(flex_window):
                            flex_window.loc[low_indice:upper_indice, app] = [1] * (upper_indice- low_indice) #Toutes les valeurs dans la plage de flexibilité sont set à 1
                        else : 
                            flex_window.loc[low_indice:upper_indice, app] = [1] * (upper_indice- low_indice+1) #Toutes les valeurs dans la plage de flexibilité sont set à 1
    return flex_window


def from_10_to_1min_basis(occ_m):
    """
    Takes as arguments :
    -occ_m a vector of values considering timestep of 10 min
    
    Return :
    -vector for timestep of 1min
    """
    length = (np.shape(occ_m)[0]-1)*10+1
    occ_min = np.array(list(range(0,length)))
    #From 10 min base to 1 min
    for i in range(len(occ_m)-1):
        for j in range(10):
            occ_min[i*10+j] = occ_m[i]  
    occ_min[-1] = occ_m[-1] 
    return occ_min


def working_start(working_indices) :
    """
    Takes as arguments a table containing the times at which the appliances are on and return the starting times of appliances"""
    working_indices = working_indices[0]
    non_successives = [working_indices[0]]
    for i in range(len(working_indices) - 1):
        if working_indices[i+1] != working_indices[i] + 1:
            non_successives.append(working_indices[i+1])
    return non_successives

def hourly_window(max_time, starting_indice, hours):
    """
    Define the flexibility window. Arguments :
    - The maximal time of the simulation (in minute)
    - The starting time of the appliance
    - The length of the flexible window in hour
    
    Return :
    - The lower and upper indice (time) of the flexibility window
    """
    low_indice = starting_indice
    upper_indice = starting_indice
    minutes = hours *60
    while minutes > 0:
        if low_indice > 0:
            low_indice = low_indice -1
        if upper_indice < max_time-1:
            upper_indice = upper_indice+1
        minutes = minutes -1
    return low_indice,upper_indice


def based_on_occupation_window(occ_m, starting_indice):
    """
    Define the flexibility window based on the occupation profile :
    -Occ_m is the occupancy merged profile of the dwelling in minutes
    -Starting_indice is the starting time of the appliances in minutes
    It returns : 
    - The lower and upper indices (minutes) of the flexibility window
    """
    low_indice = starting_indice
    upper_indice = starting_indice
    while occ_m[low_indice] == 1:
        if low_indice ==0:
            break
        else : 
            low_indice = low_indice-1
    while occ_m[upper_indice] == 1:
        if upper_indice == len(occ_m)-1:
            break
        else :
            upper_indice = upper_indice+1
     
    return low_indice,upper_indice