import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import sys
import os
import random
from datetime import datetime

space_heating_dir = os.path.dirname(os.path.realpath(__file__)) # Trouver le chemin du fichier Space_heating.py

# Créer un chemin absolu vers le fichier Excel 'Meteo2022_Liege.xlsx'
meteo_path = os.path.join(space_heating_dir, 'Meteo2022_Liege.xlsx')

# import xlsxwriter
from scipy.integrate import solve_ivp


"FUNCTION NEW METHOD FOR THEORETICAL (DYNAMIC) MODEL"
def theoretical_model_dynamic(shsetting_data, sim_ndays, sim_start_day):
    house = house_type()
    
    dayzone_temperature_set = extract_shsetting_data(shsetting_data, sim_ndays)

    T_set = dayzone_temperature_set
    C = 0.8
    initial_guess = [19,10,10,10] #for T_in; T_wall; T_roof; T_ground

    k_air = 0.024
    k_polystyrene = 0.042 #W / m.K    #internet = 0.028-0.040
    k_laine_roche = 0.035             #internet = 0.030-0.045
    k_liege = 0.039                   #internet = 0.035-0.045
    k_brique = 0.72                   #internet = 0.84
    k_beton = 0.6
    
    #récupère les surfaces des murs et du toit
    Volume = house['Volume (m^3)']
    #récupère les surfaces des murs et du toit
    A_walls = house['Wall surface (m²)']
    
    A_windows_N = house['Northern windows surface (m^2)']
    A_windows_E = house['Eastern windows surface (m^2)']
    A_windows_S = house['Southern windows surface (m^2)']
    A_windows_W = house['Western windows surface (m^2)']
    
    A_windows = A_windows_N + A_windows_E + A_windows_S + A_windows_W
    
    A_roof = house['Ground surface (m^2)']
    A_ground = A_roof

    if house['Year of construction'] == '70-80' :  #in List_70
        e_beton = 0.3

        U_walls = k_beton / e_beton  # W/m^2 K
        U_windows = 6  # simple vitrage
        U_roof = 2
        U_ground = 0.3

    elif house['Year of construction'] == '80-2000' : # in List_80_2000:
        e_polystyrene = 0.05
        e_beton = 0.19
        e_brique = 0.08
        e_air = 0.03

        U_walls = 1 / ((e_beton / k_beton) + (e_polystyrene / k_polystyrene) + (e_air / k_air) + (e_brique / k_brique))
        U_windows = 6  # simple vitrage
        U_roof = 2
        U_ground = 0.3

    elif house['Year of construction'] == '2000-2020' : # in List_2000_2020:
        e_laine_roche = 0.1
        e_beton = 0.19
        e_brique = 0.08
        e_air = 0.03

        U_walls = 1 / ((e_beton / k_beton) + (e_laine_roche / k_laine_roche) + (e_air / k_air) + (e_brique / k_brique))
        U_windows = 3  # double vitrage
        U_roof = 2
        U_ground = 0.3

    elif house['Year of construction'] == 'after 2020' : # in List_2020_now:
        e_liege = 0.2
        e_beton = 0.19
        e_brique = 0.08
        e_air = 0.03

        U_walls = 1 / ((e_beton / k_beton) + (e_liege / k_liege) + (e_air / k_air) + (e_brique / k_brique))
        U_windows = 2  # super double vitrage
        U_roof = 2
        U_ground = 0.3
    
    # #dans la formule (conduction) Q = K*(T_in-T_out), on peut déjà déterminer K
    # K = (A_walls*U_walls) + (A_windows*U_windows) + (A_roof*U_roof)
    
    P_nom = 8000 #DETERMINING THE NOMINAL POWER : 8 kW pour une PAC classique (entre 4 et 15kW normalement)
    
    #En revanche pour déterminer T_out, ça dépend des jours, des heures... on va donc itérer
    #sur toute l'année.
    months = ['jan', 'FEB', 'mar', 'APR', 'MAY', 'jun', 'jul', 'AUG', 'sep', 'oct', 'nov', 'DEC']
    
    hours = generate_numbers_as_strings(24)
    
    P_irradiation = irradiation(A_windows_N,A_windows_E,A_windows_S,A_windows_W, sim_start_day, sim_ndays)
    
    T_hours = temperature_tri(sim_start_day, sim_ndays)
    T_10minutes = [temp for temp in T_hours for _ in range(6)]  # duplique chaque case de T_hours par 6 

    Q_TU = np.zeros(sim_ndays*24*6)
    all_T_in = np.zeros(sim_ndays*24*6)
    all_T_wall = np.zeros(sim_ndays*24*6)
    
    indice_10min = 0

    for day in range(sim_ndays):
        for hour in range(24):  # Chaque jour a 24 heures
            for p in range(6):

                T_out = T_10minutes[indice_10min]

                P_in_addition = P_irradiation[indice_10min]
                
                #-------------------------------------------------

                def equation(t,T):

                    #air :
                    rho_air = 1.225  # kg/m^3
                    cp_air= 1005 #J/(kg.Kelvin)
                    m_a = Volume * rho_air

                    #isolant :
                    cp_polystyrene = 1210  # polystyrene, expanded - Extruded (R-12) Table A.3 p906 heat transfer book  #internet = 1000
                    rho_polystyrene = 55   # polystyrene, expanded - Extruded (R-12) Table A.3 p906 heat transfer book   #internet = 15-30
                    cp_laine_roche = 900   #J/kg K #internet
                    rho_laine_roche = 28   # kg/m^3    #internet = 10-28 --> laine de verre et 25-150 --> laine de roche #internet
                    cp_liege = 1800        #internet = 1600-1900
                    rho_liege = 120        #internet = 65-180

                    #matériaux construction :
                    cp_beton = 840          #internet = 880
                    rho_beton = 2600        #internet = 2400
                    rho_beton_armee = 3000  #internet = 2302 + ou - 23
                    cp_brique = 835         #internet = 840
                    rho_brique = 1920       #internet = 1500-1800

                    #autres paramètres :
                    ICF = 6 # = coefficient de fuite d'air du bâtiment: si ICF plus faible signifie une enveloppe de bâtiment plus étanche à l'air, ce qui réduit les pertes de chaleur par infiltration/exfiltration d'air.
                    phi = 0.5 #terme permettant de savoir à quel point la capacité est accessible sur une journée

                    T_out_moyen = 10 #[°C] durant l'année 2022
                    T_in_wanted = 19 #[°C]
                    v_wind_moyen = 3.5 #[m/s]


                    if house['Year of construction'] == '70-80':
                        e_beton = 0.3

                        # Calcul du taux d'infiltration (ACH) :
                        k1 = 0.1
                        k2 = 0.023  #valeurs de k1, k2 et k3 pour un batiment vieux, très mal isolé
                        k3 = 0.07
                        ACH = 0.4 #k1 + (k2 * (T_set[indice_10min] - T_out_moyen)) + (k3 * v_wind_moyen)

                        # Calcul des capacités :
                        C_wall = cp_beton * rho_beton * e_beton  # J/(K.m^2)    #660000
                        C_roof = 100000  # J/(K.m^2)
                        C_ground = cp_beton * rho_beton_armee * e_beton  # (J/K.m^2)  #valeur calculée pour dalle de 30 cm de béton armé

                        # Calcul de theta :
                        R_tot = e_beton / k_beton
                        e_d = C_wall/(2*cp_beton*rho_beton)
                        R_d = e_d/k_beton
                        theta = R_d/R_tot   # theta petit si bien isolé par l'extérieur

                    elif house['Year of construction'] == '80-2000' :
                        e_beton = 0.19
                        e_polystyrene = 0.05
                        e_air = 0.03
                        e_brique = 0.08
                        e_tot_wall = e_beton + e_polystyrene + e_air + e_brique

                        e_beton_armee = 0.3

                        # Calcul du taux d'infiltration (ACH) :
                        k1 = 0.1
                        k2 = 0.023  # valeurs de k1, k2 et k3 pour un batiment vieux, très mal isolé
                        k3 = 0.07
                        ACH = 0.4 #k1 + (k2 * (T_set[indice_10min] - T_out_moyen)) + (k3 * v_wind_moyen)

                        # Calcul des capacités :
                        C_wall = (cp_brique * rho_brique * e_brique) + (cp_air * rho_air * e_air) + (cp_polystyrene * rho_polystyrene * e_polystyrene) + (cp_beton * rho_beton * e_beton)
                        C_roof = 100000  # J/(K.m^2)
                        C_ground = cp_beton * rho_beton_armee * e_beton_armee  # (J/K.m^2)  #valeur calculée pour dalle de 30 cm de béton armé

                        # Calcul de theta :
                        R_tot = (e_beton / k_beton) + (e_polystyrene / k_polystyrene) + (e_brique / k_brique)
                        R_d = (e_beton / (2*k_beton)) + (e_polystyrene / (2*k_polystyrene)) + (e_brique / (2*k_brique))
                        theta = R_d/R_tot # theta petit si bien isolé par l'extérieur

                    elif house['Year of construction'] == '2000-2020' :
                        e_beton = 0.19
                        e_laine_roche = 0.1
                        e_air = 0.03
                        e_brique = 0.08

                        e_beton_armee = 0.3

                        # Calcul du taux d'infiltration (ACH) :
                        k1 = 0.1
                        k2 = 0.017  # valeurs de k1, k2 et k3 pour un batiment normalement isolé
                        k3 = 0.049
                        ACH = k1 + (k2 * (T_set[indice_10min] - T_out_moyen)) + (k3 * v_wind_moyen)

                        # Calcul des capacités :
                        C_wall = (cp_brique * rho_brique * e_brique) + (cp_air * rho_air * e_air) + (cp_laine_roche * rho_laine_roche * e_laine_roche) + (cp_beton * rho_beton * e_beton)
                        C_roof = 100000  # J/(K.m^2)
                        C_ground = cp_beton * rho_beton_armee * e_beton_armee  # (J/K.m^2)  #valeur calculée pour dalle de 30 cm de béton armé

                        # Calcul de theta :
                        R_tot = (e_beton / k_beton) + (e_laine_roche / k_laine_roche) + (e_brique / k_brique)
                        R_d = (e_beton / (2 * k_beton)) + (e_laine_roche  / (2 * k_laine_roche)) + (e_brique / (2 * k_brique))
                        theta = R_d / R_tot  # theta petit si bien isolé par l'extérieur

                    elif house['Year of construction'] == 'after 2020' :
                        e_beton = 0.19
                        e_liege = 0.2
                        e_air = 0.03
                        e_brique = 0.08

                        e_beton_armee = 0.3

                        # Calcul du taux d'infiltration (ACH) :
                        k1 = 0.1
                        k2 = 0.011  # valeurs de k1, k2 et k3 pour un batiment récent, très très bien isolé
                        k3 = 0.034
                        ACH = k1 + (k2 * (T_set[indice_10min] - T_out_moyen)) + (k3 * v_wind_moyen)

                        # Calcul des capacités :
                        C_wall = (cp_brique * rho_brique * e_brique) + (cp_air * rho_air * e_air) + (cp_liege * rho_liege * e_liege) + (cp_beton * rho_beton * e_beton)
                        C_roof = 100000  # J/(K.m^2)
                        C_ground = cp_beton * rho_beton_armee * e_beton_armee  # (J/K.m^2)  #valeur calculée pour dalle de 30 cm de béton armé

                        # Calcul de theta :
                        R_tot = (e_beton / k_beton) + (e_liege / k_liege) + (e_brique / k_brique)
                        R_d = (e_beton / (2 * k_beton)) + (e_liege / (2 * k_liege)) + (e_brique / (2 * k_brique))
                        theta = R_d / R_tot  # theta petit si bien isolé par l'extérieur


                    T_in,T_wall,T_roof,T_ground = T
                    
                    Q_infiltration = (ACH/6)*Volume*rho_air*cp_air*(T_in - T_out)/600 #divide by 600 (10minutes) and divide ACH by 6 because it s air change per hour
                    
                    Q_cond_ground = (U_roof / theta) * A_roof * (T_ground - T_in)
                    Q_cond_walls = (U_walls / theta) * A_walls * (T_wall - T_in)
                    Q_cond_windows = U_windows*A_windows*(T_out-T_in)
                    
                    if(abs(T_set[indice_10min]-T_in) <= 0.5):  #if we are close enough to set point temperature
                        Q_TU= 0
                    else : 
                        Q_TU = (max(min(C*(T_set[indice_10min]-T_in)*P_nom,P_nom),0)) #C=0.5 to decrease the reaction of the thermal unit’s power
                    #PQ on considère plus les pertes de chaleur via le toit ? Car il ya une équation diff rien que pour le toit
                    
                    Q_cond = Q_cond_ground+Q_cond_walls+Q_cond_windows
                    # regarder pour avoir aux alentours de 3 m/s pour notre jour sans soleil --> jour à considérer est le 25/01/2022 avec moyenne de vent de 1.175 m/s
                    
                    dTin_dt = (1/(m_a*cp_air*ICF))*(Q_TU #thermal unit
                                                    + P_in_addition # Lights,people,appliances & irradiation
                                                    + Q_cond #conduction
                                                    - Q_infiltration) #exfiltration
                        
                    dTwall_dt = (((U_walls/(1-theta))*A_walls*(T_out-T_wall))-((U_walls/theta)*A_walls*(T_wall-T_in)))/(phi*C_wall*A_walls)

                    dTroof_dt = (((U_roof / (1 - theta)) * A_roof * (T_out - T_roof)) - ((U_roof / theta) * A_roof * (T_roof - T_in))) / (phi * C_roof * A_roof)

                    dTground_dt = (((U_ground / (1 - theta)) * A_ground * (T_out - T_ground)) - ((U_ground / theta) * A_ground * (T_ground - T_in))) / (phi * C_ground * A_ground)

                    return [dTin_dt,dTwall_dt,dTroof_dt,dTground_dt]

            #-------------------------------------------------


                time_points = [0,600] #for each second during 10 min
                
                sol = solve_ivp(equation, time_points, initial_guess)
                T_in_start = sol.y[0][0] #temperature at the start of the hour
                T_in_end = sol.y[0][-1] #temperature at the end of the hour
                
                T_wall_start = sol.y[1][0]
                T_wall_end = sol.y[1][-1]
                initial_guess[0] = T_in_end  #condition limite pour pour T_in pour l'heure suivante
                
                T_in = (T_in_start+T_in_end)/2
                T_wall = (T_wall_start+T_wall_end)/2
                
                if(abs(T_set[indice_10min]-T_in) <= 0.5):  #if we are close enough to set point temperature
                    Q_TU[indice_10min]= 0
                else : 
                    Q_TU[indice_10min] = (max(min(C*(T_set[indice_10min]-T_in)*P_nom,P_nom),0))/1000 #en kW

                if(Q_TU[indice_10min] <= 0):
                    Q_TU[indice_10min] = 0

                all_T_in[indice_10min] = T_in
                all_T_wall[indice_10min] = T_wall


                #-----------------------------------------------------------------------------------------------

                indice_10min += 1


    #-------------------- PLOT ON sim_ndays ------------------------------------
    # time_steps_per_day = 144
    # total_steps = sim_ndays * time_steps_per_day

    # # PLOT
    # jours = ['Day ' + str(i+1) for i in range(sim_ndays)]  # Etiquettes pour les jours

    # # PLOT POWER AND T_OUT VS TIME
    # fig, ax1 = plt.subplots()

    # # Tracer les données de consommation d'énergie sur l'axe y1 avec un label
    # ax1.plot(range(total_steps), Q_TU, 'black')
    # ax1.set_ylabel('Thermal load [kW]', color='black')
    # ax1.fill_between(range(total_steps), Q_TU, color='black', alpha=0.8)

    # # Créer un deuxième axe des ordonnées pour les données de température
    # ax2 = ax1.twinx()

    # ax2.plot(range(total_steps), T_10minutes, color='red', label=r'T$_{out}$ [°C]')
    # ax2.plot(range(total_steps), all_T_in, color='orange', label=r'T$_{in}$ [°C]')
    # ax2.plot(range(total_steps), T_set, color='green', label=r'T$_{set}$ [°C]')
    # ax2.set_ylabel('Temperature [°C]', color='black')

    # # Ajustement des ticks de l'axe des abscisses
    # num_ticks = sim_ndays  # Afficher un tick pour chaque jour
    # tick_positions = np.linspace(0, total_steps, num_ticks)
    # ax1.set_xticks(tick_positions)
    # ax1.set_xticklabels(jours)

    # # Ajouter la légende
    # lines_1, labels_1 = ax1.get_legend_handles_labels()
    # lines_2, labels_2 = ax2.get_legend_handles_labels()
    # lines = lines_1 + lines_2
    # labels = labels_1 + labels_2
    # legend = ax1.legend(lines, labels, loc='upper right')

    # legend.set_frame_on(True)  # Activer la bordure
    # legend.get_frame().set_edgecolor('black')  # Couleur de la bordure
    # legend.get_frame().set_facecolor('white')

    # # Activer la grille sur l'axe principal
    # ax1.grid(True, alpha=0.3)
    
    # # Afficher le plot
    # plt.show()

    #--------------------------------------------------------

    Q_theoretical_cumulated = calculate_total_energy_demand(Q_TU)
    
    # print('❂ Energy consumption over a year for the space heating =', Q_theoretical_cumulated, 'MWh\n')
    
    return Q_TU



"------------------------------------------------------------------------------------------------------"
"FUNCTION THAT GIVES A HOUSE AND ITS GEOMETRY"
def house_type():
    # Listes de données ajustées
    list_built_year = ['70-80', '80-2000', '2000-2020', 'after 2020']
    list_areas = {
        1: [90, 100, 110, 120, 130, 140, 150], # Maisons de plain-pied (1 étage)
        2: [60, 70, 80, 90, 100, 110],         # Maisons à 2 étages
        3: [50, 60, 70, 80, 90]                # Maisons à 3 étages
    }
    list_heights = {
        1: 2.5,  # Maisons de plain-pied
        2: 5,  # Maisons à 2 étages
        3: 7.5   # Maisons à 3 étages
    }

    # Choisir un nombre d'étages
    floors = random.choice([1, 2, 3])
    
    # Sélection aléatoire de la surface et de la hauteur en fonction des étages
    area = random.choice(list_areas[floors])  
    height = list_heights[floors]
    
    # Sélection aléatoire du PEB
    built_year = random.choice(list_built_year)

    # Calculs
    volume = area * height
    perimeter = 4 * (area ** 0.5)  # assume area to be a square 
    wall_surface = perimeter * height  # Surface totale des murs
    window_surface_north = random.uniform(0.1, 0.2) * wall_surface / 4
    window_surface_south = random.uniform(0.1, 0.3) * wall_surface / 4
    window_surface_east = random.uniform(0.1, 0.3) * wall_surface / 4
    window_surface_west = random.uniform(0.1, 0.3) * wall_surface / 4

    print('House generated and its caracteristics : ')
    print(f" - Year of construction: {built_year}")
    print(f" - Ground surface (m^2): {area}")
    print(f" - Number of floors: {floors}")
    print(f" - Volume (m^3): {volume}")

    
    # ASSUMPTION : only the half of the house is heated , thus the house is shorthened by half
    area = area/2
    perimeter = 4 * (area ** 0.5)  # assume area to be a square 
    wall_surface = perimeter * height  # Surface totale des murs
    window_surface_north = random.uniform(0.1, 0.2) * wall_surface / 4
    window_surface_south = random.uniform(0.1, 0.3) * wall_surface / 4
    window_surface_east = random.uniform(0.1, 0.3) * wall_surface / 4
    window_surface_west = random.uniform(0.1, 0.3) * wall_surface / 4

    return {
        'Number of floors': floors,
        'Ground surface (m^2)': area,
        'Volume (m^3)': volume,
        'Wall surface (m²)': wall_surface,
        'Northern windows surface (m^2)': window_surface_north,
        'Southern windows surface (m^2)': window_surface_south,
        'Eastern windows surface (m^2)': window_surface_east,
        'Western windows surface (m^2)': window_surface_west,
        'Year of construction': built_year
    }

"------------------------------------------------------------------------------------------------------"
def irradiation(A_N,A_E,A_S,A_W, start_day, n_days):
    
    irr_n,irr_e,irr_s,irr_w = irradiation_meteo(start_day, n_days) 
    irr_n_duplicate = [elem for elem in irr_n for _ in range(6)]
    irr_e_duplicate = [elem for elem in irr_e for _ in range(6)]
    irr_s_duplicate = [elem for elem in irr_s for _ in range(6)]
    irr_w_duplicate = [elem for elem in irr_w for _ in range(6)]
    
    irr_n_duplicate = np.array(irr_n_duplicate)
    irr_e_duplicate = np.array(irr_e_duplicate)
    irr_s_duplicate = np.array(irr_s_duplicate)
    irr_w_duplicate = np.array(irr_w_duplicate)

    SF = 0.3
    # SF = 0.5
    
    Q_dot_North = A_N*irr_n_duplicate*SF
    Q_dot_East = A_E*irr_e_duplicate*SF
    Q_dot_West = A_W*irr_w_duplicate*SF
    Q_dot_South = A_S*irr_s_duplicate*SF
    
    Q_TOT = np.zeros(len(Q_dot_North))
    
    for i in range (len(Q_dot_North)):
        Q_TOT[i] = Q_dot_North[i]+Q_dot_East[i]+Q_dot_South[i]+Q_dot_West[i]

    return Q_TOT

    
"------------------------------------------------------------------------------------------------------"

"FUNCTION THAT TAKES A DATE AS A PARAMETER AND RETURNS THE NUMBER OF HOURS"
"IN THE YEAR WE NEED TO REACH THIS DATE."
def determineIndice(date):
    day = date[0:2]
    month = date[3:5]
    hours = date[9:11]
    
    dayNum = int(day)
    monthNum = int(month)
    hoursNum = int(hours)
    
    months = [31,28,31,30,31,30,31,31,30,31,30,31]
    
    numberOfDayTOT = dayNum-1
    for i in range (monthNum-1):
        numberOfDayTOT+=months[i]
    
    indice_bis = numberOfDayTOT*24+(hoursNum-1)
    
    return indice_bis

"------------------------------------------------------------------------------------------------------"



"FUNCTION CALCULATING TOTAL HEAT DEMAND OVER A YEAR"
def calculate_total_energy_demand(Q_10min_theoretical):
    Q_theoretical_cumulated = 0
    for b in range (0,len(Q_10min_theoretical)):
        Q_theoretical_cumulated+= Q_10min_theoretical[b]
        
    Q_theoretical_cumulated = Q_theoretical_cumulated/(1000*6)  #car toutes les 10min et en kWh

    return Q_theoretical_cumulated #EN MWh
"------------------------------------------------------------------------------------------------------"



"FUNCTION USED TO GET A 8760x1 TABLE CONTAINING THE TEMPERATURES ON THE SART TILMAN CAMPUS ON A HOURLY BASIS"
def temperature_tri(start_day, n_days) :
    
    meteo = pd.read_excel(meteo_path, engine='openpyxl')
    
    months = ['jan', 'FEB', 'mar', 'APR', 'MAY', 'jun', 'jul', 'AUG', 'sep', 'oct', 'nov', 'DEC']
    days_in_month = {'jan': 31, 'FEB': 28, 'mar': 31, 'APR': 30, 'MAY': 31, 'jun': 30,
                     'jul': 31, 'AUG': 31, 'sep': 30, 'oct': 31, 'nov': 30, 'DEC': 31}

    hours_bis = [i for i in range(24)]
    
    Temp = []
    
    current_day = 0  # Compte le jour en cours depuis le début de l'année
    t = 0  # Compte le nombre d'heures traitées
    
    for m in months:
        days = days_in_month[m]
        
        for d in range(1, days+1):
            current_day += 1
            
            # On commence à partir du jour `start_day`
            if current_day < start_day:
                continue
            
            # Arrêter après `n_days`
            if current_day >= start_day + n_days:
                break

            if m == 'FEB' or m == 'APR' or m == 'MAY' or m == 'AUG' or m == 'DEC':
                lign = f'{d:02d}-{m}-2021'
                day_lign = meteo.loc[meteo['Date'] == lign]
            else:
                lign = f'{d:02d}-{m}-21'
                real_date = datetime.strptime(lign, '%d-%b-%y')
                day_lign = meteo.loc[meteo['Date'] == real_date]

            # Ajouter les températures pour chaque heure du jour
            for h in hours_bis:
                try:
                    temperature = day_lign['Temperature C'].values[h]  
                    Temp.append(temperature)
                except IndexError:
                    print(f"Erreur à l'heure {h} du jour {d}-{m}: donnée manquante.")
                t += 1

            # Vérifier si on a extrait assez d'heures
            if len(Temp) >= n_days * 24:
                break

    return np.array(Temp)
"------------------------------------------------------------------------------------------------------"



"FUNCTION USED TO GET A 8760x1 TABLE CONTAINING THE IRRADIATIONS (in Watts) ON THE SART TILMAN CAMPUS ON A HOURLY BASIS"
def irradiation_meteo(start_day, n_days) :
    
    meteo = pd.read_excel(meteo_path, engine='openpyxl')
    
    months = ['jan', 'FEB', 'mar', 'APR', 'MAY', 'jun', 'jul', 'AUG', 'sep', 'oct', 'nov', 'DEC']
    days_in_month = {'jan': 31, 'FEB': 28, 'mar': 31, 'APR': 30, 'MAY': 31, 'jun': 30,
                     'jul': 31, 'AUG': 31, 'sep': 30, 'oct': 31, 'nov': 30, 'DEC': 31}

    hours_bis = [i for i in range(24)]  # Les heures de la journée (24 heures)
    
    # Initialisation des tableaux pour les irradiations
    irra_north = []
    irra_east = []
    irra_south = []
    irra_west = []
    
    current_day = 0  # Compteur de jour depuis le début de l'année
    t = 0  # Compteur pour les heures cumulées

    # Boucle à travers chaque mois et chaque jour
    for m in months:
        days = days_in_month[m]
        
        for d in range(1, days + 1):
            current_day += 1
            
            # Commencer à partir du jour `start_day`
            if current_day < start_day:
                continue
            
            # Arrêter l'extraction après avoir atteint le dernier jour souhaité
            if current_day >= start_day + n_days:
                break

            # Sélectionner la ligne de la date correspondante dans le fichier météo
            if m == 'FEB' or m == 'APR' or m == 'MAY' or m == 'AUG' or m == 'DEC':
                lign = f'{d:02d}-{m}-2021'
                day_lign = meteo.loc[meteo['Date'] == lign]
            else:
                lign = f'{d:02d}-{m}-21'
                real_date = datetime.strptime(lign, '%d-%b-%y')
                day_lign = meteo.loc[meteo['Date'] == real_date]

            # Extraire les irradiations pour chaque heure de la journée
            for h in hours_bis:
                try:
                    i_n = day_lign['I_north W/m²'].values[h]
                    i_e = day_lign['I_east W/m²'].values[h]
                    i_s = day_lign['I_south W/m²'].values[h]
                    i_w = day_lign['I_west W/m²'].values[h]

                    # Ajouter les valeurs aux listes respectives
                    irra_north.append(i_n)
                    irra_east.append(i_e)
                    irra_south.append(i_s)
                    irra_west.append(i_w)

                    t += 1
                except IndexError:
                    print(f"Erreur à l'heure {h} du jour {d}-{m}: donnée manquante.")

            # Si on a déjà extrait assez d'heures, arrêter l'extraction
            if len(irra_north) >= n_days * 24:
                break

    # Conversion des listes en tableaux NumPy pour les retourner
    return np.array(irra_north), np.array(irra_east), np.array(irra_south), np.array(irra_west)
"------------------------------------------------------------------------------------------------------"



"FUNCTION USED TO GENERATE A MONTH BASED ON A NUMBER OF DAY n (February->28, January->31, ...)"
def generate_numbers_as_strings(n):
    
    numbers_as_strings = []

    for i in range(1, n + 1):
        number_string = str(i).zfill(2)
        numbers_as_strings.append(number_string)

    return numbers_as_strings
"------------------------------------------------------------------------------------------------------"
def extract_shsetting_data(shsetting_data, n_days):

    start_index = 0  # start_day - 1 pour convertir en index (0-based), 144 pas de temps dans un jour
    end_index = n_days * 144

    selected_data = shsetting_data[start_index:end_index]
    
    return selected_data
"------------------------------------------------------------------------------------------------------"
"CONVERT kWh of space heating into "
def calculate_electric_demand(heat_demand, external_temperature):
    if external_temperature > 10:
        cop = 4
    elif 5 < external_temperature <= 10:
        cop = 3.5
    elif 0 < external_temperature <= 5:
        cop = 3
    else:
        cop = 2.5
    
    electric_demand = heat_demand / cop
    return electric_demand