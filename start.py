import sys

import main
import pygame
from functions import load_image
from CONST import *

# initializing the constructor
pygame.init()
clock = pygame.time.Clock()
class Start:
    def __init__(self):
        self.light = False

    def start_screen(self):
        intro_text = ["НАЗВАНИЕ ИГРЫ", "",
                  "Правила игры"]

        fon = pygame.transform.scale(load_image('city.png'), (WIDTH, HEIGHT))
        screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 50)
        text_coord = 50
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 1
            intro_rect.top = text_coord
            intro_rect.x = 50
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        pygame.draw.rect(screen, pygame.Color(153, 192, 212), (WIDTH // 3, HEIGHT // 6 * 4, WIDTH // 3, HEIGHT // 6), 0)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.pos[0] in range(WIDTH // 3, WIDTH // 3 * 2) and event.pos[1] in range(HEIGHT // 6 * 4, HEIGHT // 6 * 5):
                    return # начинаем игру
                elif event.type == pygame.MOUSEMOTION:
                    if event.pos[0] in range(WIDTH // 3, WIDTH // 3 * 2) and event.pos[1] in range(HEIGHT // 6 * 4, HEIGHT // 6 * 5):
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

screen = pygame.display.set_mode((WIDTH, HEIGHT))
s = Start()
Start.start_screen(s)