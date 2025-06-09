import pygame
import random
import asyncio
import threading
import time

from ledboard import led_loop, queue, renew_connection

SPRITE = [
    [0, 1, 0],
    [1, 1, 1],
    [0, 1, 0],
    [1, 0, 1],
]

TILE = 20
WIDTH, HEIGHT = 32, 16

#You will mainly use those configurations if you want to change anything 
ledboard_id = "" #You need to get your own LED board ID, if you dont know it, I have left two functions "Scan" and "Explore" in ledboard.py, you can use them to find your LED board ID and Write UUID as well
OBSTACLE_SPAWN_RATE = 0.5 # How often obstacles spawn
OBSTACLE_SPAWN_COOLDOWN = 10 # Cooldown for spawning obstacles
USE_LED = True # Set to True if you want to use the LED board, False for local display


def init_world():
    # Initialize the game world with empty spaces
    return [[" " for _ in range(WIDTH)] for _ in range(HEIGHT)]


def show_start_screen(screen):
    # Display the start screen with instructions
    font = pygame.font.SysFont("Arial", 48)
    text = font.render("START", True, (255, 255, 255))
    text_rect = text.get_rect(center=(WIDTH * TILE // 2, HEIGHT * TILE // 2))

    waiting = True

    while waiting:
        screen.fill((0, 0, 0))
        screen.blit(text, text_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    waiting = False


def show_game_over_screen(screen):
    # Display the game over screen
    font = pygame.font.SysFont("Arial", 48)
    small_font = pygame.font.SysFont("Arial", 28)
    text = font.render("GAME OVER", True, (255, 0, 0))
    restart_text = small_font.render("Restart? Press Enter", True, (255, 255, 255))

    text_rect = text.get_rect(center=(WIDTH * TILE // 2, HEIGHT * TILE // 2 - 30))
    restart_rect = restart_text.get_rect(center=(WIDTH * TILE // 2, HEIGHT * TILE // 2 + 30))

    # I explained how to do those drawings in my twitter post, if you are actually reading this, and you actually want to reproduce it and are not being able to, send me a message, I will love to help :)
    if USE_LED:
        while not queue.empty():
            queue.get_nowait()
        matrix = [
            [(255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255),
             (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255),
             (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255),
             (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255),
             (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), ],
            [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), ],
            [(255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0),
             (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0),
             (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0),
             (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), ],
            [(255, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0),
             (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0),
             (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0),
             (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), ],
            [(255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0),
             (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0),
             (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0),
             (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), ],
            [(255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0),
             (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0),
             (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), ],
            [(255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0),
             (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0),
             (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0),
             (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), ],
            [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), ],
            [(255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0),
             (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0),
             (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0),
             (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), ],
            [(255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
             (255, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0),
             (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), ],
            [(255, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0),
             (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0),
             (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0),
             (255, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), ],
            [(255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0),
             (255, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0),
             (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), ],
            [(255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (255, 0, 0), (255, 0, 0), (0, 0, 0),
             (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0),
             (255, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (0, 0, 0),
             (255, 0, 0), (0, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), (255, 0, 0), (0, 0, 0), ],
            [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), ],
            [(0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0),
             (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), ],
            [(255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255),
             (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255),
             (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255),
             (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255),
             (255, 0, 255), (255, 0, 255), (255, 0, 255), (255, 0, 255), ],
        ]

        queue.put_nowait(matrix)

    waiting = True
    while waiting:
        screen.fill((0, 0, 0))
        screen.blit(text, text_rect)
        screen.blit(restart_text, restart_rect)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    screen = pygame.display.set_mode((WIDTH * TILE, HEIGHT * TILE))
                    if USE_LED:
                        threading.Thread(target=lambda: asyncio.run(renew_connection(ledboard_id)), daemon=True).start()
                    main(screen)


def draw_all(screen, world, x, y):
    # Draws the world and the player
    screen.fill((0, 0, 0))
    for ry, row in enumerate(world):
        for rx, cell in enumerate(row):
            if cell == "O":
                pygame.draw.rect(screen, (255, 165, 0), (rx * TILE, ry * TILE, TILE, TILE))
            elif cell == "G":
                pygame.draw.rect(screen, (0, 255, 0), (rx * TILE, ry * TILE, TILE, TILE))
            elif cell == "B":
                pygame.draw.rect(screen, (0, 100, 255), (rx * TILE, ry * TILE, TILE, TILE))
            elif cell == "P":
                pygame.draw.rect(screen, (255, 105, 180), (rx * TILE, ry * TILE, TILE, TILE))
            elif cell == "W":
                pygame.draw.rect(screen, (255, 255, 255), (rx * TILE, ry * TILE, TILE, TILE))
    for ry, row in enumerate(SPRITE):
        for rx, px in enumerate(row):
            if px:
                pygame.draw.rect(screen, (128, 0, 128),
                                 ((x + rx) * TILE, (y + ry) * TILE, TILE, TILE))
    pygame.display.flip()


def spawn_orange_obstacle(world):
    # Spawn obstacles to jump
    height = 2

    if random.random() < 0.4:
        max_top = max(0, HEIGHT - height - len(SPRITE) - 1)
        top_y = random.randint(0, max_top)
    else:
        base_y = HEIGHT - height - 1
        offset = random.choice([-1, 0, 1])
        top_y = max(0, min(HEIGHT - height, base_y + offset))

    for y in range(top_y, top_y + height):
        for x in range(WIDTH - 3, WIDTH):
            world[y][x] = "O"


def is_on_ground(world, player_y, sprite_h):
    # Check if the player is on the ground
    sprite_bottom_y = player_y + sprite_h - 1
    if player_y == 14:
        return True
    for rx in range(len(SPRITE[0])):
        wx = 4 + rx
        wy = sprite_bottom_y + 1
        if wy < HEIGHT and 0 <= wx < WIDTH and world[wy][wx] == "O":
            return True
    return False


def check_collision_below(world, player_y, sprite_height):
    # Check if the player collides with obstacles below, in order to climb up on them
    sprite_bottom_y = player_y + sprite_height - 1
    check_y = sprite_bottom_y + 1

    col_index = 0
    for offset in (-1, 0, 1, 2):
        world_x = 4 + col_index + offset
        if 0 <= check_y < HEIGHT and 0 <= world_x < WIDTH:
            if world[check_y][world_x] == "O":
                return check_y
    return None


def move_world_left(world):
    # Move the world to the left, shifting all obstacles
    for row in world:
        for x in range(WIDTH - 1):
            row[x] = row[x + 1]
        row[-1] = " "


def maybe_spawn_obstacle(world, spawn_cooldown):
    # Handle obstacle spawning
    if spawn_cooldown > 0:
        return spawn_cooldown - 1

    if random.random() < OBSTACLE_SPAWN_RATE:
        spawn_orange_obstacle(world)
        return OBSTACLE_SPAWN_COOLDOWN

    return 0


def detect_side_collision(world, draw_y, sprite_h):
    # Detect if the player collides with obstacles on the sides
    for ry, row in enumerate(SPRITE):
        for rx, px in enumerate(row):
            if not px:
                continue

            wx = 4 + rx
            wy = draw_y + ry
            # só dentro dos limites
            if 0 <= wy < HEIGHT and 0 <= wx < WIDTH:
                if world[wy][wx] == "O" and ry < sprite_h - 1:
                    return True
    return False


def detect_quit():
    # Detect if the user wants to quit the game
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()


def resolve_vertical_collisions(player_y, vel_y, sprite_h, wy):
    # Resolve vertical collisions with the ground
    if wy is not None and vel_y > 0:
        vel_y = 0
        player_y = wy - sprite_h + 1
    player_y = min(14, max(0, player_y))
    return player_y, vel_y


def fire_laser(keys, draw_y, lasers, cooldown, laser_sound):
    # Handle laser firing
    if keys[pygame.K_d] and cooldown == 0:
        laser_sound.play()
        lasers.append([4 + 2, draw_y + 1])
        return 5
    return cooldown


def update_lasers(lasers, world, point_box_sound):
    # Handle laser movement and collisions
    new_lasers = []
    for x, y in lasers:
        hit = False
        for step in (1, 2):
            check_x = x + step
            if check_x >= WIDTH:
                break

            if world[y][check_x] in ("G", "B"):
                point_box_sound.play()
                for dy in range(-1, 3):
                    for dx in range(-1, 3):
                        wx = check_x + dx
                        wy = y + dy
                        if 0 <= wx < WIDTH and 0 <= wy < HEIGHT:
                            if world[wy][wx] in ("G", "B"):
                                world[wy][wx] = " "
                hit = True
                break

        if not hit:
            new_lasers.append((x + 2, y))
    return new_lasers


def draw_lasers(screen, lasers):
    # Draw lasers on the screen
    for lx, ly in lasers:
        pygame.draw.rect(screen, (255, 255, 255), (lx * TILE, ly * TILE, TILE, TILE))


def spawn_color_box(world):
    # Spawn point objects to be shoot with laser
    top_y = random.randint(HEIGHT - 6, HEIGHT - 3)
    left_x = WIDTH - 4

    for dy in range(2):
        for dx in range(2):
            wy = top_y + dy
            wx = left_x + dx
            if world[wy][wx] != " ":
                return

    color = random.choice(("G", "B"))
    for dy in range(2):
        for dx in range(2):
            world[top_y + dy][left_x + dx] = color


def spawn_cup(world):
    # Spawn the cups at the right side of the screen
    x = WIDTH - 1
    y = random.randint(1, HEIGHT - 3)

    world[y][x] = "P"
    world[y + 1][x] = "W"


def check_cup_collision(player_x, player_y, world, cup_sound):
    # Check if the player collides with the cup to get a point
    for sprite_row, row in enumerate(SPRITE):
        for sprite_col, cell in enumerate(row):
            if not cell:
                continue
            wx = player_x + sprite_col
            wy = player_y + sprite_row
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx = wx + dx
                    ny = wy + dy
                    if 0 <= nx < WIDTH and 0 <= ny < HEIGHT:
                        if world[ny][nx] in ("P", "W"):
                            cup_sound.play()
                            world[ny][nx] = " "
                            for adj_dy in (-1, 1):
                                adj_ny = ny + adj_dy
                                if 0 <= adj_ny < HEIGHT and world[adj_ny][nx] in ("P", "W"):
                                    world[adj_ny][nx] = " "


def maybe_spawn_cup(world, cup_spawn_cooldown):
    # Handle cup spawning
    if cup_spawn_cooldown > 0:
        return cup_spawn_cooldown - 1

    if random.random() < 0.15:
        x = WIDTH - 2
        y = random.randint(6, HEIGHT - 3)

        if world[y][x] == " " and world[y - 1][x] == " ":
            world[y - 1][x] = "P"
            world[y
            ][x] = "W"
            return 5
    return 0


def generate_matrix_from_world(world, player_x, player_y, lasers):
    # Generate a matrix representation of the world for the LED board
    color_map = {
        "O": (255, 165, 0),
        "G": (0, 255, 0),
        "B": (0, 100, 255),
        "P": (255, 105, 180),
        "W": (255, 255, 255),
        " ": (0, 0, 0),
    }

    matrix = [[color_map.get(cell, (0, 0, 0)) for cell in row] for row in world]

    for ry, row in enumerate(SPRITE):
        for rx, px in enumerate(row):
            if px:
                x = player_x + rx
                y = player_y + ry
                if 0 <= x < WIDTH and 0 <= y < HEIGHT:
                    matrix[y][x] = (128, 0, 128)

    for lx, ly in lasers:
        if 0 <= lx < WIDTH and 0 <= ly < HEIGHT:
            matrix[ly][lx] = (255, 255, 255)
    return matrix


def main(screen):
    clock = pygame.time.Clock()
    sprite_h = len(SPRITE)
    player_y, vel_y = 14, 0
    gravity, jump_strength = 1, -3
    spawn_cooldown = 0
    world = init_world()
    lasers = []
    laser_cd = 0
    running = True
    cup_spawn_cooldown = 0

    # I downloaded those sound efects in myinstants, you cant get any sound effect you want there, I am not uploading them in github sorry
    cup_sound = pygame.mixer.Sound("coin_sound_effect.mp3")
    laser_sound = pygame.mixer.Sound("laser_sound.mp3")
    point_box_sound = pygame.mixer.Sound("point_box_sound.mp3")
    game_over_sound = pygame.mixer.Sound("game_over_sound.mp3")

    time.sleep(1)

    pygame.mixer.init()
    pygame.mixer.music.load("2CupsStuffed.mp3")
    pygame.mixer.music.play(-1)

    while running:
        detect_quit()

        keys = pygame.key.get_pressed()

        draw_y = round(player_y - (sprite_h - 2))
        draw_y = max(0, min(HEIGHT - sprite_h, draw_y))

        if USE_LED:
            matrix = generate_matrix_from_world(world, 4, draw_y, lasers)
            while queue.full():
                time.sleep(0.001)
            try:
                queue.put_nowait(matrix)
            except asyncio.QueueFull:
                pass

        if keys[pygame.K_SPACE] and is_on_ground(world, player_y, sprite_h):
            vel_y = jump_strength

        player_y += vel_y
        vel_y += gravity

        wy = check_collision_below(world, player_y, sprite_h)
        player_y, vel_y = resolve_vertical_collisions(player_y, vel_y, sprite_h, wy)

        move_world_left(world)
        spawn_cooldown = maybe_spawn_obstacle(world, spawn_cooldown)
        cup_spawn_cooldown = maybe_spawn_cup(world, cup_spawn_cooldown)

        if random.random() < 0.02:
            spawn_color_box(world)

        if detect_side_collision(world, draw_y, sprite_h):
            pygame.mixer.music.stop()
            game_over_sound.play()
            show_game_over_screen(screen)

        laser_cd = fire_laser(keys, draw_y, lasers, laser_cd, laser_sound)
        laser_cd = max(0, laser_cd - 1)
        lasers = update_lasers(lasers, world, point_box_sound)

        check_cup_collision(4, draw_y, world, cup_sound)

        draw_all(screen, world, 4, draw_y)
        draw_lasers(screen, lasers)
        pygame.display.flip()

        if USE_LED:
            clock.tick(30)
        else:
            clock.tick(10)


if __name__ == "__main__":
    first_run = True
    while True:
        pygame.init()
        pygame.key.set_repeat(1, 100)
        screen = pygame.display.set_mode((WIDTH * TILE, HEIGHT * TILE))
        pygame.display.set_caption("Double Cup Dash")

        if first_run:
            show_start_screen(screen)
            first_run = False

        if USE_LED:
            threading.Thread(target=lambda: asyncio.run(led_loop(ledboard_id)), daemon=True).start()

        main(screen)
