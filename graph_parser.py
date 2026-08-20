from pathlib import Path

def load_graph():
    nodes = {}
    edge_list = []
    adj_list = {}
    expected_node_count = 0
    expected_edge_count =0

    data_path = Path(__file__).parent / "data" / "USA_BAY_ROAD_with_energy.xy"

    with open(data_path, "r") as file:
        for line in file:
            parts = line.split()

            if not parts:
                continue

            if parts[0] == "nodes":
                expected_node_count = int(parts[1])
                expected_edge_count = int(parts[3])
                continue

            if parts[0] == "v":
                node_id = int(parts[1])
                x = int(parts[2])
                y = int(parts[3])
                elevation = int(parts[4])

                nodes[node_id] = (x, y, elevation)

            elif parts[0] == "e":
                u = int(parts[1])
                v = int(parts[2])
                dist = int(parts[3])
                energy = int(parts[4])

                assert dist >= 0, f"Negative distance on edge {u} -> {v}"

                edge_list.append((u, v, dist, energy))

    for edge in edge_list:
        u = edge[0]
        v, dist, energy = edge[1:]
        
        if u in adj_list:
            adj_list[u].append((v, dist, energy))
        else:
            adj_list[u] = [(v, dist, energy)]

    assert len(nodes) == expected_node_count, f"Number of nodes {len(nodes)} does not match expected number {expected_node_count}"
    assert len(edge_list) == expected_edge_count, f"Number of edges {len(edge_list)} does not match expected number {expected_edge_count}"

    for edge in edge_list:
        u, v = edge[0], edge[1]
        assert u in nodes, f"Source node {u} does not exist"
        assert v in nodes, f"Destination node {v} does not exist"

    return nodes, edge_list, adj_list