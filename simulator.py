from scheduler import Scheduler
from drone import Drone

class Simulator:
    def __init__(self, graph, path: list):
        self.graph = graph
        self.scheduler = Scheduler(graph)
        if len(path) == 1:
            self.drones = [Drone(i, path[0]) for i in range(graph.nb_drones)] # give all drones the same path for now, we can later assign different paths to different drones if needed
        else:
            self.drones = [Drone(i, path[i % len(path)]) for i in range(graph.nb_drones)]

    def run(self) -> list:
        turn = 0
        turns = [{f"D{d.id}": d.path[d.index] for d in self.drones}] # initial state of the drones

        while not all(d.finished for d in self.drones):
            turn += 1
            moves = self.scheduler.decide_moves(self.drones)

            if all(d.finished for d in self.drones):
                break
            print("\nTurn", turn, " ".join(f"D{d_id}-{to}" for d_id, to in moves))

            # turns.append({f"D{d.id}": d.path[d.index] for d in self.drones})

            turns.append({f"D{d.id}": f"{d.path[d.index]}-{d.path[d.index + 1]}" if d.hold else d.path[d.index] for d in self.drones})
        
        return turns
    


# D1-start-waypoint1
# D1-waypoint1
# D1-goal D2-start-waypoint1
# D2-waypoint1
# D2-goal