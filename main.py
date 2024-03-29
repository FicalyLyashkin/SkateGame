import random
import sys
import os
import pygame
import configparser
import pygame.mixer

WIDTH = 1300
HEIGHT = WIDTH // 13 * 9

FPS = 30
count_points = 0

jump = False
jump_on_ramp = False

lanes_y = [int(WIDTH // (1300 / 500)), int(WIDTH // (1300 / 700)), int(WIDTH // (1300 / 900))]
obstacle_lanes_y = [x - 50 for x in lanes_y]

levels = {1: "max_easy_points", 2: "max_medium_points", 3: "max_hard_points"}

all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
cones = pygame.sprite.Group()
ramps = pygame.sprite.Group()

last_level = 1
obj_speed = 10
ramp_y = 10


def load_image(name, colorkey=None):
    # Загружает фото
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    return image


def write_statistics(filename, points, level):
    # Записывает рекорды
    if int(load_statistics(filename, level)) < points:
        config = configparser.ConfigParser()
        config.read("data/" + filename)
        config.set("Statistics", levels[level], str(points))
        with open("data/" + filename, 'w') as f:
            config.write(f)


def load_statistics(filename, level):
    # Получает сведения о рекордах
    config = configparser.ConfigParser()
    config.read("data/" + filename)
    past_res = config["Statistics"][levels[level]]
    return past_res


class Obstacle(pygame.sprite.Sprite):
    # Спрайт трубы
    image = load_image("obstacle2.png")
    image = pygame.transform.scale(image, (WIDTH // 26 * 3, WIDTH // 26))

    def __init__(self, lane_y, lane_x=WIDTH):
        pygame.sprite.Sprite.__init__(self)
        self.image = Obstacle.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = lane_x
        self.rect.y = lane_y
        self.speedx = obj_speed

    def update(self):
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.kill()


class Cone(pygame.sprite.Sprite):
    # Спрайт конуса
    image = load_image("cone.png")
    image = pygame.transform.scale(image, (WIDTH // 26 * 2.4, WIDTH // 26 * 2.4))

    def __init__(self, lane_y, lane_x=WIDTH):
        pygame.sprite.Sprite.__init__(self)
        self.image = Cone.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = lane_x
        self.rect.y = lane_y - WIDTH // 13 // 2
        self.speedx = obj_speed

    def update(self):
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.kill()


class Ramp(pygame.sprite.Sprite):
    # Спрайт рампы
    image = load_image("ramp.png")
    image = pygame.transform.scale(image, (WIDTH // 26 * 1.8, WIDTH // 26 * 1.8))

    def __init__(self, lane_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = Ramp.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = WIDTH
        self.rect.y = lane_y - WIDTH // 26 * 1.8
        self.speedx = obj_speed

    def update(self):
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.kill()


class Player(pygame.sprite.Sprite):
    # Спрайт игрока
    def __init__(self, lanes_y, sheet, columns, rows):
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
        self.update_sprite = 0

    def cut_sheet(self, sheet, columns, rows):
        # Анимация игрока
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

    def update(self):
        self.update_sprite += 1
        if jump or jump_on_ramp:
            self.cur_frame = (self.cur_frame + 1) % len(self.frames)
            self.image = self.frames[1]
        elif self.update_sprite % 15 == 0:
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


def game(level):
    # Основной игровой процесс
    global jump, FPS, WIDTH, HEIGHT, count_points, obj_speed, jump_on_ramp, ramp_y

    player = Player(lanes_y,
                    pygame.transform.scale(load_image("skater_boy.png"), (200, 50)),
                    4, 1)
    all_sprites.add(player)

    background_x = 0
    background_speed = -obj_speed
    background_image = load_image("road.png")

    city_x = 0
    city_speed = -6.5
    city_image = load_image("city2.png")

    fence_x = 0
    fence_speed = -obj_speed
    fence_image = load_image("fence.png")

    font = pygame.font.Font(None, WIDTH // 26)
    text_color = pygame.Color("red")

    count_points = 0
    jump = False
    running = True
    count = 0
    jump_on_ramp = False
    count_jump_on_ramp = 0

    last_obstacle = 0
    last_cone = 0
    last_ramp = 0
    last_up = 0
    last_mid = 0
    last_down = 0
    on_obstacle = False

    pygame.mixer.music.play(-1, 0.0)
    while running:

        last_obstacle += 1
        last_cone += 1
        last_ramp += 1
        last_up += 1
        last_mid += 1
        last_down += 1

        # Генерация препядствий
        if random.randrange(100) < 60:

            random_obj = random.randint(0, 2)
            lane_y = random.choice(lanes_y)

            if (lane_y == lanes_y[0] and last_up > 30) or (lane_y == lanes_y[1] and last_mid > 30) or (
                    lane_y == lanes_y[2] and last_down > 30):

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
                        cone = Cone(lane_y - WIDTH // 13 // 2, lane_x=WIDTH + WIDTH // 13 // 2 * 1.5)
                        all_sprites.add(cone)
                        cones.add(cone)
                        last_cone = 0
                        last_ramp = 0

                    else:
                        ramp = Ramp(lane_y)
                        all_sprites.add(ramp)
                        ramps.add(ramp)
                        obstacle = Obstacle(lane_y - WIDTH // 13 // 2, lane_x=WIDTH + WIDTH // 13 // 2 * 1.9)
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
                e = End()
                End.end_screen(e, level)
                running = False

            elif event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_w and not jump and
                        player.rect.top > lanes_y[0]):
                    player.rect.y -= lanes_y[1] - lanes_y[0]

                elif (jump is False and event.key == pygame.K_s and
                      player.rect.bottom not in range(lanes_y[-2] + 1, lanes_y[-1] + 1)):
                    player.rect.y += lanes_y[1] - lanes_y[0]

                elif event.key == pygame.K_c and not jump and (player.rect.bottom in lanes_y
                                                               or player.rect.bottom in obstacle_lanes_y):
                    jump = True

        if jump:
            if count < 1:
                player.rect.y -= WIDTH // 130 * 11 // 2
            count += 1

            if count == 10:
                jump = False
                count = 0

        if jump_on_ramp:
            if count_jump_on_ramp < 1:
                player.rect.y -= 30
            count_jump_on_ramp += 1

            if count_jump_on_ramp == 10:
                count_jump_on_ramp = 0
                jump_on_ramp = False

        count_points += 1
        all_sprites.update()

        background_x += background_speed
        city_x += city_speed
        fence_x += fence_speed

        ramp_hits = pygame.sprite.spritecollide(player, ramps, False, pygame.sprite.collide_mask)
        if ramp_hits:
            player.gravity = 0
            ramp_hits = ramp_hits[0]

            if ramp_hits.rect.right == 651:
                jump_on_ramp = True
                pass
            player.rect.bottom -= ramp_y

        else:
            player.gravity = 0.6

        hits = pygame.sprite.spritecollide(player, cones, False, pygame.sprite.collide_mask)
        if hits:
            e = End()
            End.end_screen(e, level)
            running = False

        if on_obstacle:
            player.rect.bottom = obstacle_top
            if obstacle_hits.rect.right < player.rect.right:
                on_obstacle = False

        obstacles_hits = pygame.sprite.spritecollide(player, obstacles, False, pygame.sprite.collide_mask)
        if (not on_obstacle and obstacles_hits and
                player.rect.right - obstacles_hits[0].rect.left in range(0, WIDTH // 32)):
            e = End()
            End.end_screen(e, level)
            running = False

        elif obstacles_hits:
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

        clock.tick(FPS)
        all_sprites.draw(screen)
        pygame.display.flip()

    return


class Start:
    # Начально окно
    def __init__(self):
        self.light_easy = False
        self.light_medium = False
        self.light_hard = False

    def start_screen(self):
        global obj_speed, FPS, ramp_y

        records = dict()
        for x in range(1, 4):
            records[x] = load_statistics('statistics.txt', x)

        intro_text = ["SCATE GAME", "",
                      "W - Переход на дорожку выше",
                      "S - Переход на дорожку ниже",
                      "С - Прыжок", "",
                      "Рекорды:", "",
                      f"Easy: {records[1]}",
                      f"Medium: {records[2]}",
                      f"Hard: {records[3]}"]

        fon = pygame.transform.scale(load_image('city.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, WIDTH // 26)
        text_coord = WIDTH // 26
        k = 0

        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 1

            if "Easy" in line or "Medium" in line or "Hard" in line:
                k += 1
                if int(records[k]) > 50:
                    ach = pygame.transform.scale(load_image('achive2.png'), (20, 20))
                elif int(records[k]) > 150:
                    ach = pygame.transform.scale(load_image('achive3.png'), (20, 20))
                elif int(records[k]) > 350:
                    ach = pygame.transform.scale(load_image('achive4.png'), (20, 20))
                elif int(records[k]) > 650:
                    ach = pygame.transform.scale(load_image('achive5.png'), (20, 20))
                else:
                    ach = pygame.transform.scale(load_image('achive1.png'), (20, 20))
                screen.blit(ach, ((15, text_coord + 8)))

            intro_rect.top = text_coord
            intro_rect.x = WIDTH // 26
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        button_easy_rect = pygame.Rect(WIDTH // 3, (HEIGHT // 6 * 4) - 250, WIDTH // 3, HEIGHT // 10)
        button_medium_rect = pygame.Rect(WIDTH // 3, (HEIGHT // 6 * 4) - 150, WIDTH // 3, HEIGHT // 10)
        button_hard_rect = pygame.Rect(WIDTH // 3, (HEIGHT // 6 * 4) - 50, WIDTH // 3, HEIGHT // 10)

        button_easy_text = font.render("Easy", True, pygame.Color('black'))
        button_medium_text = font.render("Medium", True, pygame.Color('black'))
        button_hard_text = font.render("Hard", True, pygame.Color('black'))

        pygame.draw.rect(screen, pygame.Color(153, 192, 212), button_easy_rect, 0)
        pygame.draw.rect(screen, pygame.Color(153, 192, 212), button_medium_rect, 0)
        pygame.draw.rect(screen, pygame.Color(153, 192, 212), button_hard_rect, 0)

        screen.blit(button_easy_text, (button_easy_rect.x + WIDTH // 8, button_easy_rect.y + 25))
        screen.blit(button_medium_text, (button_medium_rect.x + WIDTH // 8, button_medium_rect.y + 25))
        screen.blit(button_hard_text, (button_hard_rect.x + WIDTH // 8, button_hard_rect.y + 25))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_easy_rect.collidepoint(event.pos):
                        obj_speed = 13
                        ramp_y = 10
                        game(1)
                    elif button_medium_rect.collidepoint(event.pos):
                        obj_speed = 26
                        ramp_y = 20
                        game(2)
                    elif button_hard_rect.collidepoint(event.pos):
                        obj_speed = 39
                        ramp_y = 30
                        game(3)

                elif event.type == pygame.MOUSEMOTION:
                    if button_easy_rect.collidepoint(event.pos):
                        self.light_easy = True
                    else:
                        self.light_easy = False

                    if button_medium_rect.collidepoint(event.pos):
                        self.light_medium = True
                    else:
                        self.light_medium = False

                    if button_hard_rect.collidepoint(event.pos):
                        self.light_hard = True
                    else:
                        self.light_hard = False

            if self.light_easy:
                pygame.draw.rect(screen, pygame.Color(210, 228, 236),
                                 button_easy_rect, 0)
            else:
                pygame.draw.rect(screen, pygame.Color(153, 192, 212),
                                 button_easy_rect, 0)

            if self.light_medium:
                pygame.draw.rect(screen, pygame.Color(210, 228, 236),
                                 button_medium_rect, 0)
            else:
                pygame.draw.rect(screen, pygame.Color(153, 192, 212),
                                 button_medium_rect, 0)

            if self.light_hard:
                pygame.draw.rect(screen, pygame.Color(210, 228, 236),
                                 button_hard_rect, 0)
            else:
                pygame.draw.rect(screen, pygame.Color(153, 192, 212),
                                 button_hard_rect, 0)

            screen.blit(button_easy_text, (button_easy_rect.x + WIDTH // 8, button_easy_rect.y + 25))
            screen.blit(button_medium_text, (button_medium_rect.x + WIDTH // 8, button_medium_rect.y + 25))
            screen.blit(button_hard_text, (button_hard_rect.x + WIDTH // 8, button_hard_rect.y + 25))

            pygame.display.flip()

    def terminate(self):
        pygame.quit()
        sys.exit()


class End:
    # Конечное окно
    def __init__(self):
        self.light_restart = False
        self.light_menu = False
        self.light_leave = False

    def end_screen(self, level):
        global last_level

        intro_text = ["ВЫ ПРОИГРАЛИ", "",
                      "Счёт: {}".format(count_points // 5)]
        write_statistics("statistics.txt", count_points // 5, level)

        pygame.mixer.music.stop()

        fon = pygame.transform.scale(load_image('city.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))

        font = pygame.font.Font(None, WIDTH // 13)
        font_buttons = pygame.font.Font(None, WIDTH // 26)
        text_coord = WIDTH // 20

        all_sprites.empty()
        obstacles.empty()
        cones.empty()
        ramps.empty()

        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 1
            intro_rect.top = text_coord
            intro_rect.x = WIDTH // 3
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)

        button_restart_rect = pygame.Rect(WIDTH // 3, (HEIGHT // 6 * 4) - 250, WIDTH // 3, HEIGHT // 10)
        button_menu_rect = pygame.Rect(WIDTH // 3, (HEIGHT // 6 * 4) - 150, WIDTH // 3, HEIGHT // 10)
        button_leave_rect = pygame.Rect(WIDTH // 3, (HEIGHT // 6 * 4) - 50, WIDTH // 3, HEIGHT // 10)

        button_restart_text = font_buttons.render("Попробовать заново", True, pygame.Color('black'))
        button_menu_text = font_buttons.render("Меню", True, pygame.Color('black'))
        button_leave_text = font_buttons.render("Выйти из игры", True, pygame.Color('black'))

        pygame.draw.rect(screen, pygame.Color(153, 192, 212), button_restart_rect, 0)
        pygame.draw.rect(screen, pygame.Color(153, 192, 212), button_menu_rect, 0)
        pygame.draw.rect(screen, pygame.Color(153, 192, 212), button_leave_rect, 0)

        screen.blit(button_restart_text, (button_restart_rect.x + WIDTH // 28, button_restart_rect.y + 25))
        screen.blit(button_menu_text, (button_menu_rect.x + WIDTH // 8, button_menu_rect.y + 25))
        screen.blit(button_leave_text, (button_leave_rect.x + WIDTH // 16, button_leave_rect.y + 25))

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.terminate()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if button_restart_rect.collidepoint(event.pos):
                        game(last_level)

                    elif button_menu_rect.collidepoint(event.pos):
                        s = Start()
                        Start.start_screen(s)

                    elif button_leave_rect.collidepoint(event.pos):
                        self.terminate()

                elif event.type == pygame.MOUSEMOTION:
                    if button_restart_rect.collidepoint(event.pos):
                        self.light_restart = True
                    else:
                        self.light_restart = False

                    if button_menu_rect.collidepoint(event.pos):
                        self.light_menu = True
                    else:
                        self.light_menu = False

                    if button_leave_rect.collidepoint(event.pos):
                        self.light_leave = True
                    else:
                        self.light_leave = False

            if self.light_restart:
                pygame.draw.rect(screen, pygame.Color(210, 228, 236),
                                 button_restart_rect, 0)
            else:
                pygame.draw.rect(screen, pygame.Color(153, 192, 212),
                                 button_restart_rect, 0)

            if self.light_menu:
                pygame.draw.rect(screen, pygame.Color(210, 228, 236),
                                 button_menu_rect, 0)
            else:
                pygame.draw.rect(screen, pygame.Color(153, 192, 212),
                                 button_menu_rect, 0)

            if self.light_leave:
                pygame.draw.rect(screen, pygame.Color(210, 228, 236),
                                 button_leave_rect, 0)
            else:
                pygame.draw.rect(screen, pygame.Color(153, 192, 212),
                                 button_leave_rect, 0)

            screen.blit(button_restart_text, (button_restart_rect.x + WIDTH // 28, button_restart_rect.y + 25))
            screen.blit(button_menu_text, (button_menu_rect.x + WIDTH // 8, button_menu_rect.y + 25))
            screen.blit(button_leave_text, (button_leave_rect.x + WIDTH // 16, button_leave_rect.y + 25))

            pygame.display.flip()

    def terminate(self):
        pygame.quit()
        sys.exit()


pygame.init()
pygame.mixer.init()
pygame.mixer.music.load("data/7e9f69ea4d60b9a.mp3")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))

