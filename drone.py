class Drone:
    def __init__(self, drone_id: int, path: list[str]):
        self.id = drone_id
        self.path = path  # the path assigned to this drone
        self.index = 0  # where the drone is on the path
        self.finished = False
        self.hold = False  # THis is used to indicate if the drone is currently holding in a restricted zone, which means it can only move every other turn
