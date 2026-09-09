from graph_parser import load_graph
from math import inf

def battery_feasible_bellman_ford(nodes, adj_list, source, destination, battery_capacity, initial_battery):
    n = len(nodes)
    
    energy_cost = [inf] * n
    battery = [-inf] * n
    pred = [None] * n

    energy_cost[source] = 0
    battery[source] = initial_battery

    for _ in range(n-1):
        relaxation_occurred = False

        for u in range(n):
            if energy_cost[u] == inf:
                continue
            for v, _, energy in adj_list.get(u, []):
                energy_spent = energy
                new_battery = battery[u] - energy
                
                if new_battery < 0: 
                    continue
                if new_battery > battery_capacity:
                    energy_spent = battery[u] - battery_capacity
                    new_battery = battery_capacity
            
                if energy_cost[v] > energy_cost[u] + energy_spent:
                    energy_cost[v] = energy_cost[u] + energy_spent
                    battery[v] = new_battery
                    pred[v] = u
                    relaxation_occurred = True
            
        if not relaxation_occurred:
            break
    if energy_cost[destination] == inf:
        return inf, None, []
    
    return energy_cost[destination], battery[destination], pred
                

    

if __name__ == '__main__':
    nodes = {
        0: (0, 0, 0),
        1: (0, 0, 0),
        2: (0, 0, 0)
    }

    graph = {
        0: [
            (1, 10, 20),
            (2, 10, 40)
        ],
        1: [
            (2, 10, 10)
        ],
        2: []
    }

    energy_cost, battery, pred = battery_feasible_bellman_ford(
        nodes,
        graph,
        source=0,
        destination=2,
        battery_capacity=100,
        initial_battery=100
    )

    print("Energy cost:", energy_cost)
    print("Battery:", battery)
    print("Pred:", pred)