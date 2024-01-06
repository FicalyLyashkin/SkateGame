import random
import sys
import os
import pygame
import configparser
import threading

WIDTH = 1300
HEIGHT = WIDTH // 13 * 9
print(HEIGHT, (650 // (650 / WIDTH), 450 // (450 / HEIGHT)), WIDTH // (1300 / 300))
FPS = 35


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def load_level(filename):
    filename = "data/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    max_width = max(map(len, level_map))
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def write_statistics(filename, points):
    print(load_statistics(filename), points)
    if int(load_statistics(filename)) < points:
        config = configparser.ConfigParser()
        config.read("data/" + filename)
        config.set("Statistics", "max_count_points", str(points))
        with open("data/" + filename, 'w') as f:
            config.write(f)


def load_statistics(filename):
    config = configparser.ConfigParser()
    config.read("data/" + filename)
    past_res = config["Statistics"]["max_count_points"]
    return past_res


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


class Obstacle(pygame.sprite.Sprite):
    image = load_image("obstacle2.png")
    image = pygame.transform.scale(image, (WIDTH // 26 * 3, WIDTH // 26))

    def __init__(self, lane_y, lane_x=WIDTH):
        pygame.sprite.Sprite.__init__(self)
        self.image = Obstacle.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = lane_x
        self.rect.y = lane_y
        self.speedx = 15

    def update(self):
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.kill()


class Cone(pygame.sprite.Sprite):
    image = load_image("cone.png")
    image = pygame.transform.scale(image, (WIDTH // 26 * 2.4, WIDTH // 26 * 2.4))

    def __init__(self, lane_y, lane_x=WIDTH):
        pygame.sprite.Sprite.__init__(self)
        self.image = Cone.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = lane_x
        self.rect.y = lane_y - WIDTH // 13 // 2
        self.speedx = 15

    def update(self):
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.kill()


class Ramp(pygame.sprite.Sprite):
    image = load_image("ramp.png")
    image = pygame.transform.scale(image, (WIDTH // 26 * 3.4, WIDTH // 26 * 1.8))

    def __init__(self, lane_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = Ramp.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = WIDTH
        self.rect.y = lane_y - WIDTH // 26 * 1.8
        self.speedx = 15

    def update(self):
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, lanes_y, sheet, columns, rows, size1, size2):
        pygame.sprite.Sprite.__init__(self)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.y = lanes_y[1] - self.rect.height
        self.speedy = 0
        self.gravity = 0.5
        self.mask = pygame.mask.from_surface(self.image)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]
        if not jump:
            self.speedy += self.gravity
            self.rect.y += self.speedy
        for y in lanes_y:
            if self.rect.colliderect(pygame.Rect(0, y, WIDTH, 1)):
                self.rect.bottom = y
                self.speedy = 0
                break

        if self.rect.top <= 0:
            self.rect.top = 0
            self.speedy = 0


sprites_names = {
    'ramp': Ramp,
    'cone': Cone,
    'obstracle': Obstacle
}

tile_width = tile_height = WIDTH // 26


def generate_level(level):
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '.':
                pass
            elif level[y][x] == '*':
                lane_y = lanes_y[y]
                cone = Cone(lane_y - WIDTH // 13 // 2)
                all_sprites.add(cone)
                cones.add(cone)
            elif level[y][x] == '-':
                lane_y = lanes_y[y]
                obstacle = Obstacle(lane_y - WIDTH // 13 // 2)
                all_sprites.add(obstacle)
                obstacles.add(obstacle)
            elif level[y][x] == "+":
                lane_y = lanes_y[y]
                ramp = Ramp(lane_y)
                all_sprites.add(ramp)
                ramps.add(ramp)

    return x, y


class Start:
    def __init__(self):
        self.light = False

    def start_screen(self):
        intro_text = ["НАЗВАНИЕ ИГРЫ", "",
                      "Правила игры", "",
                      f"Рекорд: {load_statistics('statistics.txt')} очк"]

        fon = pygame.transform.scale(load_image('city.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, WIDTH // 26)
        text_coord = WIDTH // 26
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 1
            intro_rect.top = text_coord
            intro_rect.x = WIDTH // 26
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        pygame.draw.rect(screen, pygame.Color(153, 192, 212), (WIDTH // 3, HEIGHT // 6 * 4, WIDTH // 3, HEIGHT // 6), 0)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    end_scr.terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.pos[0] in range(WIDTH // 3, WIDTH // 3 * 2) and \
                        event.pos[1] in range(HEIGHT // 6 * 4, HEIGHT // 6 * 5):
                    return  # начинаем игру
                elif event.type == pygame.MOUSEMOTION:
                    if event.pos[0] in range(WIDTH // 3, WIDTH // 3 * 2) and event.pos[1] in range(HEIGHT // 6 * 4,
                                                                                                   HEIGHT // 6 * 5):
                        self.light = True
                    else:
                        self.light = False

            if self.light:
                pygame.draw.rect(screen, pygame.Color(210, 228, 236),
                                 (WIDTH // 3, HEIGHT // 6 * 4, WIDTH // 3, HEIGHT // 6), 0)
            else:
                pygame.draw.rect(screen, pygame.Color(153, 192, 212),
                                 (WIDTH // 3, HEIGHT // 6 * 4, WIDTH // 3, HEIGHT // 6), 0)
            pygame.display.flip()
            clock.tick(FPS)

    def terminate(self):
        pygame.quit()
        sys.exit()


class End:
    def __init__(self):
        self.on_btn = False

    def end_screen(self):
        intro_text = ["ВЫ ПРОИГРАЛИ", "",
                      "Счёт: {}".format(count_points // 5)]

        write_statistics("statistics.txt", count_points // 5)

        screen.fill(pygame.Color(153, 192, 212))
        font = pygame.font.Font(None, WIDTH // 13)
        text_coord = WIDTH // 20
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 1
            intro_rect.top = text_coord
            intro_rect.x = WIDTH // 3
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        btn_coords = (WIDTH // 3, HEIGHT // 6)
        pygame.draw.rect(screen, pygame.Color(153, 192, 212), (btn_coords[0], btn_coords[1] * 4, *btn_coords), 0)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    end_scr.terminate(self)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.pos[0] in range(btn_coords[0],
                                                                                    btn_coords[0] * 2) and \
                        event.pos[1] in range(btn_coords[1] * 4, btn_coords[1] * 5):
                    self.terminate()
                elif event.type == pygame.MOUSEMOTION:
                    if (event.pos[0] in range(btn_coords[0], btn_coords[0] * 2) and
                            event.pos[1] in range(btn_coords[1] * 4, btn_coords[1] * 5)):
                        self.on_btn = True
                    else:
                        self.on_btn = False

            if self.on_btn:
                pygame.draw.rect(screen, pygame.Color(50, 50, 50),
                                 (WIDTH // 3, HEIGHT // 6 * 4, WIDTH // 3, HEIGHT // 6), 0)
            else:
                pygame.draw.rect(screen, pygame.Color(0, 0, 0),
                                 (WIDTH // 3, HEIGHT // 6 * 4, WIDTH // 3, HEIGHT // 6), 0)
            pygame.display.flip()
            clock.tick(FPS)

    def terminate(self):
        pygame.quit()
        sys.exit()


all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
cones = pygame.sprite.Group()
ramps = pygame.sprite.Group()
lanes_y = [int(WIDTH // (1300 / 500)), int(WIDTH // (1300 / 700)), int(WIDTH // (1300 / 900))]
print("aaa", lanes_y)

player = Player(lanes_y,
                pygame.transform.scale(load_image("player (1).png"), (250 // (1300 / WIDTH), 95 // (900 / HEIGHT))), 5,
                2, 50, 50)
all_sprites.add(player)
if WIDTH != 1300:
    background_image = pygame.transform.scale(load_image("road.png"), (2600 // (1300 / WIDTH), 600 // (900 / HEIGHT)))
    city_image = pygame.transform.scale(load_image("city2.png"),
                                        (int(650 / (650 / WIDTH) * 2), int(450 / (450 / HEIGHT) * 2 // 6)))
    # city_image = load_image("city2.png")
    fence_image = pygame.transform.scale(load_image("fence.png"), (2600 // (1300 / WIDTH), 100 // (900 / HEIGHT)))
else:
    background_image = load_image("road.png")
    city_image = load_image("city2.png")
    fence_image = load_image("fence.png")
print(city_image.get_width(), city_image.get_height())
background_x = 0
background_speed = -15
city_x = 0
city_speed = -(WIDTH // (1300 / 9))
fence_x = 0
fence_speed = -13

font = pygame.font.Font(None, WIDTH // 26)
text_color = pygame.Color("red")
jump = False

screen = pygame.display.set_mode((WIDTH, HEIGHT))
s = Start()
Start.start_screen(s)

count_points = 0
jump = False
running = True
count = 0
count_ramp_gravity = 0
count_ramp_hits = 0

last_obstacle = 0
last_cone = 0
last_ramp = 0
last_up = 0
last_mid = 0
last_down = 0
on_obstacle = False

lanes = {lanes_y[0]: last_up, lanes_y[1]: last_mid, lanes_y[2]: last_down}

'''sprites_names = {
    0: Ramp(lane_y),
    1: Obstacle(lane_y - 50),
    2: Cone(lane_y - 50)
}'''
end_scr = End

while running:

    last_obstacle += 1
    last_cone += 1
    last_ramp += 1
    last_up += 1
    last_mid += 1
    last_down += 1

    print("lasr up", last_up)

    if random.randrange(100) < 60:
        random_obj = random.randint(0, 2)
        lane_y = random.choice(lanes_y)
        if (lane_y == lanes_y[0] and last_up > 20) or (lane_y == lanes_y[1] and last_mid > 20) or (
                lane_y == lanes_y[2] and last_down > 20):
            if random_obj == 1 and last_obstacle > 30:
                obstacle = Obstacle(lane_y - WIDTH // 26)
                all_sprites.add(obstacle)
                obstacles.add(obstacle)
                last_obstacle = 0
            elif random_obj == 2 and last_cone > 40:
                cone = Cone(lane_y - WIDTH // 13 // 2)
                all_sprites.add(cone)
                cones.add(cone)
                last_cone = 0
            elif random_obj == 0 and last_ramp > 50:
                random_obj_ramp = random.randint(0, 1)
                if random_obj_ramp == 0:
                    ramp = Ramp(lane_y)
                    all_sprites.add(ramp)
                    ramps.add(ramp)
                    cone = Cone(lane_y - WIDTH // 13 // 2, lane_x=WIDTH + WIDTH // 13 // 2 * 3)
                    all_sprites.add(cone)
                    cones.add(cone)
                    last_cone = 0
                    last_ramp = 0
                else:
                    ramp = Ramp(lane_y)
                    all_sprites.add(ramp)
                    ramps.add(ramp)
                    obstacle = Obstacle(lane_y - WIDTH // 13 // 2, lane_x=WIDTH + WIDTH // 13 // 2 * 3.6)
                    all_sprites.add(obstacle)
                    obstacles.add(obstacle)
                    last_obstacle = 0
                    last_cone = 0
            if lane_y == lanes_y[0]:
                last_up = 0
            elif lane_y == lanes_y[1]:
                last_mid = 0
            elif lane_y == lanes_y[2]:
                last_down = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w and not jump:
                if player.rect.top > lanes_y[0]:
                    player.rect.y -= lanes_y[1] - lanes_y[0]
            elif jump is False and event.key == pygame.K_s:
                if player.rect.bottom not in range(lanes_y[-2] + 1, lanes_y[-1] + 1):
                    player.rect.y += lanes_y[1] - lanes_y[0]
            elif event.key == pygame.K_c and not jump and player.rect.bottom in lanes_y:  # добавить возможность прыгать на трубе.
                jump = True

    if jump:
        if count < 1:
            player.rect.y -= WIDTH // 130 * 11 // 2
        count += 1
        if count == 10:
            jump = False
            count = 0
    count_points += 1
    all_sprites.update()

    background_x += background_speed
    city_x += city_speed
    fence_x += fence_speed
    ramp_hits = pygame.sprite.spritecollide(player, ramps, False, pygame.sprite.collide_mask)
    if ramp_hits:
        player.gravity = 0
        ramp_hits = ramp_hits[0]
        ramp_top = ramp_hits.rect.top
        player.rect.bottom -= WIDTH // 260 * 4
        print(ramp_top, player.rect.bottom)
    else:
        player.gravity = 0.5

    hits = pygame.sprite.spritecollide(player, cones, False, pygame.sprite.collide_mask)
    if hits:
        e = End()
        End.end_screen(e)
        running = False

    print("obstr", player.rect.right)

    if on_obstacle:
        player.rect.bottom = obstacle_top + 1
        print(player.rect.left, obstacle_hits.rect.right)
        if obstacle_hits.rect.right == WIDTH // 13 * 7:
            on_obstacle = False

    obstacles_hits = pygame.sprite.spritecollide(player, obstacles, False, pygame.sprite.collide_mask)
    if not on_obstacle and obstacles_hits and player.rect.bottom not in range(obstacles_hits[0].rect.top + 1,
                                                                              obstacles_hits[0].rect.bottom):
        print(player.rect.bottom, range(obstacles_hits[0].rect.top + 1, obstacles_hits[0].rect.bottom))
        e = End()
        end_scr.end_screen(e)
        running = False
    elif obstacles_hits:
        print(player.rect.bottom, range(obstacles_hits[0].rect.top + 2, obstacles_hits[0].rect.bottom))
        obstacle_hits = obstacles_hits[0]
        obstacle_top = obstacle_hits.rect.top
        player.rect.bottom = obstacle_top

        on_obstacle = True

    screen.fill((0, 0, 0))
    if background_x <= -WIDTH:
        background_x = 0
    if city_x <= -WIDTH:
        city_x = 0

    if fence_x <= -WIDTH:
        fence_x = 0

    screen.blit(background_image, (background_x, 300 // (1300 / WIDTH)))
    screen.blit(city_image, (city_x, 0))
    screen.blit(fence_image, (fence_x, 200 // (1300 / WIDTH)))

    score_text = font.render(str(count_points // 5), True, text_color)
    screen.blit(score_text, (WIDTH // 13 * 12, WIDTH // 26))

    clock.tick(FPS + count_points // 1000)
    print("speed:", FPS + count_points // 1000)
    all_sprites.draw(screen)
    pygame.display.flip()

pygame.quit()
