_____________________________________________________
The Config.json file defines the following variables:
_____________________________________________________

    "nb_days": Number of days [day]
    "year": Year to simulate [year]
    "country": (string) Associated country. Needed in ramp_mobility module. Currently is only working for 'BE' (Belgium).                      
    "nb_households": (int) Households to simulate, ie the number of simulation made.                
    "start_day":(int) Number of the day at which simulation starts. 
    "flex_mode": (string) Flexibility type
        - 'Hours window': is for a flexibility window that is dependent on a time given by the user. For example, if the machine starts at 12pm and the user decides to give a flexibility window of 2h, then the machine will have a flexibility window from 10 to 14h.
        - 'Daily flexible': loads are flexible over a whole day.
        - 'Weekly flexible': loads are flexible over a whole week. For example, a machine initially running on Monday could end up running on Friday.
        - 'Based on consumption': the flexibility window is based on occupancy. It is considered that all machines must be activated manually and that therefore a person must be present at home to activate the machine. However, it is considered that the machine is necessarily launched on the same occupancy slot as initially.
    "flex_rate": Rate of the flexibility for "flex_mode" == "Hours window" [hour]
    "plot": (boolean) Make an interactive plot. 
    "plot_ts": Time step for post-processing plot. [min]                         
               
    "appliances": List of appliances presence probabilities. [0; 1]
    {
        "WashingMachine": [-],
        "TumbleDryer": [-],
        "DishWasher": [-],
        "WasherDryer": [-]
    },               

    "EV_presence": Presence rate of Electrical Vehicle.          
    "prob_EV_size": Probabilities array of EV size: [small, medium, large] cfr readme.txt in ramp_mobility module for more informations. 
    "prob_EV_usage": Probabilities array of EV usage: [short, normal, long] cfr readme.txt in ramp_mobility module for more informations.
    "prob_EV_charger_power": Probabilities array of power charger: [3.7, 7.4, 11, 22] (kW) 
    "EV_km_per_year": Number of kilometers per year [km/year]. Used if it's set greater than 0, instead of EV_usage probabilities array.
    
    "dwelling_nb_compo": Number of resident in considered household. [person] [0; 5]
    "dwelling_member1":	Type of resident 1. Choose between: ('Random', 'FTE' (Full Time Employed), 'PTE' (Partial Time Employed), 'U12' (Under 12 y.o.), 'Retired', 'Unemployed', 'School' (Student))
    "dwelling_member2":	Type of resident 2.     "
    "dwelling_member3":	Type of resident 3.     "
    "dwelling_member4":	Type of resident 4.     "
    "dwelling_member5":	Type of resident 5.     "