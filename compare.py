import pandas as pd
import matplotlib.pyplot as plt

fluvius = pd.read_csv(r"C:\Master3\TFE\Fluvius\P6269_1_50_DMK_Sample_Elek.csv",sep=";")

n_day = 31
n_house = 600
fluvius = fluvius[(fluvius['Elektrisch_Voertuig_Indicator']==0) & (fluvius['Warmtepomp_Indicator']==0)]
fluvius_hourly = fluvius.pivot(index="Datum_Startuur", columns = "EAN_ID", values="Volume_Afname_kWh")
del fluvius
print(sum(fluvius_hourly.head(96*n_day).sum(axis=1))*1000/(len(fluvius_hourly.columns)*n_day))
plt.plot(fluvius_hourly.head(96*n_day).sum(axis=1)*4000/len(fluvius_hourly.columns), label = "Fluvius")
print(len(fluvius_hourly.columns))

# Charger le fichier Excel  # Remplacez par le chemin de votre fichier Excel
excel = pd.read_csv(r"C:\Master3\TFE\Results_Boiler\Results035_31d.csv", sep=',')
print(f'Average consumption {excel["Total"].sum() / (n_house*n_day * 4)}')
plt.plot(excel['Total']/n_house, label="Model 50")

excel = pd.read_csv(r"C:\Master3\TFE\Results_Boiler\Results00_31d.csv", sep=',')
print(f'Average consumption {excel["Total"].sum() / (n_house*n_day * 4)}')
plt.plot(excel['Total']/n_house, label="Model 00")

excel = pd.read_csv(r"C:\Master3\TFE\Results_Boiler\Results035_31d_bis.csv", sep=',')
print(f'Average consumption {excel["Total"].sum() / (n_house*n_day * 4)}')
plt.plot(excel['Total']/n_house, label="Model 30")

excel = pd.read_csv(r"C:\Master3\TFE\Results_Boiler\Results038_31d.csv", sep=',')
print(f'Average consumption {excel["Total"].sum() / (n_house*n_day * 4)}')
plt.plot(excel['Total']/n_house, label="Model 38")

plt.legend()
plt.show()

