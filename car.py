class Car:
    """The player's car. Speed works as health points."""

    def __init__(self, speed):
        self.speed = speed
        self.lane = 0  # 0 = left (gate A), 1 = right (gate B)

    def move_to_lane(self, lane):
        self.lane = lane

    def pass_gate(self, gate):
        self.speed = gate.apply(self.speed)
