import os
import pandas as pd
import matplotlib.dates as mdates
from plots import make_demand_plot
# Définir le dossier contenant les CSV
folder_path = r"C:\Master3\TFE\ULG-Flex-Residential-Load-3phases copy\consumption_with_heating"

# Lister les fichiers du dossier
files = os.listdir(folder_path)
all_dfs = []
df = pd.DataFrame(columns=['Max load [kW]', 'Yearly Consumption [kWh]'], index= range(1,101))
nb_house = len(files)
aggregated = pd.DataFrame()
# Parcourir les fichiers
for file in files:
    if file.endswith(".csv"):  # Vérifie si c'est un fichier CSV
        file_path = os.path.join(folder_path, file)
        number = file.split("_")
        number = number[-1].split(".")[0]
       # print(f"Lecture du fichier : {file_path}")
        df2 = pd.read_csv(file_path, index_col='DateTime')
        aggregated[number]=df2["mult"]
        df.loc[int(number)] = [max(df2["mult"]), sum(df2["mult"])/4]
#df.to_csv(r"C:\Master3\TFE\ULG-Flex-Residential-Load-3phases copy\ThomasCIRED\LoadProfilesResumeModel.csv")
#aggregated.to_excel("Results.xlsx")
aggregated["Total"] = aggregated.sum(axis=1)
print(f'Average yearly consumption [kWh] : {df["Yearly Consumption [kWh]"].sum()/nb_house}')
print(f'Maximum non-coincident demand [kW]:  {df["Max load [kW]"].sum()}')
print(f'Maximum diversified demand[kW]:{max(aggregated["Total"])}')

#aggregated_per_quarter

aggregated.index = pd.to_datetime(aggregated.index)
aggregated["time"]= aggregated.index.time
aggregated = aggregated.copy()
daily_mean = aggregated.groupby('time').mean()['Total']/nb_house
import matplotlib.pyplot as plt
fluvius_file = r"C:\Master3\TFE\Fluvius\P6269_1_50_DMK_Sample_Elek.csv"

fluvius = pd.read_csv(fluvius_file, sep=";")
fluvius_EV =fluvius[((fluvius['Elektrisch_Voertuig_Indicator']==1) & (fluvius['Warmtepomp_Indicator']==0)) & (fluvius['PV-Installatie_Indicator']==0)] 
fluvius = fluvius[((fluvius['Elektrisch_Voertuig_Indicator']==0) & (fluvius['Warmtepomp_Indicator']==0)) & (fluvius['PV-Installatie_Indicator']==0)]
fluvius_hourly = fluvius.pivot(index="Datum_Startuur", columns = "EAN_ID", values="Volume_Afname_kWh")
fluvius_hourly.index = pd.to_datetime(aggregated.index)
print(f'Maximum non-coincident demand fluvius [kW]:  {max(fluvius_hourly.max()*4)}')

fluvius_hourly['Total']=fluvius_hourly.sum(axis=1)
fluvius_hourly["time"]= fluvius_hourly.index+ pd.Timedelta(hours=2)
fluvius_hourly['time']=fluvius_hourly['time'].dt.time


daily_mean_fluvius = fluvius_hourly.groupby('time').mean()['Total']*4/(len(fluvius_hourly.columns)-2)


print(f'Average yearly consumption fluvius [kWh] : {fluvius_hourly["Total"].sum()/(len(fluvius_hourly.columns)-2)}')
print(f'Maximum diversified demand Fluvius [kW]:{max(fluvius_hourly["Total"])*4}')


daily_mean_fluvius.to_csv("C:\\Master3\\TFE\\ULG-Flex-Residential-Load-3phases copy\\ThomasCIRED\\dailyMeanFluvius.csv", index=True)
daily_mean.to_csv("C:\\Master3\\TFE\\ULG-Flex-Residential-Load-3phases copy\\ThomasCIRED\\dailyMeanModel.csv", index=True)

aggregated["month"] = aggregated.index.month
monthly_consumption = aggregated.groupby(['month'])['Total'].sum().reset_index()
monthly_consumption['month_name'] = pd.to_datetime(monthly_consumption['month'], format='%m').dt.month_name()

# Tracer les données

fluvius_hourly['month'] = fluvius_hourly.index.month
monthly_consumption_fluvius = fluvius_hourly.groupby(['month'])['Total'].sum().reset_index()
monthly_consumption_fluvius['month_name'] = pd.to_datetime(monthly_consumption_fluvius['month'], format='%m').dt.month_name()
import numpy as np
bar_width = 0.45
r1 = np.arange(len(monthly_consumption_fluvius['month_name']))
r2 = [x + bar_width for x in r1]



fig,ax = plt.subplots(figsize=(12, 7))
bar1_plot = ax.bar(r1, monthly_consumption['Total']/(nb_house*4),  width=bar_width,label='Model Data')
bar2_plot = ax.bar(r2, monthly_consumption_fluvius['Total']/(len(fluvius_hourly.columns)-2),width=bar_width, label='Fluvius')

ax.set_xlabel(r'Month')
ax.set_ylabel(r'Average total electrical consumption')
ax.set_title(r'Average monthly electical consumption of households')
ax.legend()
ax.set_xticks([r + bar_width / 2 for r in range(len(monthly_consumption_fluvius['month_name']))])
ax.set_xticklabels(monthly_consumption_fluvius['month_name'], rotation=45)
plt.savefig('C:\Master3\TFE\IMAGE\monthly_elec_consumption_with_water_boiler.pdf')



from datetime import datetime, timedelta


start_time = datetime(2023, 1, 1, 0, 0)
end_time = datetime(2023, 1, 1, 23, 45)
time_intervals = [start_time + timedelta(minutes=15 * i) for i in range(96)]

# Création du graphique
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(time_intervals, daily_mean, label='Model Data')
ax.plot(time_intervals, daily_mean_fluvius, label = 'Fluvius Data')

# Configuration de l'axe des x pour afficher uniquement les heures pleines
ax.xaxis.set_major_locator(mdates.HourLocator())  # Une étiquette toutes les heures
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))  # Format HH:M
ax.set_xlim([datetime(2023, 1, 1, 0, 0), datetime(2023, 1, 1, 23, 45 )])
# Rotation des étiquettes pour une meilleure lisibilité
# Ajout des labels et du titre
ax.set_xlabel(r'Hour of the day [h]')
ax.set_ylabel(r'Average power [kW]')
ax.set_ylim(0,2)
plt.grid()
ax.set_title(r"Average daily electricity consumption profile over 1 year without EV ")
ax.legend()

# Affichage du graphique
plt.tight_layout()
plt.savefig('C:\Master3\TFE\IMAGE\Average_daily_consumption.pdf')
#plt.show()

def EV_camparison(fluvius, model_folder, dest_file):

##EV Part
    files = os.listdir(model_folder)
    #Recover peak demand from load profile and yearly consumption
    all_dfs = []
    df = pd.DataFrame(columns=['Max load [kW]', 'Yearly Consumption [kWh]'], index= range(1,101))
    nb_house = len(files)
    aggregated = pd.DataFrame()
    # Parcourir les fichiers
    for file in files:
        if file.endswith(".csv"):  # Vérifie si c'est un fichier CSV
            file_path = os.path.join(folder_path, file)
            number = file.split("_")
            number = number[-1].split(".")[0]
        # print(f"Lecture du fichier : {file_path}")
            df2 = pd.read_csv(file_path, index_col='DateTime')
            aggregated[number]=df2["mult"]+df2['EVCharging']
            df.loc[int(number)] = [max(aggregated[number]), sum(aggregated[number])/4]
    
    
    aggregated["Total"] = aggregated.sum(axis=1)

    print(f'Average yearly consumption [kWh] : {df["Yearly Consumption [kWh]"].sum()/nb_house}')
    print(f'Maximum non-coincident demand [kW]:  {df["Max load [kW]"].sum()}')
    print(f'Maximum diversified demand[kW]:{max(aggregated["Total"])}')

    #aggregated_per_quarter

    aggregated.index = pd.to_datetime(aggregated.index)
    aggregated["time"]= aggregated.index.time
    aggregated = aggregated.copy()
    daily_mean = aggregated.groupby('time').mean()['Total']/nb_house

    fluvius = fluvius.pivot(index="Datum_Startuur", columns = "EAN_ID", values="Volume_Afname_kWh")
    fluvius.index = pd.to_datetime(aggregated.index)

    print(f'Maximum non-coincident demand fluvius [kW]:  {max(fluvius.max()*4)}')

    fluvius['Total']=fluvius.sum(axis=1)
    fluvius["time"]= fluvius.index+ pd.Timedelta(hours=2)
    fluvius['time']=fluvius['time'].dt.time


    daily_mean_fluvius = fluvius.groupby('time').mean()['Total']*4/(len(fluvius.columns)-2)


    print(f'Average yearly consumption fluvius [kWh] : {fluvius["Total"].sum()/(len(fluvius.columns)-2)}')
    print(f'Maximum diversified demand Fluvius [kW]:{max(fluvius["Total"])*4}')

    if dest_file:
        start_time = datetime(2023, 1, 1, 0, 0)
        end_time = datetime(2023, 1, 1, 23, 45)
        time_intervals = [start_time + timedelta(minutes=15 * i) for i in range(96)]

        # Création du graphique
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(time_intervals, daily_mean, label='Model Data')
        ax.plot(time_intervals, daily_mean_fluvius, label = 'Fluvius Data')

        # Configuration de l'axe des x pour afficher uniquement les heures pleines
        ax.xaxis.set_major_locator(mdates.HourLocator())  # Une étiquette toutes les heures
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))  # Format HH:M
        ax.set_xlim([datetime(2023, 1, 1, 0, 0), datetime(2023, 1, 1, 23, 45 )])
        # Rotation des étiquettes pour une meilleure lisibilité
        ax.set_ylim(0,2)
        # Ajout des labels et du titre
        ax.set_xlabel(r'Hour of the day [h]')
        ax.set_ylabel(r'Average power [kW]')
        ax.set_title(r"Average daily electricity consumption profile over 1 year with EV ")
        ax.legend()
        # Affichage du graphique
        plt.grid()
        plt.tight_layout()
        plt.savefig(dest_file)


EV_camparison(fluvius_EV, folder_path, r'C:\Master3\TFE\IMAGE\average_elec_daily_profile_with_EV.pdf')

def make_demand_plot_average(folder_path):
    files = os.listdir(folder_path)
    #Recover peak demand from load profile and yearly consumption
    columns = ['mult','EVCharging','Heating','Hot Water']
    df = pd.DataFrame(columns=columns)
    # Parcourir les fichiers
    i=0
    for file in files:
        if file.endswith(".csv"):  # Vérifie si c'est un fichier CSV
            file_path = os.path.join(folder_path, file)
            df2 = pd.read_csv(file_path, index_col='DateTime')
            if i == 0:
                df = df2
            else:
                df += df2
            i+=1
    
    make_demand_plot(df.index, df, title=r'Aggregation of electrical consumption profile of 100 households for 15 minutes timestep')

make_demand_plot_average(folder_path)