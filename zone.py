class Zone:
    def __init__(self, name: str, x: int, y: int, kind: str, zone: str = "normal", color: str = "none", max_drones: int = 1):
        self.name = name
        self.x = x
        self.y = y
        self.kind = kind
        self.zone = zone
        self.color = color
        self.max_drones = max_drones

    def movement_cost(self) -> int:
        if self.zone == "restricted":
            return 2
        return 1

    def is_blocked(self) -> bool:
        return self.zone == "blocked"
