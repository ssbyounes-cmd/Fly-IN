from zone import Zone
from connection import Connection


class Graph:
    def __init__(self, nb_drones: int, zones: dict[str, Zone], connections: list[Connection]):
        self.nb_drones = nb_drones
        self.zones = zones
        self.connections = connections
        
        self.adjacency: dict[str, list[str]] = {name: [] for name in zones}
        for connection in connections:
            self.adjacency[connection.from_].append(connection.to)
            self.adjacency[connection.to].append(connection.from_)

        self.start = [zone.name for zone in self.zones.values()
                      if zone.kind == "start_hub"][0]
        self.end = [zone.name for zone in self.zones.values()
                    if zone.kind == "end_hub"][0]

    def get_zone(self, name: str) -> Zone | None:
        return self.zones.get(name)

    def get_neighbors(self, name: str) -> list[str]:
        return self.adjacency[name]

    def is_start(self, name: str) -> bool:
        return self.zones[name].kind == "start_hub"

    def is_end(self, name: str) -> bool:
        return self.zones[name].kind == "end_hub"
