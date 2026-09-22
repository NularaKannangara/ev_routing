import heapq
from math import inf


def bicriteria_dijkstra(
    adj_list,
    source,
    destination,
    battery_capacity,
    initial_battery,
):
    labels = {node: [] for node in adj_list}
    labels[source] = [(0, initial_battery)]

    pq = [(0, source, initial_battery)]

    pred = {}
    pred[(source, 0, initial_battery)] = None

    expanded_count = 0

    while pq:
        time_taken, u, remaining_battery = heapq.heappop(pq)

        if (time_taken, remaining_battery) not in labels[u]:
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

            heapq.heappush(pq, (new_time_taken, v, new_remaining_battery))

    return inf, None, pred, None, expanded_count
