class Car:
    """The player's car. Speed works as health points."""

    def __init__(self, speed):
        self.speed = speed
        self.lane = 0  # 0 = left, 1 = middle/right, 2 = right
        self.lane_position = float(self.lane)
        self.lane_count = 3

    def move_to_lane(self, lane, lane_count=3):
        if lane_count != self.lane_count:
            self.set_lane_count(lane_count)
        self.lane = max(0, min(lane, lane_count - 1))

    def set_lane_count(self, lane_count):
        if lane_count < 1:
            raise ValueError("lane_count must be positive")

        current_center = (self.lane_position + 0.5) / self.lane_count
        target_center = (self.lane + 0.5) / self.lane_count
        self.lane_count = lane_count
        self.lane = max(
            0,
            min(round(target_center * lane_count - 0.5), lane_count - 1),
        )
        self.lane_position = current_center * lane_count - 0.5

    def update(self, delta_seconds):
        lane_change_speed = 2.5
        distance = lane_change_speed * delta_seconds
        if self.lane_position < self.lane:
            self.lane_position = min(self.lane_position + distance, self.lane)
        elif self.lane_position > self.lane:
            self.lane_position = max(self.lane_position - distance, self.lane)

    def pass_gate(self, gate):
        self.speed = gate.apply(self.speed)
