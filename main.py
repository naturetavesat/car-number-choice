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


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(value, min_value, max_value):
    return max(min_value, min(value, max_value))


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


def reset_game():
    car = Car(random.randint(10, 30))
    stages = make_stages()
    passed = [False] * len(stages)
    ramp = Ramp(random.randint(30, 100))
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


def draw_road(screen):
    horizon_y = HEIGHT * 0.18
    road_top_half = 60
    road_bottom_half = WIDTH * 0.42

    road_points = [
        (WIDTH // 2 - road_top_half, horizon_y),
        (WIDTH // 2 + road_top_half, horizon_y),
        (WIDTH // 2 + road_bottom_half, HEIGHT),
        (WIDTH // 2 - road_bottom_half, HEIGHT),
    ]
    pygame.draw.polygon(screen, (40, 40, 45), road_points)
    pygame.draw.polygon(screen, (90, 90, 100), road_points, 2)

    for i in range(1, 8):
        t = i / 8
        y = lerp(horizon_y, HEIGHT, t)
        half_w = lerp(road_top_half, road_bottom_half, t)
        pygame.draw.line(screen, (160, 160, 170), (WIDTH // 2, y), (WIDTH // 2, y + 18), 2)
        pygame.draw.line(screen, (90, 90, 100), (WIDTH // 2 - half_w, y), (WIDTH // 2 - half_w, y + 10), 2)
        pygame.draw.line(screen, (90, 90, 100), (WIDTH // 2 + half_w, y), (WIDTH // 2 + half_w, y + 10), 2)

    for i in range(1, 6):
        t = i / 6
        y = lerp(horizon_y, HEIGHT, t)
        half_w = lerp(road_top_half, road_bottom_half, t)
        pygame.draw.line(screen, (220, 220, 220), (WIDTH // 2 - half_w, y), (WIDTH // 2 + half_w, y), 1)


def draw_gate_panel(screen, x_center, y, width, height, color, text, font):
    rect = pygame.Rect(x_center - width // 2, y - height // 2, width, height)
    pygame.draw.rect(screen, color, rect, border_radius=8)
    pygame.draw.rect(screen, (235, 235, 235), rect, 2, border_radius=8)
    label = font.render(text, True, (255, 255, 255))
    screen.blit(label, label.get_rect(center=rect.center))


def draw_stage_gate(screen, pair, y, font):
    if not (0 <= y <= HEIGHT):
        return

    horizon_y = HEIGHT * 0.18
    depth = clamp((y - horizon_y) / (HEIGHT - horizon_y), 0.0, 1.0)
    width = int(lerp(70, 210, depth))
    height = int(lerp(18, 52, depth))

    for lane, gate in enumerate(pair):
        lane_offset = -0.35 if lane == 0 else 0.35
        x_center = WIDTH // 2 + int(lane_offset * width * 1.5)
        color = (60, 160, 60) if gate.op in "+x" else (180, 60, 60)
        draw_gate_panel(screen, x_center, y, width, height, color, gate.label(), font)


def draw_ramp(screen, ramp, y, font):
    if not (0 <= y <= HEIGHT):
        return

    horizon_y = HEIGHT * 0.18
    depth = clamp((y - horizon_y) / (HEIGHT - horizon_y), 0.0, 1.0)
    width = int(lerp(70, 220, depth))
    height = int(lerp(18, 52, depth))
    x_center = WIDTH // 2

    pygame.draw.rect(screen, (230, 200, 40), (x_center - width, y - height // 2, width * 2, height), border_radius=8)
    pygame.draw.rect(screen, (40, 40, 40), (x_center - width, y - height // 2, width * 2, height), 2, border_radius=8)
    text = font.render(f"Need {ramp.required}", True, (0, 0, 0))
    screen.blit(text, text.get_rect(center=(x_center, y)))


def draw_car(screen, x_center, y_center, car_img=None):
    if car_img is not None:
        screen.blit(car_img, (x_center - car_img.get_width() // 2, y_center - car_img.get_height() // 2))
        return

    body = pygame.Rect(x_center - 34, y_center - 26, 68, 52)
    shadow = pygame.Rect(x_center - 42, y_center + 26, 84, 10)
    pygame.draw.ellipse(screen, (25, 25, 25), shadow)
    pygame.draw.rect(screen, (60, 120, 220), body, border_radius=12)
    pygame.draw.rect(screen, (100, 180, 255), (body.x + 12, body.y + 10, 44, 18), border_radius=6)
    pygame.draw.rect(screen, (255, 225, 70), (body.x + 14, body.y + 34, 40, 8), border_radius=4)
    pygame.draw.circle(screen, (35, 35, 35), (body.x + 14, body.y + 50), 6)
    pygame.draw.circle(screen, (35, 35, 35), (body.x + body.width - 14, body.y + 50), 6)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Car Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 40)
    big_font = pygame.font.SysFont(None, 72)
    title_font = pygame.font.SysFont(None, 72)

    car_img = None
    try:
        car_img = pygame.image.load("Pic/car1.png").convert_alpha()
        car_img = pygame.transform.scale(car_img, (108, 165))
    except Exception:
        car_img = None

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

                    for i, pair in enumerate(stages):
                        if not passed[i] and distance >= (i + 1) * STAGE_GAP:
                            car.pass_gate(pair[car.lane])
                            passed[i] = True

                    if distance >= ramp_world_y:
                        result = "WIN" if ramp.can_pass(car.speed) else "LOSE"

            if current_state == "game":
                screen.fill((12, 12, 18))
                draw_road(screen)

                for i, pair in enumerate(stages):
                    y = CAR_Y - ((i + 1) * STAGE_GAP - distance)
                    draw_stage_gate(screen, pair, y, font)

                ramp_y = CAR_Y - (ramp_world_y - distance)
                draw_ramp(screen, ramp, ramp_y, font)

                car_center_x = WIDTH // 2 + (car.lane - 0.5) * 110
                car_center_y = HEIGHT * 0.82
                draw_car(screen, car_center_x, car_center_y, car_img)

                speed_text = font.render(f"Speed: {car.speed}", True, (255, 255, 255))
                screen.blit(speed_text, (10, 10))

                if result:
                    msg = big_font.render(f"YOU {result}", True, (255, 255, 255))
                    screen.blit(msg, msg.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
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
