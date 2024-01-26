import networkx as nx
import matplotlib.pyplot as plt
from gurobipy import tuplelist

def read_data():
    f = open("ShortestPathDescription.txt", "r")
    line = f.readline()
    line = line.strip('\n')
    data = line.split(':')
    num_nodes = int(data[1])
    line = f.readline()
    line = line.strip('\n')
    data = line.split(':')
    num_arcs = int(data[1])
    line = f.readline()
    line = line.strip('\n')
    data = line.split(':')
    origin = int(data[1])
    line = f.readline()
    line = line.strip('\n')
    data = line.split(':')
    destination = int(data[1])
    line = f.readline()
    line = f.readline()

    links = tuplelist()
    cost  = {}
    while(len(line)):
        line = line.strip('\n')
        data = line.split()
        from_node = int(data[0])
        to_node = int(data[1])
        cost_arc = float(data[2])
        links.append((from_node,to_node))
        cost[from_node, to_node] = cost_arc
        line = f.readline()
    f.close() 
    return num_nodes, links, cost

def create_digraph(num_nodes, links, cost):
    G=nx.DiGraph()
    list_nodes = list(range(1, num_nodes+1))
    G.add_nodes_from(list_nodes)
    for i,j in links:
        G.add_edge(i,j)

    node_pos = {1: (0, 0), 2: (2, 2), 3: (2, -2), 4: (5, 2), 5: (5, -2), 6: (7, 0)}

    node_col = ['white' for node in G.nodes()]
    edge_col = ['black' for edge in G.edges()]

    nx.draw_networkx(G,node_pos, node_color= node_col, node_size=450)
    nx.draw_networkx_edges(G, node_pos,edge_color= edge_col)
    nx.draw_networkx_edge_labels(G, node_pos,font_color='blue', edge_labels=cost)
    plt.axis('off')
    plt.show()

def visualize_final_path(num_nodes, links, cost, x, destination):
    G=nx.DiGraph()
    list_nodes = list(range(1, num_nodes+1))
    G.add_nodes_from(list_nodes)
    for i,j in links:
        G.add_edge(i,j)

    node_pos = {1: (0, 0), 2: (2, 2), 3: (2, -2), 4: (5, 2), 5: (5, -2), 6: (7, 0)}
    red_edges = [(i,j) for i,j in links if x[i,j].x > 0]

    sp = [ i for i,j in links if x[i,j].x > 0 ]
    sp.append(destination)

    node_col = ['white' if not node in sp else 'red' for node in G.nodes()]
    edge_col = ['black' if not edge in red_edges else 'red' for edge in G.edges()]
    nx.draw_networkx(G,node_pos, node_color= node_col, node_size=450)
    nx.draw_networkx_edges(G, node_pos,edge_color= edge_col)
    nx.draw_networkx_edge_labels(G, node_pos,font_color='blue', edge_labels=cost)
    plt.axis('off')
    plt.show()