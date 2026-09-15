from math import inf, radians, sin, cos, sqrt, atan2
import heapq


def astar(
    nodes,
    adj_list,
    battery_capacity,
    initial_battery,
    total_mass,
    s,
    destination,
    lambda_value,
    g=9.81,
):
    n = len(nodes)

    reduced_cost = [inf] * n
    battery = [-inf] * n
    pred = [None] * n

    reduced_cost[s] = 0
    battery[s] = initial_battery

    pq = []
    expanded = set()

    start_h = heuristic(nodes, s, destination, lambda_value)

    heapq.heappush(pq, (start_h, 0, s))

    while pq:
        _, current_cost, u = heapq.heappop(pq)

        if current_cost != reduced_cost[u]:
            continue

        if u in expanded:
            continue
        expanded.add(u)

        if u == destination:
            break

        for v, _, original_energy, reduced_energy in adj_list.get(u, []):
            energy_spent = original_energy

            new_battery = battery[u] - original_energy

            if new_battery < 0:
                continue

            if new_battery > battery_capacity:
                energy_spent = battery[u] - battery_capacity
                new_battery = battery_capacity

                delta_elevation = nodes[v][2] - nodes[u][2]

                gpe_joules = total_mass * g * delta_elevation
                gpe_wh = gpe_joules / 3600

                reduced_energy = energy_spent - gpe_wh

            new_cost = reduced_cost[u] + reduced_energy

            if new_cost < reduced_cost[v]:
                reduced_cost[v] = new_cost
                battery[v] = new_battery
                pred[v] = u

                h = heuristic(nodes, v, destination, lambda_value)

                if new_battery < h:
                    continue

                priority = new_cost + h

                heapq.heappush(pq, (priority, new_cost, v))

    return reduced_cost, battery, pred


def calculate_lambda(adj_list, eta_e=14.1):
    lambda_value = inf

    for u, edges in adj_list.items():
        for v, dist, _, reduced_energy in edges:
            distance_m = dist / 10

            if distance_m > 0:
                estimated_energy = eta_e * (distance_m / 100)

                lambda_value = min(lambda_value, (reduced_energy / estimated_energy))

    return lambda_value


def haversine_distance(nodes, u, destination):
    scale = 10**6

    lon1 = nodes[u][0] / scale
    lat1 = nodes[u][1] / scale

    lon2 = nodes[destination][0] / scale
    lat2 = nodes[destination][1] / scale

    lon1 = radians(lon1)
    lat1 = radians(lat1)
    lon2 = radians(lon2)
    lat2 = radians(lat2)

    delta_lon = lon2 - lon1
    delta_lat = lat2 - lat1

    a = sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_lon / 2) ** 2

    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    earth_radius = 6371000

    return earth_radius * c


def heuristic(nodes, u, destination, lambda_value, eta_e=14.1):
    distance_m = haversine_distance(nodes, u, destination)

    return lambda_value * eta_e * (distance_m / 100)


if __name__ == "__main__":
    nodes = {0: (0, 0, 0), 1: (0, 0, 0), 2: (0, 0, 0)}

    graph = {0: [(1, 10, 20, 20), (2, 10, 40, 40)], 1: [(2, 10, 10, 10)], 2: []}

    reduced_cost, battery, pred = astar(
        nodes, graph, battery_capacity=100, initial_battery=100, total_mass=1000, s=0
    )

    print("Reduced cost:", reduced_cost)
    print("Battery:", battery)
    print("Pred:", pred)
