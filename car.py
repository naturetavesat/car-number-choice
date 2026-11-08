class Car:
    """The player's car. Speed works as health points."""

    def __init__(self, speed):
        self.speed = speed
        self.lane = 0  # 0 = left (gate A), 1 = right (gate B)
        self.lane_position = float(self.lane)

    def move_to_lane(self, lane):
        self.lane = lane

    def update(self, delta_seconds):
        lane_change_speed = 2.5
        distance = lane_change_speed * delta_seconds
        if self.lane_position < self.lane:
            self.lane_position = min(self.lane_position + distance, self.lane)
        elif self.lane_position > self.lane:
            self.lane_position = max(self.lane_position - distance, self.lane)

    def pass_gate(self, gate):
        self.speed = gate.apply(self.speed)
