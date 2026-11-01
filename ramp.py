class Ramp:
    """The final obstacle. The player loses if speed is below the requirement."""

    def __init__(self, required):
        self.required = required

    def can_pass(self, speed):
        return speed >= self.required
