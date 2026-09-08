def reweight(nodes, adj_list, total_mass, g=9.81):
    reweighted_graph = {}

    for u, edges in adj_list.items():
        reweighted_graph[u] = []
        elevation_u = nodes[u][2]

        for v,dist,energy in edges:
            elevation_v = nodes[v][2]

            delta_elevation = elevation_v - elevation_u
            gpe_joules = total_mass*g*delta_elevation
            gpe_wh = gpe_joules / 3600

            reduced_energy = energy - gpe_wh

            reweighted_graph[u].append((v,dist,energy,reduced_energy))
    
    return reweighted_graph

if __name__ == '__main__':
    graph_nodes = {
        # id: (x, y, elevation)
        0: (0, 0, 0),
        1: (1, 0, 10),   # 10 m higher
        2: (2, 0, 10),   # same elevation as node 1
        3: (3, 0, 0)     # 10 m lower
    }

    graph_adj = {
        0: [(1, 100, 40)],    # uphill
        1: [(2, 100, 20)],    # flat
        2: [(3, 100, -10)],   # downhill
        3: []
    }

    result = reweight(
        graph_nodes,
        graph_adj,
        total_mass=1000
    )

    for u, edges in result.items():
        for edge in edges:
            print(u, "->", edge)