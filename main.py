import random
import sys
from start import *
from end import *

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, lane_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((150, 50))
        self.image.fill((0, 0, 255))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = lane_y
        self.speedx = 15

    def update(self):
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.kill()


class Cone(pygame.sprite.Sprite):
    image = load_image("cone.png")
    image = pygame.transform.scale(image, (120, 120))

    def __init__(self, lane_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = Cone.image
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = WIDTH
        self.rect.y = lane_y - 50
        self.speedx = 15

    def update(self):
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.kill()


class Ramp(pygame.sprite.Sprite):
    def __init__(self, lane_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((20, 20))
        self.image.fill((255, 255, 0))
        self.rect = self.image.get_rect()
        self.rect.x = WIDTH
        self.rect.y = lane_y - 10
        self.speedx = 15

    def update(self):
        self.rect.x -= self.speedx
        if self.rect.right < 0:
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, lanes_y):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((50, 50))
        self.image.fill(pygame.Color("green"))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.y = lanes_y[1] - self.rect.height
        self.speedy = 0
        self.gravity = 0.5

    def update(self):
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


all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()
cones = pygame.sprite.Group()
ramps = pygame.sprite.Group()
lanes_y = [500, 700, 900]

player = Player(lanes_y)
all_sprites.add(player)
background_image = load_image("road.png")
city_image = load_image("city2.png")
fence_image = load_image("fence.png")
background_x = 0
background_speed = -15
city_x = 0
city_speed = -9
fence_x = 0
fence_speed = -13

count_points = 0
font = pygame.font.Font(None, 36)
text_color = pygame.Color("red")
jump = False
running = True
count = 0
count_ramp_hits = 0

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                if player.rect.top > lanes_y[0]:
                    player.rect.y -= 200
            elif event.key == pygame.K_s:
                if player.rect.bottom < lanes_y[-1]:
                    player.rect.y += 200
            elif event.key == pygame.K_c and player.rect.y in [ \
                    x - 50 for x in lanes_y
            ]:
                jump = True

    if jump:
        if count < 1:
            player.rect.y -= 55
        count += 1
        if count == 10:
            jump = False
            count = 0
    count_points += 1
    all_sprites.update()

    if random.randrange(100) < 3:
        random_obj = random.randint(0, 2)
        if random_obj == 1:
            lane_y = random.choice(lanes_y)
            obstacle = Obstacle(lane_y - 50)
            all_sprites.add(obstacle)
            obstacles.add(obstacle)
        elif random_obj == 2:
            lane_y = random.choice(lanes_y)
            cone = Cone(lane_y - 50)
            all_sprites.add(cone)
            cones.add(cone)
        else:
            lane_y = random.choice(lanes_y)
            ramp = Ramp(lane_y)
            all_sprites.add(ramp)
            ramps.add(ramp)

    background_x += background_speed
    city_x += city_speed
    fence_x += fence_speed
    ramp_hits = pygame.sprite.spritecollide(player, ramps, False)

    if ramp_hits:
        count_ramp_hits += 1
        if count_ramp_hits == 1:
            player.rect.y -= 100
            player.speedy = 0
            count_ramp_hits = 0
            jump = False

    hits = pygame.sprite.spritecollide(player, cones, False, pygame.sprite.collide_mask)
    if hits:
        e = End()
        End.end_screen(e)
        running = False

    screen.fill((0, 0, 0))
    if background_x <= -1300:
        background_x = 0

    if city_x <= -1300:
        city_x = 0

    if fence_x <= -1300:
        fence_x = 0

    screen.blit(background_image, (background_x, 300))
    screen.blit(city_image, (city_x, 0))
    screen.blit(fence_image, (fence_x, 200))

    score_text = font.render(str(count_points // 5), True, text_color)
    screen.blit(score_text, (1100, 50))

    clock.tick(FPS)
    all_sprites.draw(screen)
    pygame.display.flip()


pygame.quit()
