import pandas as pd   
import matplotlib.pyplot as plt  
import seaborn as sns  
import warnings
warnings.filterwarnings("ignore")



def load_data():
  df_load_curves = pd.read_csv('https://github.com/Gurobi/modeling-examples/blob/master/power_generation/demand.csv?raw=true') 

  # select the demand for the chosen day (July 1st, 2011)
  df_subset = df_load_curves[(df_load_curves['YEAR']==2011)&(df_load_curves['MONTH']==7)&(df_load_curves['DAY']==1)] 

  # store the demand to a dicionary
  d = df_subset.set_index(['HOUR']).LOAD.to_dict() 

  H = set(d.keys()) # set of hours in a day (1 through 24)
  df_plant_info = pd.read_csv('https://github.com/Gurobi/modeling-examples/blob/master/power_generation/small_plant_data/plant_capacities.csv?raw=true') # replace "small_plant_data" with "large_plant_data" to use the full dataset

  P = set(df_plant_info['Plant'].unique())                          # set of all power plants

  plant_type = df_plant_info.set_index('Plant').PlantType.to_dict() # plant type for each plant

  P_N = set([i for i in P if plant_type[i]=='NUCLEAR'])             # set of all nuclear plants  

  fuel_type = df_plant_info.set_index('Plant').FuelType.to_dict()   # fuel type for each plant

  df_fuel_costs = pd.read_csv('https://github.com/Gurobi/modeling-examples/blob/master/power_generation/small_plant_data/fuel_costs.csv?raw=true') 
  # df_fuel_costs = pd.read_csv('small_plant_data/fuel_costs.csv') 

  # read the fuel costs and transform it from fuel-type to plant-name
  f = {i: df_fuel_costs[df_fuel_costs['year']==2011].T.to_dict()[9][fuel_type[i]] for i in fuel_type} # dictionary of fuel cost for each plant

  df_oper_costs = pd.read_csv('https://github.com/Gurobi/modeling-examples/blob/master/power_generation/small_plant_data/operating_costs.csv?raw=true')  
  # df_oper_costs = pd.read_csv('small_plant_data/operating_costs.csv')
  o = {i: df_oper_costs[df_oper_costs['year']==2011].T.to_dict()[9][fuel_type[i]] for i in fuel_type} # operating cost/MWh (plant)

  df_startup_costs = pd.read_csv('https://github.com/Gurobi/modeling-examples/blob/master/power_generation/small_plant_data/startup_costs.csv?raw=true')  
  # df_startup_costs = pd.read_csv('small_plant_data/startup_costs.csv')
  s = {i: df_startup_costs[df_startup_costs['year']==2011].T.to_dict()[9][fuel_type[i]] for i in fuel_type} # operating cost/MWh (plant)
  
  t = s.copy() # assume that the cost of shuting down = starting up

  df_health_costs = pd.read_csv('https://github.com/Gurobi/modeling-examples/blob/master/power_generation/small_plant_data/health_costs.csv?raw=true')  
  # df_health_costs = pd.read_csv('small_plant_data/health_costs.csv')
  a = df_health_costs[(df_health_costs['Year']==2007)&(df_health_costs['Day']==1)].set_index(['Plant','Hour']).to_dict()['Cost'] # operating cost/MWh (plant)
  a.update({(i,h): 0 for i in P for h in H if i not in ['Bowen','Jack McDonough','Scherer']})  

  df_plant_info['capacity'] = df_plant_info['Capacity']
  c = df_plant_info.set_index('Plant').capacity.to_dict() # generation capacity  

  m = {i: 0.8 if i in P_N else 0.01 for i in P} # min % generation when on 

  r = {i: 1 if i in ['BIOMASS','GAS','HYDRO','OIL'] else .2 if i in P_N else .25 for i in P}  # ramp up/down speed (plant)  
  
  return P, H, f, a, o, s, t, d, c, m, P_N, r
