from time import perf_counter
from math import isclose

from utils.graph_parser import load_graph
from utils.construct_path import reconstruct_path

from energy_optimal.reweight_graph import reweight
from energy_optimal.battery_feasible_baseline import battery_feasible_bellman_ford
from energy_optimal.energy_optimal_dijkstra import dijkstra
from energy_optimal.energy_optimal_astar import astar, calculate_lambda


def reconstruct_path(pred, source, destination):
    path = []
    total_energy = 0

    current = destination

    while current != source:
        if pred[current] is None:
            return None, None

        previous, energy_spent = pred[current]

        path.append(current)
        total_energy += energy_spent

        current = previous

    path.append(source)
    path.reverse()

    return path, total_energy


def run_query(
    nodes,
    adj_list,
    reweighted_graph,
    source,
    destination,
    battery_capacity,
    initial_battery,
    total_mass,
    lambda_value,
):
    results = {}

    # -----Bellman-Ford-----
    start = perf_counter()

    bf_cost, bf_battery, bf_pred, bf_attempts = battery_feasible_bellman_ford(
        nodes,
        adj_list,
        source,
        destination,
        battery_capacity,
        initial_battery,
    )

    bf_runtime = perf_counter() - start

    bf_path, bf_actual_energy = reconstruct_path(
        bf_pred,
        source,
        destination,
    )

    results["bellman_ford"] = {
        "energy": bf_actual_energy,
        "runtime": bf_runtime,
        "relaxation_attempts": bf_attempts,
        "path": bf_path,
    }

    # -----Dijkstra-----
    start = perf_counter()

    d_cost, d_battery, d_pred, d_expanded = dijkstra(
        nodes,
        reweighted_graph,
        battery_capacity,
        initial_battery,
        total_mass,
        source,
        destination,
    )

    d_runtime = perf_counter() - start

    d_path, d_actual_energy = reconstruct_path(
        d_pred,
        source,
        destination,
    )

    results["dijkstra"] = {
        "energy": d_actual_energy,
        "runtime": d_runtime,
        "expanded": d_expanded,
        "path": d_path,
    }

    # -----A*-----

    start = perf_counter()

    a_cost, a_battery, a_pred, a_expanded = astar(
        nodes,
        reweighted_graph,
        battery_capacity,
        initial_battery,
        total_mass,
        source,
        destination,
        lambda_value,
    )

    a_runtime = perf_counter() - start

    a_path, a_actual_energy = reconstruct_path(
        a_pred,
        source,
        destination,
    )

    results["astar"] = {
        "energy": a_actual_energy,
        "runtime": a_runtime,
        "expanded": a_expanded,
        "path": a_path,
    }

    return results


def print_results(results):
    print("\n--- Bellman-Ford ---")
    print("Energy:", results["bellman_ford"]["energy"])
    print("Runtime:", results["bellman_ford"]["runtime"])
    print(
        "Relaxation attempts:",
        results["bellman_ford"]["relaxation_attempts"],
    )

    print("\n--- Dijkstra ---")
    print("Energy:", results["dijkstra"]["energy"])
    print("Runtime:", results["dijkstra"]["runtime"])
    print("Nodes expanded:", results["dijkstra"]["expanded"])

    print("\n--- A* ---")
    print("Energy:", results["astar"]["energy"])
    print("Runtime:", results["astar"]["runtime"])
    print("Nodes expanded:", results["astar"]["expanded"])


def check_correctness(results):
    bf_energy = results["bellman_ford"]["energy"]
    d_energy = results["dijkstra"]["energy"]
    a_energy = results["astar"]["energy"]

    if bf_energy is None or d_energy is None or a_energy is None:
        print("\nAt least one algorithm did not find a feasible path.")
        return

    bf_d_same = isclose(
        bf_energy,
        d_energy,
        rel_tol=1e-9,
        abs_tol=1e-6,
    )

    bf_a_same = isclose(
        bf_energy,
        a_energy,
        rel_tol=1e-9,
        abs_tol=1e-6,
    )

    d_a_same = isclose(
        d_energy,
        a_energy,
        rel_tol=1e-9,
        abs_tol=1e-6,
    )

    print("\n--- Correctness check ---")
    print("Bellman-Ford == Dijkstra:", bf_d_same)
    print("Bellman-Ford == A*:", bf_a_same)
    print("Dijkstra == A*:", d_a_same)


def print_comparison(results):
    d_runtime = results["dijkstra"]["runtime"]
    a_runtime = results["astar"]["runtime"]

    d_expanded = results["dijkstra"]["expanded"]
    a_expanded = results["astar"]["expanded"]

    print("\n--- Dijkstra vs A* ---")

    if a_runtime > 0:
        speedup = d_runtime / a_runtime
        print("A* speedup:", speedup)

    if d_expanded > 0:
        expansion_reduction = (d_expanded - a_expanded) / d_expanded * 100

        print("Expansion reduction:", expansion_reduction, "%")


if __name__ == "__main__":

    # Change these to the values you are using
    # in your research model.
    TOTAL_MASS = 2000
    BATTERY_CAPACITY = 73000
    INITIAL_BATTERY = 73000

    print("Loading graph...")

    nodes, edge_list, adj_list = load_graph()

    print("Graph loaded")
    print("Nodes:", len(nodes))
    print("Edges:", len(edge_list))

    print("\nReweighting graph...")

    reweighted_graph = reweight(
        nodes,
        adj_list,
        TOTAL_MASS,
    )

    print("Calculating lambda...")

    lambda_value = calculate_lambda(reweighted_graph)

    print("Lambda:", lambda_value)

    # Start with ONE query.
    # Once this works, we can generate many queries.
    source = 0
    destination = 321269

    print(f"\nRunning query {source} -> {destination}...")

    results = run_query(
        nodes,
        adj_list,
        reweighted_graph,
        source,
        destination,
        BATTERY_CAPACITY,
        INITIAL_BATTERY,
        TOTAL_MASS,
        lambda_value,
    )

    print_results(results)

    check_correctness(results)

    print_comparison(results)
