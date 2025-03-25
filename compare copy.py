import pandas as pd
import matplotlib.pyplot as plt
import csv
fluvius = pd.read_csv(r"E:\Master3\TFE\Fluvius\P6269_1_50_DMK_Sample_Elek.csv",sep=";")

n_day = 31
print(fluvius.columns)

fluvius_hourly = fluvius[(fluvius['Elektrisch_Voertuig_Indicator']==0) & (fluvius['Warmtepomp_Indicator']==0)]
fluvius_car_noSolar = fluvius[(fluvius['Elektrisch_Voertuig_Indicator']==1) & (fluvius['PV-Installatie_Indicator']==0)]
car_solar = fluvius[(fluvius['Elektrisch_Voertuig_Indicator']==1) & (fluvius['PV-Installatie_Indicator']==1)]

fluvius_hourly.to_csv(r"E:\Master3\TFE\Fluvius\P6269_1_50_DMK_Sample_Elek_NOCAR_NOHP.csv", index=False)
fluvius_car_noSolar.to_csv(r"E:\Master3\TFE\Fluvius\P6269_1_50_DMK_Sample_Elek_CAR_NOSOLAR.csv", index=False)
car_solar.to_csv(r"E:\Master3\TFE\Fluvius\P6269_1_50_DMK_Sample_Elek_CAR_WITH_SOLAR.csv", index=False)


  