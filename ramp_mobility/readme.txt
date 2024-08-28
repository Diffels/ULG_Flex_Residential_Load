 _______________________________________
|                                       |
| EV module, derived from ramp-mobility |
|_______________________________________|

This module allows to compute stochastically an EV load profile based on an occupancy profile and predefined parameters (type of the car and driver working statut) for a time horizon of 1 day to 1 year, minute per minute.  

Main Assumptions: 

1. The charging pattern is 'uncontrolled', ie soon as the EV come back home, it is charge at nominal charger power until fully charged.
2. Each departure corresponds to a departure with the EV. 
3. At each departure a probability is fixed (depending on the energy available in EV and the energy required for the journey) for the EV to be refiled and charged during this departure.
4. When a charge occurs not at home (see above), a percentage of the full departure time is taken, stochastically, for the EV to be charged. It's assumed to be at the half of the journey and instantaneous.

Inputs: 

Size car [x, y, z] defined in .py + expl
Type Driver [] defined in +expl



#TO DO: maybe set a min time for EV departure, ex if the departure lasts less than 10 min, no EV departure.

# Delete not usefull things such as working statut, windows etc
# Faire varier
    param nb de km (grand cond, moy cond, petit con)
param taille de voiture (kWh/km)

# flexibilité: quand voiture est à la maison et de combien elle doit être rechargée, comment sortir ça
# tab de flexibilité: 

# add EV_cons in class user instead of passing argument?

# profile de l'année par km/an?

# change charger power as input