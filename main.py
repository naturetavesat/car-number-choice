import random
import pygame

from car import Car
from gate import Gate
from ramp import Ramp

WIDTH, HEIGHT = 480, 720
CAR_Y = 600
STAGE_GAP = 300
SCROLL_SPEED = 4
HORIZON_Y = int(HEIGHT * 0.18)


def lerp(start, end, amount):
    return start + (end - start) * amount


def clamp(value, lower, upper):
    return max(lower, min(value, upper))


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
    start_ticks = pygame.time.get_ticks()
    return car, stages, passed, ramp, ramp_world_y, distance, result, start_ticks


def draw_menu(screen, title_font, font, start_btn, exit_btn):
    screen.fill((20, 20, 30))

    title = title_font.render("The Car Game", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(WIDTH // 2, HEIGHT // 3)))

    pygame.draw.rect(screen, (60, 170, 90), start_btn, border_radius=8)
    pygame.draw.rect(screen, (180, 70, 70), exit_btn, border_radius=8)

    start_text = font.render("Start", True, (255, 255, 255))
    screen.blit(start_text, start_text.get_rect(center=start_btn.center))

    exit_text = font.render("Exit", True, (255, 255, 255))
    screen.blit(exit_text, exit_text.get_rect(center=exit_btn.center))


def draw_road(screen, distance):
    """Draw a receding road with perspective lane markings and roadside stripes."""
    road_top_half = 48
    road_bottom_half = WIDTH * 0.46
    road_points = [
        (WIDTH // 2 - road_top_half, HORIZON_Y),
        (WIDTH // 2 + road_top_half, HORIZON_Y),
        (WIDTH // 2 + road_bottom_half, HEIGHT),
        (WIDTH // 2 - road_bottom_half, HEIGHT),
    ]

    screen.fill((100, 160, 95))
    pygame.draw.rect(screen, (110, 175, 105), (0, HORIZON_Y, WIDTH, HEIGHT - HORIZON_Y))
    pygame.draw.polygon(screen, (45, 46, 52), road_points)
    pygame.draw.polygon(screen, (210, 210, 210), road_points, 2)

    # Short dashed center line segments shrink toward the horizon and scroll with the road.
    stripe_cycle = 100
    scroll = (distance * 3) % stripe_cycle
    for index in range(-1, 10):
        world_y = index * stripe_cycle + scroll
        t = world_y / (HEIGHT - HORIZON_Y)
        if not 0 <= t <= 1:
            continue
        y = int(lerp(HORIZON_Y, HEIGHT, t))
        half_width = lerp(road_top_half, road_bottom_half, t)
        dash_height = max(2, int(lerp(3, 24, t)))
        dash_width = max(1, int(lerp(1, 5, t)))
        pygame.draw.rect(
            screen,
            (230, 230, 220),
            (WIDTH // 2 - dash_width // 2, y, dash_width, dash_height),
        )

        # Perspective cross-road markings add depth without adding gameplay obstacles.
        if index % 2 == 0:
            pygame.draw.line(
                screen,
                (75, 76, 82),
                (WIDTH // 2 - half_width, y + dash_height),
                (WIDTH // 2 + half_width, y + dash_height),
                max(1, int(1 + t * 2)),
            )

    # Scrolling red/white edge markers reinforce the sense of forward motion.
    for side in (-1, 1):
        for index in range(-1, 9):
            world_y = index * 90 + (distance * 3) % 90
            t = world_y / (HEIGHT - HORIZON_Y)
            if not 0 <= t <= 1:
                continue
            y = int(lerp(HORIZON_Y, HEIGHT, t))
            half_width = lerp(road_top_half, road_bottom_half, t)
            marker_width = max(2, int(lerp(2, 12, t)))
            marker_height = max(2, int(lerp(3, 30, t)))
            x = int(WIDTH // 2 + side * (half_width + marker_width))
            color = (225, 225, 220) if index % 2 else (190, 65, 55)
            pygame.draw.rect(
                screen,
                color,
                (x - marker_width // 2, y, marker_width, marker_height),
            )


def perspective_for_y(y):
    return clamp((y - HORIZON_Y) / (HEIGHT - HORIZON_Y), 0.0, 1.0)


def draw_gate(screen, gate, lane, y, font):
    if y < HORIZON_Y - 10 or y > HEIGHT + 60:
        return

    depth = perspective_for_y(y)
    width = int(lerp(28, 166, depth))
    height = int(lerp(12, 58, depth))
    lane_center = WIDTH // 2 + (-1 if lane == 0 else 1) * int(lerp(18, 98, depth))
    rect = pygame.Rect(lane_center - width // 2, int(y) - height // 2, width, height)
    color = (50, 150, 65) if gate.op in "+x" else (180, 55, 55)

    # Shadow, raised gate panel, and border give the 2D shapes a simple 3D look.
    pygame.draw.rect(screen, (24, 25, 28), rect.move(0, max(2, int(5 * depth))), border_radius=5)
    pygame.draw.rect(screen, color, rect, border_radius=5)
    pygame.draw.rect(screen, (245, 245, 235), rect, max(1, int(1 + 2 * depth)), border_radius=5)

    label_size = max(13, int(lerp(14, 34, depth)))
    label_font = pygame.font.SysFont(None, label_size)
    label = label_font.render(gate.label(), True, (255, 255, 255))
    screen.blit(label, label.get_rect(center=rect.center))


def draw_ramp(screen, ramp, y, font):
    if y < HORIZON_Y - 10 or y > HEIGHT + 60:
        return

    depth = perspective_for_y(y)
    half_width = int(lerp(35, WIDTH * 0.43, depth))
    height = int(lerp(10, 46, depth))
    points = [
        (WIDTH // 2 - half_width, y + height // 2),
        (WIDTH // 2 - half_width + int(12 * depth), y - height // 2),
        (WIDTH // 2 + half_width - int(12 * depth), y - height // 2),
        (WIDTH // 2 + half_width, y + height // 2),
    ]
    pygame.draw.polygon(screen, (45, 38, 20), [(x, yy + 5) for x, yy in points])
    pygame.draw.polygon(screen, (230, 190, 45), points)
    pygame.draw.polygon(screen, (255, 230, 110), points, max(1, int(1 + 2 * depth)))

    label = font.render(f"Need {ramp.required}", True, (25, 25, 25))
    screen.blit(label, label.get_rect(center=(WIDTH // 2, int(y))))


def draw_car(screen, car, car_img):
    lane_x = WIDTH // 2 + (-1 if car.lane == 0 else 1) * 58
    car_y = int(HEIGHT * 0.82)

    if car_img is not None:
        # Preserve the supplied sprite while scaling it to sit naturally on the road.
        image = pygame.transform.scale(car_img, (84, 128))
        screen.blit(image, image.get_rect(midbottom=(lane_x, car_y + 35)))
        return

    # Fallback car sprite if the image asset is unavailable.
    shadow = pygame.Rect(lane_x - 42, car_y + 22, 84, 13)
    body = pygame.Rect(lane_x - 31, car_y - 29, 62, 58)
    pygame.draw.ellipse(screen, (25, 25, 25), shadow)
    pygame.draw.rect(screen, (45, 120, 225), body, border_radius=12)
    pygame.draw.polygon(screen, (105, 185, 255), [
        (lane_x - 21, car_y - 7), (lane_x - 14, car_y - 23),
        (lane_x + 14, car_y - 23), (lane_x + 21, car_y - 7),
    ])
    pygame.draw.rect(screen, (230, 230, 240), (lane_x - 21, car_y + 5, 42, 12), border_radius=4)
    pygame.draw.circle(screen, (30, 30, 30), (lane_x - 23, car_y + 23), 7)
    pygame.draw.circle(screen, (30, 30, 30), (lane_x + 23, car_y + 23), 7)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("The Car Game")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 40)
    big_font = pygame.font.SysFont(None, 72)
    title_font = pygame.font.SysFont(None, 72)

    def load_image(path):
        try:
            return pygame.image.load(path).convert_alpha()
        except (pygame.error, FileNotFoundError):
            return None

    car_img = load_image("Pic/car1.png")
    red_light = load_image("Pic/RedLight.png")
    yellow_light = load_image("Pic/YellowLight.png")
    green_light = load_image("Pic/GreenLight.png")

    start_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 - 20, 240, 60)
    exit_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 70, 240, 60)
    continue_btn = pygame.Rect(WIDTH // 2 - 120, HEIGHT // 2 + 60, 240, 60)

    current_state = "menu"
    car, stages, passed, ramp, ramp_world_y, distance, result, start_ticks = reset_game()
    prepare_time = 2.0

    running = True
    try:
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue

                if current_state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if start_btn.collidepoint(event.pos):
                            current_state = "game"
                            car, stages, passed, ramp, ramp_world_y, distance, result, start_ticks = reset_game()
                        elif exit_btn.collidepoint(event.pos):
                            running = False
                    continue

                if current_state == "game":
                    if result is not None:
                        if event.type == pygame.MOUSEBUTTONDOWN and continue_btn.collidepoint(event.pos):
                            current_state = "menu"
                            continue
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                            car, stages, passed, ramp, ramp_world_y, distance, result, start_ticks = reset_game()
                            continue

                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_a, pygame.K_LEFT):
                            car.move_to_lane(0)
                        elif event.key in (pygame.K_d, pygame.K_RIGHT):
                            car.move_to_lane(1)
                    elif event.type == pygame.MOUSEMOTION:
                        car.move_to_lane(0 if event.pos[0] < WIDTH // 2 else 1)

            if current_state == "game":
                passed_sec = (pygame.time.get_ticks() - start_ticks) / 1000.0

                if result is None and passed_sec >= prepare_time:
                    distance += SCROLL_SPEED

                    for index, pair in enumerate(stages):
                        if not passed[index] and distance >= (index + 1) * STAGE_GAP:
                            car.pass_gate(pair[car.lane])
                            passed[index] = True

                    if distance >= ramp_world_y:
                        result = "WIN" if ramp.can_pass(car.speed) else "LOSE"

                draw_road(screen, distance)

                for index, pair in enumerate(stages):
                    gate_y = CAR_Y - ((index + 1) * STAGE_GAP - distance)
                    for lane, gate in enumerate(pair):
                        draw_gate(screen, gate, lane, gate_y, font)

                ramp_y = CAR_Y - (ramp_world_y - distance)
                draw_ramp(screen, ramp, ramp_y, font)
                draw_car(screen, car, car_img)

                speed_text = font.render(f"Speed: {car.speed}", True, (255, 255, 255))
                screen.blit(speed_text, (10, 10))

                if passed_sec < prepare_time:
                    light = red_light if passed_sec < 1.0 else yellow_light
                    if light is not None:
                        light = pygame.transform.smoothscale(light, (72, 110))
                        screen.blit(light, light.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
                    else:
                        color = (220, 45, 45) if passed_sec < 1.0 else (235, 190, 35)
                        pygame.draw.circle(screen, color, (WIDTH // 2, HEIGHT // 3), 24)
                elif passed_sec < prepare_time + 0.25:
                    if green_light is not None:
                        light = pygame.transform.smoothscale(green_light, (72, 110))
                        screen.blit(light, light.get_rect(center=(WIDTH // 2, HEIGHT // 3)))
                    else:
                        pygame.draw.circle(screen, (40, 210, 80), (WIDTH // 2, HEIGHT // 3), 24)

                if result:
                    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                    overlay.fill((0, 0, 0, 120))
                    screen.blit(overlay, (0, 0))
                    message = big_font.render(f"YOU {result}", True, (255, 255, 255))
                    screen.blit(message, message.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30)))
                    pygame.draw.rect(screen, (60, 170, 90), continue_btn, border_radius=8)
                    continue_text = font.render("Continue", True, (255, 255, 255))
                    screen.blit(continue_text, continue_text.get_rect(center=continue_btn.center))
                    restart_text = font.render("Or Press 'R'", True, (220, 220, 220))
                    screen.blit(restart_text, restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 150)))
            else:
                draw_menu(screen, title_font, font, start_btn, exit_btn)

            pygame.display.flip()
            clock.tick(60)
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
