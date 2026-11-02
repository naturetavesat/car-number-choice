import random
import pygame

from car import Car
from gate import Gate
from ramp import Ramp

WIDTH, HEIGHT = 480, 720
LANE_X = [120, 360]          # left lane = A, right lane = B
CAR_Y = 600
STAGE_GAP = 300
SCROLL_SPEED = 4


def random_gate():
    op = random.choice(["+", "-", "x", "/"])
    if op == "+":
        value = random.randint(5, 30)
    elif op == "-":
        value = random.randint(5, 20)
    else:
        value = random.randint(2, 3)
    return Gate(op, value)


def make_stages():
    count = random.randint(5, 10)
    return [[random_gate(), random_gate()] for _ in range(count)]


def highest_possible_gate_result(stages):
    """Return the maximum possible speed value any gate could produce for this run."""
    max_start_speed = 30
    return max(gate.apply(max_start_speed) for pair in stages for gate in pair)


def reset_game():
    car = Car(random.randint(10, 30))
    stages = make_stages()
    passed = [False] * len(stages)
    highest_result = highest_possible_gate_result(stages)
    ramp = Ramp(random.randint(0, max(0, highest_result - 1)))
    ramp_world_y = (len(stages) + 1) * STAGE_GAP
    distance = 0
    result = None
    return car, stages, passed, ramp, ramp_world_y, distance, result


def draw_menu(screen, title_font, font, start_btn, exit_btn):
    screen.fill((20, 20, 30))

    title = title_font.render("The Car Game", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 3)))

    pygame.draw.rect(screen, (60, 170, 90), start_btn)
    pygame.draw.rect(screen, (180, 70, 70), exit_btn)

    start_text = font.render("Start", True, (255, 255, 255))
    screen.blit(start_text, start_text.get_rect(center=start_btn.center))

    exit_text = font.render("Exit", True, (255, 255, 255))
    screen.blit(exit_text, exit_text.get_rect(center=exit_btn.center))


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Car Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 40)
    big_font = pygame.font.SysFont(None, 72)
    title_font = pygame.font.SysFont(None, 72)

    start_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 20, 240, 60)
    exit_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 70, 240, 60)
    continue_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 60, 240, 60)

    current_state = "menu"
    car, stages, passed, ramp, ramp_world_y, distance, result = reset_game()

    running = True
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    return

                if current_state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if start_btn.collidepoint(event.pos):
                            current_state = "game"
                            car, stages, passed, ramp, ramp_world_y, distance, result = reset_game()
                        elif exit_btn.collidepoint(event.pos):
                            running = False
                            return
                    continue

                if (
                    result is not None
                    and event.type == pygame.MOUSEBUTTONDOWN
                    and continue_btn.collidepoint(event.pos)
                ):
                    current_state = "menu"
                    continue

                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_a, pygame.K_LEFT):
                        car.move_to_lane(0)
                    if event.key in (pygame.K_d, pygame.K_RIGHT):
                        car.move_to_lane(1)
                if event.type == pygame.MOUSEMOTION:
                    car.move_to_lane(0 if event.pos[0] < WIDTH // 2 else 1)

            if current_state == "game":
                if result is None:
                    distance += SCROLL_SPEED

                    # Gate check: when a stage reaches the car, apply the gate in its lane
                    for i, pair in enumerate(stages):
                        if not passed[i] and distance >= (i + 1) * STAGE_GAP:
                            car.pass_gate(pair[car.lane])
                            passed[i] = True

                    # Ramp check at the end
                    if distance >= ramp_world_y:
                        result = "WIN" if ramp.can_pass(car.speed) else "LOSE"

            # ---- Drawing ----
            if current_state == "game":
                screen.fill((60, 60, 60))
                pygame.draw.line(screen, (200, 200, 200), (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 3)

                for i, pair in enumerate(stages):
                    y = CAR_Y - ((i + 1) * STAGE_GAP - distance)
                    if 0 <= y <= HEIGHT:
                        for lane in range(2):
                            rect = pygame.Rect(LANE_X[lane] - 90, y - 25, 180, 50)
                            color = (60, 160, 60) if pair[lane].op in "+x" else (180, 60, 60)
                            pygame.draw.rect(screen, color, rect)
                            text = font.render(pair[lane].label(), True, (255, 255, 255))
                            screen.blit(text, text.get_rect(center=rect.center))

                ramp_y = CAR_Y - (ramp_world_y - distance)
                if 0 <= ramp_y <= HEIGHT:
                    pygame.draw.rect(screen, (230, 200, 40), (0, ramp_y - 30, WIDTH, 60))
                    text = font.render(f"Need {ramp.required}", True, (0, 0, 0))
                    screen.blit(text, text.get_rect(center=(WIDTH // 2, ramp_y)))

                pygame.draw.rect(screen, (60, 120, 220), (LANE_X[car.lane] - 25, CAR_Y - 40, 50, 80))
                speed_text = font.render(f"Speed: {car.speed}", True, (255, 255, 255))
                screen.blit(speed_text, (10, 10))

                if result:
                    msg = big_font.render(f"YOU {result}", True, (255, 255, 255))
                    screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
                    pygame.draw.rect(screen, (60, 170, 90), continue_btn)
                    continue_text = font.render("Continue", True, (255, 255, 255))
                    screen.blit(continue_text, continue_text.get_rect(center=continue_btn.center))
            else:
                draw_menu(screen, title_font, font, start_btn, exit_btn)

            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
