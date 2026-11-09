import random
import pygame

from car import Car
from gate import Gate
from levels import LEVELS, LevelConfig
from ramp import Ramp

WIDTH, HEIGHT = 480, 720
CAR_Y = 600
STAGE_GAP = 300
SCROLL_SPEED = 4
HORIZON_Y = int(HEIGHT * 0.18)
ROAD_TOP_HALF = 48
ROAD_BOTTOM_HALF = WIDTH * 0.46


def lerp(start, end, amount):
    return start + (end - start) * amount


def clamp(value, lower, upper):
    return max(lower, min(value, upper))


def random_gate(allowed_operations):
    op = random.choice(allowed_operations)
    if op == "+":
        value = random.randint(5, 30)
    elif op == "-":
        value = random.randint(5, 20)
    else:
        value = random.randint(2, 3)
    return Gate(op, value)


def make_stages(config):
    if config.fixed_stages:
        return [list(pair) for pair in config.fixed_stages]

    count = config.stage_count
    stages = [
        [
            random_gate(config.allowed_operations)
            for _ in range(random.randint(config.min_gates, config.max_gates))
        ]
        for _ in range(count)
    ]

    # A large multiplier followed by division creates a tempting but risky route.
    if config.include_traps and count > 1 and random.random() < 0.75:
        trap_stage = random.randrange(count - 1)
        stages[trap_stage][0] = Gate("x", 3)
        stages[trap_stage + 1][0] = Gate("/", 3)
        if len(stages[trap_stage]) == 2:
            stages[trap_stage][1] = Gate("+", random.randint(8, 15))
        if len(stages[trap_stage + 1]) == 2:
            stages[trap_stage + 1][1] = Gate("+", random.randint(8, 15))
    return stages


def possible_route_results(start_speed, stages):
    """Return every final speed reachable by choosing one gate per stage."""
    possible_speeds = {start_speed}
    for pair in stages:
        possible_speeds = {
            gate.apply(speed)
            for speed in possible_speeds
            for gate in pair
        }
    return possible_speeds


def highest_possible_route_result(start_speed, stages):
    """Return the best final speed available when considering every stage."""
    return max(possible_route_results(start_speed, stages))


def reset_game(config):
    car = Car(random.randint(*config.starting_speed))
    stages = make_stages(config)
    car.set_lane_count(len(stages[0]))
    passed = [False] * len(stages)
    reachable_results = sorted(possible_route_results(car.speed, stages))
    target_index = int((len(reachable_results) - 1) * config.target_percentile)
    ramp_requirement = reachable_results[target_index]
    ramp = Ramp(ramp_requirement)
    ramp_world_y = (len(stages) + 1) * STAGE_GAP
    distance = 0
    result = None
    start_ticks = pygame.time.get_ticks()
    return car, stages, passed, ramp, ramp_world_y, distance, result, start_ticks


def active_lane_count(stages, passed):
    next_stage = next(
        (index for index, passed_stage in enumerate(passed) if not passed_stage),
        len(stages) - 1,
    )
    return len(stages[next_stage])


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


def draw_level_select(screen, title_font, font, levels, unlocked_level):
    screen.fill((20, 20, 30))
    title = title_font.render("Choose Level", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(WIDTH // 2, 70)))

    for index, config in enumerate(levels):
        y = 125 + index * 105
        unlocked = index <= unlocked_level
        button = pygame.Rect(35, y, WIDTH - 70, 82)
        color = (55, 135, 80) if unlocked else (65, 65, 75)
        pygame.draw.rect(screen, color, button, border_radius=8)
        label = f"{index + 1}. {config.name}"
        if not unlocked:
            label += "  (Locked)"
        name = font.render(label, True, (255, 255, 255))
        screen.blit(name, (button.x + 16, button.y + 10))
        description = pygame.font.SysFont(None, 22).render(
            config.description, True, (220, 220, 220)
        )
        screen.blit(description, (button.x + 16, button.y + 47))

    hint = pygame.font.SysFont(None, 24).render(
        "Click a level or press 1-5. Escape: back", True, (220, 220, 220)
    )
    screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT - 25)))


def draw_road(screen, distance):
    """Draw a receding road with perspective lane markings and roadside stripes."""
    road_points = [
        (WIDTH // 2 - ROAD_TOP_HALF, HORIZON_Y),
        (WIDTH // 2 + ROAD_TOP_HALF, HORIZON_Y),
        (WIDTH // 2 + ROAD_BOTTOM_HALF, HEIGHT),
        (WIDTH // 2 - ROAD_BOTTOM_HALF, HEIGHT),
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
        half_width = road_half_width(t)
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
            half_width = road_half_width(t)
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


def road_half_width(depth):
    return lerp(ROAD_TOP_HALF, ROAD_BOTTOM_HALF, depth)


def lane_center_x(lane_position, lane_count, depth):
    lane_width = (road_half_width(depth) * 2) / lane_count
    return int(WIDTH // 2 - road_half_width(depth) + (lane_position + 0.5) * lane_width)


def draw_gate(screen, gate, lane, lane_count, y, font):
    if y < HORIZON_Y - 10 or y > HEIGHT + 60:
        return

    depth = perspective_for_y(y)
    lane_width = (road_half_width(depth) * 2) / lane_count
    width = max(12, int(lane_width * 0.78))
    height = int(lerp(12, 58, depth))
    lane_center = lane_center_x(lane, lane_count, depth)
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


def draw_car(screen, car, car_img, lane_count):
    lane_position = min(car.lane_position, lane_count - 1)
    lane_x = lane_center_x(
        lane_position,
        lane_count,
        perspective_for_y(CAR_Y),
    )
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
    leave_level_btn = pygame.Rect(WIDTH - 105, 42, 95, 36)
    level_buttons = [
        pygame.Rect(35, 125 + index * 105, WIDTH - 70, 82)
        for index in range(len(LEVELS))
    ]

    current_state = "menu"
    selected_level = 0
    unlocked_level = 0
    config = LEVELS[selected_level]
    car, stages, passed, ramp, ramp_world_y, distance, result, start_ticks = reset_game(config)
    prepare_time = 2.0

    running = True
    try:
        while running:
            delta_seconds = clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    continue

                if current_state == "menu":
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if start_btn.collidepoint(event.pos):
                            current_state = "level_select"
                        elif exit_btn.collidepoint(event.pos):
                            running = False
                    continue

                if current_state == "level_select":
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            current_state = "menu"
                        elif pygame.K_1 <= event.key <= pygame.K_5:
                            level_index = event.key - pygame.K_1
                            if level_index <= unlocked_level:
                                selected_level = level_index
                                config = LEVELS[selected_level]
                                car, stages, passed, ramp, ramp_world_y, distance, result, start_ticks = reset_game(config)
                                current_state = "game"
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        for level_index, button in enumerate(level_buttons):
                            if button.collidepoint(event.pos) and level_index <= unlocked_level:
                                selected_level = level_index
                                config = LEVELS[selected_level]
                                car, stages, passed, ramp, ramp_world_y, distance, result, start_ticks = reset_game(config)
                                current_state = "game"
                                break
                    continue

                if current_state == "game":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        current_state = "level_select"
                        continue
                    if event.type == pygame.MOUSEBUTTONDOWN and leave_level_btn.collidepoint(event.pos):
                        current_state = "level_select"
                        continue

                    if result is not None:
                        if event.type == pygame.MOUSEBUTTONDOWN and continue_btn.collidepoint(event.pos):
                            current_state = "level_select"
                            continue
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                            car, stages, passed, ramp, ramp_world_y, distance, result, start_ticks = reset_game(config)
                            continue

                    if event.type == pygame.KEYDOWN:
                        lane_count = active_lane_count(stages, passed)
                        if event.key in (pygame.K_a, pygame.K_LEFT):
                            car.move_to_lane(0, lane_count)
                        elif event.key in (pygame.K_s, pygame.K_DOWN):
                            car.move_to_lane(1, lane_count)
                        elif event.key in (pygame.K_d, pygame.K_RIGHT):
                            car.move_to_lane(lane_count - 1, lane_count)
                    elif event.type == pygame.MOUSEMOTION:
                        lane_count = active_lane_count(stages, passed)
                        car_depth = perspective_for_y(HEIGHT * 0.82)
                        closest_lane = min(
                            range(lane_count),
                            key=lambda lane: abs(
                                event.pos[0] - lane_center_x(lane, lane_count, car_depth)
                            ),
                        )
                        car.move_to_lane(closest_lane, lane_count)

            if current_state == "game":
                car.update(delta_seconds)
                passed_sec = (pygame.time.get_ticks() - start_ticks) / 1000.0

                if result is None and passed_sec >= prepare_time:
                    if config.time_limit is not None and passed_sec >= config.time_limit:
                        result = "LOSE"
                    distance += SCROLL_SPEED * delta_seconds * 60

                    if result is None:
                        for index, pair in enumerate(stages):
                            if not passed[index] and distance >= (index + 1) * STAGE_GAP:
                                car.pass_gate(pair[min(car.lane, len(pair) - 1)])
                                passed[index] = True
                                if index + 1 < len(stages):
                                    car.set_lane_count(len(stages[index + 1]))

                    if result is None and distance >= ramp_world_y:
                        result = "WIN" if ramp.can_pass(car.speed) else "LOSE"
                        if result == "WIN" and selected_level == unlocked_level:
                            unlocked_level = min(unlocked_level + 1, len(LEVELS) - 1)

                draw_road(screen, distance)

                for index, pair in enumerate(stages):
                    gate_y = CAR_Y - ((index + 1) * STAGE_GAP - distance)
                    for lane, gate in enumerate(pair):
                        draw_gate(screen, gate, lane, len(pair), gate_y, font)

                ramp_y = CAR_Y - (ramp_world_y - distance)
                draw_ramp(screen, ramp, ramp_y, font)
                draw_car(screen, car, car_img, car.lane_count)

                speed_text = font.render(f"Speed: {car.speed}", True, (255, 255, 255))
                screen.blit(speed_text, (10, 10))
                if config.time_limit is not None and result is None:
                    timer_text = font.render(
                        f"Time: {max(0, config.time_limit - passed_sec):.1f}",
                        True,
                        (255, 235, 120),
                    )
                    screen.blit(timer_text, (10, 48))
                controls_font = pygame.font.SysFont(None, 24)
                controls_text = controls_font.render(
                    "A/Left   S/Down   D/Right", True, (225, 225, 225)
                )
                screen.blit(
                    controls_text,
                    controls_text.get_rect(midbottom=(WIDTH // 2, HEIGHT - 8)),
                )

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
                level_text = font.render(config.name, True, (255, 255, 255))
                screen.blit(level_text, level_text.get_rect(center=(WIDTH // 2, 20)))
                pygame.draw.rect(screen, (180, 70, 70), leave_level_btn, border_radius=6)
                leave_text = pygame.font.SysFont(None, 24).render("Exit", True, (255, 255, 255))
                screen.blit(leave_text, leave_text.get_rect(center=leave_level_btn.center))
            else:
                if current_state == "menu":
                    draw_menu(screen, title_font, font, start_btn, exit_btn)
                else:
                    draw_level_select(screen, title_font, font, LEVELS, unlocked_level)

            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
