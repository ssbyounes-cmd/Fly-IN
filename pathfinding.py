from zone import Zone
from graph import Graph


def bfs_pathfinding(graph, start_zone, ignore_zone=None) -> list[list[str]] | None:
    queue = [(start_zone, [start_zone], 0)]
    result = []

    while queue:
        zone, zone_list, res = queue.pop(0)
        if zone == graph.end:
            result.append(zone_list)
            if len(result) == 3:
                return result

        # if the zone we're in is restricted. append it and turn down the unrestricted effect by reducing res
        if res > 0:
            queue.append((zone, zone_list, 0))
            res -= 1
            continue

        # getting neighbors
        neighbors = graph.get_neighbors(zone)
    
        # We make sure to iterate first through the priority zones neighbors if there are any
        neighbors = sorted(neighbors, key=lambda n: 0 if graph.get_zone(n).zone == "priority" else 1)

        for neighbor in neighbors:
            if neighbor == ignore_zone:
                continue
            if neighbor in zone_list: # this avoids going back but allows sharing paths
                continue
            elif graph.get_zone(neighbor).zone == "priority":
                queue.append((neighbor, zone_list + [neighbor], 0))
            elif graph.get_zone(neighbor).zone == "blocked":
                continue
            elif graph.get_zone(neighbor).zone == "restricted":
                queue.append((neighbor, zone_list + [neighbor], 1))
            else:
                queue.append((neighbor, zone_list + [neighbor], 0))

    if result:
        return result
    return None


# Last resort::
# SO this is the final approach,, Calculating up to 3 ways that are close in count_moves range from bfs_pathfinding
# NOte that when distributing all 3 paths (if all found) to drones,, drones need to be sorted distinctively
