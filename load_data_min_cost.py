import gurobipy as gp
def get_data_min_cost():
    # Create dictionaries to capture factory supply limits, depot throughput limits, and customer demand.

    supply = dict({'Austin': 150000,
                'Dallas': 200000})

    through = dict({'Arlington': 70000,
                    'Buda': 50000,
                    'College Station': 100000,
                    'Houston': 40000})

    demand = dict({'C1': 50000,
                'C2': 10000,
                'C3': 40000,
                'C4': 35000,
                'C5': 60000,
                'C6': 20000})

    # Create a dictionary to capture shipping costs.

    arcs, cost = gp.multidict({
        ('Austin', 'Arlington'): 0.5,
        ('Austin', 'Buda'): 0.5,
        ('Austin', 'College Station'): 1.0,
        ('Austin', 'Houston'): 0.2,
        ('Austin', 'C1'): 1.0,
        ('Austin', 'C3'): 1.5,
        ('Austin', 'C4'): 2.0,
        ('Austin', 'C6'): 1.0,
        ('Dallas', 'Buda'): 0.3,
        ('Dallas', 'College Station'): 0.5,
        ('Dallas', 'Houston'): 0.2,
        ('Dallas', 'C1'): 2.0,
        ('Arlington', 'C2'): 1.5,
        ('Arlington', 'C3'): 0.5,
        ('Arlington', 'C5'): 1.5,
        ('Arlington', 'C6'): 1.0,
        ('Buda', 'C1'): 1.0,
        ('Buda', 'C2'): 0.5,
        ('Buda', 'C3'): 0.5,
        ('Buda', 'C4'): 1.0,
        ('Buda', 'C5'): 0.5,
        ('College Station', 'C2'): 1.5,
        ('College Station', 'C3'): 2.0,
        ('College Station', 'C5'): 0.5,
        ('College Station', 'C6'): 1.5,
        ('Houston', 'C3'): 0.2,
        ('Houston', 'C4'): 1.5,
        ('Houston', 'C5'): 0.5,
        ('Houston', 'C6'): 1.5
    })
    return supply, through, demand, arcs, cost