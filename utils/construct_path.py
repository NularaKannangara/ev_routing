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