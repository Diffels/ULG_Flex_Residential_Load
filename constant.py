from StROBe.Data.Appliances import set_appliances

# translation the input variables into standard english to be used in the library:
translate = {
    'dwelling_type': {'Appartement':'1f',
                      "2 façades":'2f',
                      '3 façades':'3f',
                      '4 façades':'4f'},
    'dwelling_member1':{'Aucun':None,
              'Aléatoire':'Random',
              'Travailleur à temps plein':'FTE',
              'Travailleur à temps partiel':'PTE',
              'Enfant':'U12',
              'Retraité':'Retired',
              'Sans emploi':'Unemployed',
              'Etudiant':'School'},
    'dwelling_member2':{'Aucun':None,
              'Aléatoire':'Random',
              'Travailleur à temps plein':'FTE',
              'Travailleur à temps partiel':'PTE',
              'Enfant':'U12',
              'Retraité':'Retired',
              'Sans emploi':'Unemployed',
              'Etudiant':'School'},
    'dwelling_member3':{'Aucun':None,
              'Aléatoire':'Random',
              'Travailleur à temps plein':'FTE',
              'Travailleur à temps partiel':'PTE',
              'Enfant':'U12',
              'Retraité':'Retired',
              'Sans emploi':'Unemployed',
              'Etudiant':'School'},
    'dwelling_member4':{'Aucun':None,
              'Aléatoire':'Random',
              'Travailleur à temps plein':'FTE',
              'Travailleur à temps partiel':'PTE',
              'Enfant':'U12',
              'Retraité':'Retired',
              'Sans emploi':'Unemployed',
              'Etudiant':'School'},
    'dwelling_member5':{'Aucun':None,
              'Aléatoire':'Random',
              'Travailleur à temps plein':'FTE',
              'Travailleur à temps partiel':'PTE',
              'Enfant':'U12',
              'Retraité':'Retired',
              'Sans emploi':'Unemployed',
              'Etudiant':'School'},
    }
year = 2015
defaultcolors = {'Base Load':'#7fe5ca', 
                 'WasherDryer':'#ffb2c8', 
                 'TumbleDryer':'#d5b0fc',
                 'DishWasher':'#ffd0ac',
                 'HeatPumpPower':'#daf3bf', 
                 'DomesticHotWater':'#8be9f9',
                 'EVCharging':'#ffcbff',
                 'BatteryConsumption':'#b0b6fc',
                 'WashingMachine': '#ffffbe'}

special_appliances = ['DishWasher','WasherDryer','TumbleDryer','WashingMachine', 'EVCharging']

StaticLoad = [x for x in set_appliances if (set_appliances[x]['type'] == 'appliance' and x not in special_appliances)]

