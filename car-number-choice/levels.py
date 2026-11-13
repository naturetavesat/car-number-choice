from dataclasses import dataclass

from gate import Gate


@dataclass(frozen=True)
class LevelConfig:
    name: str
    description: str
    stage_count: int
    min_gates: int
    max_gates: int
    allowed_operations: tuple[str, ...]
    starting_speed: tuple[int, int]
    include_traps: bool
    target_percentile: float
    fixed_stages: tuple[tuple[Gate, ...], ...] = ()


LEVELS = (
    LevelConfig(
        "Tutorial",
        "Learn the controls with simple gates.",
        3, 2, 2, ("+", "-"), (20, 20), False, 0.45,
        ((Gate("+", 10), Gate("-", 5)),
         (Gate("+", 15), Gate("-", 8)),
         (Gate("+", 20), Gate("-", 10))),
    ),
    LevelConfig(
        "Easy",
        "Short route with addition, subtraction, and division.",
        5, 2, 2, ("+", "-", "/"), (15, 25), False, 0.40,
    ),
    LevelConfig(
        "Normal",
        "A longer route with occasional third lanes.",
        7, 2, 3, ("+", "-", "x", "/"), (12, 28), True, 0.40,
    ),
    LevelConfig(
        "Hard",
        "More stages and dangerous multiplier routes.",
        10, 2, 3, ("+", "-", "x", "/"), (10, 25), True, 0.35,
    ),
    LevelConfig(
        "Expert",
        "The full challenge: long, unpredictable, and unforgiving.",
        13, 3, 3, ("+", "-", "x", "/"), (10, 22), True, 0.30,
    ),
)
