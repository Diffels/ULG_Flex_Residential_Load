 _______________________________________
|                                       |
| EV module, derived from ramp-mobility |
|_______________________________________|

This module allows to compute stochastically an EV load profile based on an occupancy profile 
and predefined parameters (type of the car and driver usage) for a time horizon from 1 day to 1 year, 
minute per minute.  

Main Assumptions: 

    1. The charging pattern is 'uncontrolled', ie soon as the EV come back home, it is charge at nominal charger 
    power until fully charged.
    2. Each departure corresponds to a departure with the EV. 
    3. At each departure a probability is fixed (depending on the energy available in EV and the energy required 
    for the journey) for the EV to be refiled and charged during this departure.
    4. When a charge occurs not at home (see above), a percentage of the full departure time is taken, stochastically, 
    for the EV to be charged. It's assumed to be at the half of the journey and instantaneous.
    5. If E_arrive > SOC_max or < SOC_min: 

Inputs: 

    - Occupancy profile which details if the main driver is at home (1) or not (0) of length N, the number of min 
    considered in the simulation time horizon. 
    - Size  of the EV ['small', 'medium', 'large'] which corresponds on different battery capacities defined in 
    config_init_.py of 37, 60, and 100 kWh. 
    - Driver usage ['short', 'normal', 'long'] which defines de type of driver journeys to simulate. Normal type is 
    the statistical mean daily kilometer: 50 [km/weekday] and 60 [km/weekend-day]. Short corresponding to smaller
    journeys (30% x 50 [km] and 30% x 60 [km]) and long doubling the distances: (200% x 50 [km] and 200% x 60 [km]).  

Outputs:

    It returns several time steps, such as the load profile of the EV charging, the SOC evolution of the car, when 
    the car is plugged, and when a charge event occurs while not home. The load profile associated with the occupancy
    profile could be merged and use for further flexibility working. 


#TO DO:
# add EV_cons in class user instead of passing argument?
# profile de l'année par km/an?
# verif pour tous type de car + usage que c'est bon
# implement probability for size car and driver usage