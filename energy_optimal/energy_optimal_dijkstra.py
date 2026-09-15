from math import inf
import heapq

def dijkstra(nodes, adj_list, battery_capacity, initial_battery, total_mass, s, destination, g=9.81):
    n = len(nodes)

    reduced_cost = [inf]*n
    battery = [-inf]*n 
    pred = [None]*n
    reduced_cost[s] = 0
    battery[s] = initial_battery
    pq = []
    heapq.heappush(pq, (0,s))

    while len(pq) > 0:
        key, u = heapq.heappop(pq)
        if reduced_cost[u] == key:
            if u == destination:
                break

            for v, _, original_energy, reduced_energy in adj_list[u]:
                energy_spent = original_energy
                
                new_battery = battery[u] - original_energy
                if new_battery < 0: 
                    continue
                if new_battery > battery_capacity:
                    energy_spent = battery[u] - battery_capacity
                    new_battery = battery_capacity
                    
                    delta_elevation = nodes[v][2] - nodes[u][2]
                    gpe_joules = total_mass*g*delta_elevation
                    gpe_wh = gpe_joules / 3600

                    reduced_energy = energy_spent - gpe_wh


                if reduced_cost[v] > reduced_cost[u] + reduced_energy:
                    reduced_cost[v] = reduced_cost[u] + reduced_energy
                    battery[v] = new_battery
                    pred[v] = u
                    heapq.heappush(pq, (reduced_cost[v],v))

    return reduced_cost, battery, pred

if __name__ == '__main__':
    nodes = {
        0: (0, 0, 0),
        1: (0, 0, 0),
        2: (0, 0, 0)
    }

    graph = {
        0: [
            (1, 10, 20, 20),
            (2, 10, 40, 40)
        ],
        1: [
            (2, 10, 10, 10)
        ],
        2: []
    }

    reduced_cost, battery, pred = dijkstra(
        nodes,
        graph,
        battery_capacity=100,
        initial_battery=100,
        total_mass=1000,
        s=0,
        destination=2
    )

    print("Reduced cost:", reduced_cost)
    print("Battery:", battery)
    print("Pred:", pred)