from pathfinding import bfs_pathfinding

class Scheduler:
    def __init__(self, graph):
        self.graph = graph
        self.zone_usage = {name: self.graph.nb_drones if zone.kind == "start_hub" else 0 for name, zone in self.graph.zones.items()}


    def can_move(self, frm, to) -> bool:
        zone_to = self.graph.get_zone(to)
        if self.zone_usage.get(to, 0) >= int(zone_to.max_drones):
            return False
        
        for con in self.graph.connections:
            if {con.from_, con.to} == {frm, to}:
                link = tuple(sorted((frm, to)))
                if self.link_usage.get(link, 0) >= int(con.max_link_capacity):
                    return False
        return True


    def decide_moves(self, drones) -> list:
        moves = []
        self.link_usage = {}

        for d in drones:
            path, index = d.path, d.index

            # print(self.moves_count(d.path))
            
            if index == len(path) - 1:
                d.finished = True
                continue

            frm = path[index]
            to = path[index + 1]


            if d.hold:
                d.index += 1
                moves.append((d.id, to))
                d.hold = False
                continue


            if self.can_move(frm, to):
                self.zone_usage[frm] = self.zone_usage.get(frm, 0) - 1
                self.zone_usage[to] = self.zone_usage.get(to, 0) + 1

                link = tuple(sorted((frm, to)))
                self.link_usage[link] = self.link_usage.get(link, 0) + 1

                if self.graph.get_zone(to).movement_cost() == 2 and not d.hold:
                    moves.append((d.id, f"{frm}-{to}"))
                    d.hold = True
                    continue

                moves.append((d.id, to))
                d.index += 1
            # else:
            #     # THe drone will either wait or change its path entirely to a new one
            #     current_path = self.moves_count(path[index:])

            #     new_paths = bfs_pathfinding(self.graph, frm, path[index + 1])
            #     margin = 2
            #     if new_paths and self.moves_count(new_paths[0]) <= current_path + margin:
            #         new_path = new_paths[0]
            #         to = new_path[1]  # the next zone to move to on the new path
            #         if self.can_move(frm, to):
            #             d.path = path[:index] + new_path # we change path only if movement is possible

            #             self.zone_usage[frm] = self.zone_usage.get(frm, 0) - 1
            #             self.zone_usage[to] = self.zone_usage.get(to, 0) + 1
                        
            #             link = tuple(sorted((frm, to)))
            #             self.link_usage[link] = self.link_usage.get(link, 0) + 1

            #             if self.graph.get_zone(to).movement_cost() == 2 and not d.hold:
            #                 moves.append((d.id, f"{frm}-{to}"))
            #                 d.hold = True
            #                 continue

            #             moves.append((d.id, to))
            #             d.index += 1

                
        return moves
    
    def moves_count(self, path: list[str]):
        return sum (2 if self.graph.get_zone(x).zone == "restricted" else 1 for x in path)
    


