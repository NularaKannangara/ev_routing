import heapq
from math import inf


def build_reverse_graph(adj_list):
    reverse_adj = {node: [] for node in adj_list}

    for u in adj_list:
        for v, distance, edge_time, edge_energy in adj_list[u]:
            if v not in reverse_adj:
                reverse_adj[v] = []

            reverse_adj[v].append((u, distance, edge_time, edge_energy))

    return reverse_adj


def build_reverse_reweighted_graph(adj_list, nodes, total_mass, g=9.81):
    reverse_adj = {node: [] for node in adj_list}

    for u, edges in adj_list.items():
        elevation_u = nodes[u][2]
        p_u = total_mass * g * elevation_u / 3600

        for v, distance, edge_time, edge_energy in edges:
            elevation_v = nodes[v][2]
            p_v = total_mass * g * elevation_v / 3600

            reduced_energy = edge_energy + p_u - p_v

            if v not in reverse_adj:
                reverse_adj[v] = []

            reverse_adj[v].append((u, distance, edge_time, edge_energy, reduced_energy))

    return reverse_adj


def compute_time_heuristic(reverse_adj, destination):
    """
    Computes h_T(v) = minimum travel time from v to destination
    ignoring battery constraints.
    """

    h_time = {node: inf for node in reverse_adj}
    h_time[destination] = 0

    pq = [(0, destination)]

    while pq:
        time_so_far, u = heapq.heappop(pq)

        if time_so_far != h_time[u]:
            continue

        for v, _, edge_time, _ in reverse_adj[u]:
            new_time = time_so_far + edge_time

            if new_time < h_time[v]:
                h_time[v] = new_time
                heapq.heappush(pq, (new_time, v))

    return h_time


def compute_energy_lower_bound(
    reverse_reweighted_adj, destination, nodes, total_mass, g=9.81
):
    """
    Computes minimum net-energy cost to the destination using
    non-negative reduced energy costs and Dijkstra.
    """

    reduced_dist = {node: inf for node in reverse_reweighted_adj}
    reduced_dist[destination] = 0

    pq = [(0, destination)]

    while pq:
        dist_u, u = heapq.heappop(pq)

        if dist_u != reduced_dist[u]:
            continue

        for v, _, _, _, reduced_energy in reverse_reweighted_adj[u]:
            if reduced_energy < -1e-10:
                raise ValueError(
                    f"Negative reduced energy on edge {u} -> {v}: {reduced_energy}"
                )

            reduced_energy = max(0.0, reduced_energy)
            new_dist = dist_u + reduced_energy

            if new_dist < reduced_dist[v]:
                reduced_dist[v] = new_dist
                heapq.heappush(pq, (new_dist, v))

    def potential(v):
        elevation = nodes[v][2]
        return total_mass * g * elevation / 3600

    p_destination = potential(destination)

    h_energy = {}

    for v, dist in reduced_dist.items():
        if dist == inf:
            h_energy[v] = inf
        else:
            h_energy[v] = dist - potential(v) + p_destination

    return h_energy


def bicriteria_baum_astar(
    adj_list,
    nodes,
    source,
    destination,
    battery_capacity,
    initial_battery,
    total_mass,
):
    reverse_adj = build_reverse_graph(adj_list)

    reverse_reweighted_adj = build_reverse_reweighted_graph(adj_list, nodes, total_mass)

    h_time = compute_time_heuristic(reverse_adj, destination)

    h_energy = compute_energy_lower_bound(
        reverse_reweighted_adj, destination, nodes, total_mass
    )

    if h_time.get(source, inf) == inf:
        return inf, None, {}, None, 0

    labels = {node: [] for node in adj_list}
    labels[source] = [(0, initial_battery)]

    # Queue: (A* priority, time_taken, vertex, remaining_battery)
    pq = [(h_time[source], 0, source, initial_battery)]

    pred = {(source, 0, initial_battery): None}
    expanded_count = 0

    while pq:
        priority, time_taken, u, remaining_battery = heapq.heappop(pq)

        if (time_taken, remaining_battery) not in labels[u]:
            continue

        if remaining_battery < h_energy.get(u, inf):
            continue

        expanded_count += 1

        if u == destination:
            return (
                time_taken,
                remaining_battery,
                pred,
                (u, time_taken, remaining_battery),
                expanded_count,
            )

        for v, _, edge_time, edge_energy in adj_list.get(u, []):
            new_remaining_battery = remaining_battery - edge_energy

            if new_remaining_battery < 0:
                continue

            new_remaining_battery = min(battery_capacity, new_remaining_battery)

            new_time_taken = time_taken + edge_time

            if new_remaining_battery < h_energy.get(v, inf):
                continue

            dominated = False
            dominated_labels = []

            for existing_time, existing_battery in labels.get(v, []):
                if (
                    existing_time <= new_time_taken
                    and existing_battery >= new_remaining_battery
                ):
                    dominated = True
                    break

                if (
                    new_time_taken <= existing_time
                    and new_remaining_battery >= existing_battery
                ):
                    dominated_labels.append((existing_time, existing_battery))

            if dominated:
                continue

            for label in dominated_labels:
                labels[v].remove(label)

            labels[v].append((new_time_taken, new_remaining_battery))

            pred[(v, new_time_taken, new_remaining_battery)] = (
                u,
                time_taken,
                remaining_battery,
            )

            priority = new_time_taken + h_time.get(v, inf)

            heapq.heappush(pq, (priority, new_time_taken, v, new_remaining_battery))

    return inf, None, pred, None, expanded_count
