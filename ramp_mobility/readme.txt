 __________________________
|                           |
|         EV module         |    by Noé Diffels, derived from ramp-mobility
|___________________________|

This module computes a stochastic EV load profile based on an occupancy profile and predefined parameters 
(such as the type of EV and driver usage) for a time horizon ranging from 1 day to 1 year, minute by minute.

Main Assumptions:

    1. The charging pattern is 'uncontrolled,' i.e., as soon as the EV comes back home, it charges at the nominal 
    charger power (which is defined according to a probability array among 4 fixed values) until fully charged.
    2. Each departure in the occupancy profile corresponds to a departure with the EV, except for departures that 
    last less than 10 minutes, which are not considered as EV usage.
    3. At each EV departure, a probability is computed (depending on the energy available in the EV and the energy 
    required for the journey) for the EV to be refueled and charged during this departure, outside the home.
    4. When a charge occurs away from home (see above), a percentage of the full departure time is taken,
    stochastically, for the EV to be charged. It's assumed to be at the midpoint of the journey and is an instantaneous 
    charge.
    5. The outside battery refuel is defined such that E_come_back_home <= SOC_max - E_spent_half_departure and 
    E_come_back_home >= SOC_min.
    6. Outside charging event are associated with a nominal power of the charging station, which is not always the 
    same that home charger. home_charger=[3.7, 7.4, 11, 22] (kW) with associated probabilities defined in Config.xlsx, 
                        and outside_charger=[7.4, 11, 22, 150] (kW) with associated probabilities=[0.3, 0.35, 0.3, 0.05].

Inputs:

    - Occupancy profile, which details whether the main driver is at home (1) or not (0), with a length of N, the 
    number of minutes considered in the simulation time horizon.
    - Probability of the EV size ['small', 'medium', 'large'], corresponding to different battery capacities defined 
    in config_init_.py as 37, 60, and 100 kWh.
    - Probability of driver usage ['short', 'normal', 'long'], which defines the type of driver journeys to simulate. 
    The 'normal' type corresponds to the statistical mean daily kilometers: 50 km/weekday and 60 km/weekend-day. 
    'Short' corresponds to smaller journeys (30% of 50 km and 30% of 60 km), and 'long' doubles the distances (200% of 
    50 km and 200% of 60 km). All of these distances are then stochastically varied for each journey to simulate daily 
    variations.

    Another way for the user to variates distance EV runs during the simulation is to set a yearly number of 
    kilometers in Config.xlsx. This number would be split in a daily basis and then will be associated to a 
    stochastic number of kilometers per day. If EV_km_per_year <= 0, it does not take into account this input
    and probabilities of driver usage is used.

Outputs:

    It returns several time series, such as the load profile of EV charging, the SOC evolution of the car, when the 
    car is plugged in, and when a charge event occurs away from home. The load profile associated with the occupancy
    profile can be merged and used for further flexibility analysis.


Sources: 

    [1] Falvo, et al. (2014, June) EV charging stations and modes: International standards. In 2014 international 
    symposium on power electronics, electrical drives, automation and motion (pp. 1134-1139). IEEE.
    [2] 


# TODO/Improvements

# Why some huge execution time, other not?