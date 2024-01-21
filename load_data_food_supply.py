import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt

class Load_Data():

    def __init__(self):
        # Load the data
        self.node_types = pd.read_csv('https://raw.githubusercontent.com/Gurobi/modeling-examples/master/food_program/data/node_types.csv') # Dataframe containing all nodes
        self.edge_costs = pd.read_csv('https://raw.githubusercontent.com/Gurobi/modeling-examples/master/food_program/data/edge_costs.csv') # Dataframe containing all edge costs associated with the nodes
        self.nutrient_requirements = pd.read_csv('https://raw.githubusercontent.com/Gurobi/modeling-examples/master/food_program/data/nutrient_requirements.csv', index_col=False) #  Dataframe containing nutritional information. An average person has specific minimum limits on several nutrient types
        self.food_nutrition = pd.read_csv('https://raw.githubusercontent.com/Gurobi/modeling-examples/master/food_program/data/food_nutrition.csv', index_col=False) # Dataframe containing the nutritional content of each food type.
        self.df_food_costs = pd.read_csv('https://raw.githubusercontent.com/Gurobi/modeling-examples/master/food_program/data/food_costs.csv') # Dataframe containing procurement cost for a subset of food type that varies depending on supplier city. 
        self.international_food_price = pd.read_csv('https://raw.githubusercontent.com/Gurobi/modeling-examples/master/food_program/data/food_internationalprice.csv').set_index('Food')['InternationalPrice'].to_dict() # DataFrame containing rest of the food types and suppliers 
        
        self.demand = None
        self.t = None 
        self.edges = None 
        self.G = nx.DiGraph() 
        self.N = None
        self.N_S = None
        self.N_TS = None
        self.N_B = None
        self.U = None
        self.m = None
        self.F = None
        self.v = None
        self.p = None


    def load(self):
    
        # Calculate the total number of nodes, number of suppliers, transit hubs and beneficiary camps. 
        self.N = set(self.node_types['Name'])
        self.N_S = set(s[:-2] for s in self.N if s[-2:] == ' S') 
        self.N_TS = set(s[:-3] for s in self.N if s[-2:] == 'TS') 
        self.N_B = set(s[:-2] for s in self.N if s[-1] == 'D') 
        self.N = self.N_S.union(self.N_TS,self.N_B)  # set of all cities
        self.demand = {i: self.node_types.set_index('Name').stack().to_dict()[i+' D','Demand'] for i in self.N_B}


        # Create a dictionary 't' with keys as the edges and values as the travel cost for each edge. 'edges' contains the list of all the edges 
        self.t = self.edge_costs.set_index(['A','B']).tCost.to_dict() 
        self.edges = list(self.t.keys())

        # Create an empty directed graph, add edges to the graph. This step automatically creates the nodes as well
        self.G = nx.DiGraph() 
        self.G.add_edges_from(self.edges) 

        # Create 'U', a set of all nutrients, and a dicionary 'm' containing minimum nutritional requirement per person 
        self.U = self.nutrient_requirements.columns.values.tolist()
        self.U.remove('Type')
        self.m = {u: self.nutrient_requirements.to_dict()[u][0] for u in self.U}

        # Create 'F', a set of Food Types, and a dicionary 'v' containing nutrional content in each food type
        self.F = set(self.food_nutrition['Food'])
        self.v = self.food_nutrition.set_index('Food').stack().to_dict()

        # Create 'p', the mean historical food costs. The data from 'food_costs.csv' only contains a subset of all food types and supplier cities. 
        # For the rest of the food types and suppliers, we set their procurement costs to be the international average prices derived from the 'food_internationalprice.csv' as shown below. 
        # Due to this limitation in data availability, we assume that the prices are constant for these food types and cities.
        self.p = self.df_food_costs.set_index(['supplier','food'])['Mean'].to_dict()
        self.p.update({(i,f): self.international_food_price[f] for f in self.F for i in self.N_S if (i,f) not in self.p})

        return self.N, self.N_S, self.N_TS, self.N_B, self.demand, self.t, self.edges, self.G, self.U, self.m, self.F, self.v, self.p

    def plot(self):
        # Plot the Digraph
        plt.figure(figsize=(20, 20))
        color_map = ['green' if (i in self.N_S and i not in self.N_B) else 'red' if (i in self.N_B and i not in self.N_S) else 'blue' if (i in self.N_B and i in self.N_S) else 'lightblue' for i in self.G.nodes()]
        nx.draw(self.G, pos = nx.nx_pydot.graphviz_layout(self.G),node_color=color_map, node_size=900, linewidths=.25, width=1, font_size=25, font_weight='bold', with_labels=True, arrowsize=50, verticalalignment='top', horizontalalignment='right')
        nx.draw_networkx_edge_labels(self.G, pos = nx.nx_pydot.graphviz_layout(self.G), edge_labels = self.t,  font_size=20)
        print("Legend - Green node: Only a supplier, Red node: Only a beneficiary, Blue node: Both a supplier and a beneficiary. \nThe transportation cost for each edge is also shown.")
        plt.show()

