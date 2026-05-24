class Connection:
    def __init__(self, from_: str, to: str, max_link_capacity: int = 1):
        self.from_ = from_
        self.to = to
        self.max_link_capacity = max_link_capacity
