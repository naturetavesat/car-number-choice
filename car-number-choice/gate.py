class Gate:
    """A gate changes the car's speed using an operator and a value."""

    def __init__(self, op, value):
        self.op = op          # one of: "+", "-", "x", "/"
        self.value = value

    def apply(self, speed):
        if self.op == "+":
            result = speed + self.value
        elif self.op == "-":
            result = speed - self.value
        elif self.op == "x":
            result = speed * self.value
        else:  # "/" rounds down
            result = speed // self.value
        return max(0, result)

    def label(self):
        return f"{self.op}{self.value}"
