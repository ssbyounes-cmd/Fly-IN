from map_parser import Parser
from zone import Zone
from connection import Connection
from graph import Graph
from simulator import Simulator
from visualizer import Visualizer
from scheduler import Scheduler
import pathfinding 
import sys


try:
    if len(sys.argv) != 2:
        raise ValueError("Usage: python flyin.py <map_file>")
    data = Parser.parsing_all(sys.argv[1])
    print(data)
    graph = Graph(data["nb_drones"], {zone["name"]: Zone(**zone) for zone in data["zones"]}, [Connection(**conn) for conn in data["connections"]])
    path = pathfinding.bfs_pathfinding(graph, graph.start)
    if not path:
        raise ValueError("No path found from start to end.")
except Exception as e:
    print(e)
    sys.exit(1)


scheduler = Scheduler(graph)

def filter_paths(scheduler, path):

    margin = 2
    shortest = scheduler.moves_count(path[0])
    return list(filter(lambda x: scheduler.moves_count(x) < shortest + margin, path))


path = filter_paths(scheduler, path)

    



print("\nSHortest path from start to end:")
print(path)


print()
simulator = Simulator(graph, path)
turns = simulator.run()


# print(turns)

visualizer = Visualizer(graph, turns)