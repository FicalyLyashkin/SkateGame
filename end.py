import sys

import main
import pygame
from functions import load_image
from CONST import *


pygame.init()
clock = pygame.time.Clock()


class End:
    def __init__(self):
        self.on_btn = False

    def end_screen(self):
        intro_text = ["ВЫ ПРОИГРАЛИ", "",
                      "Счёт: {}".format(main.count_points)]

        screen.fill(pygame.Color(153, 192, 212))
        font = pygame.font.Font(None, 70)
        text_coord = 50
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
                    terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN and event.pos[0] in range(btn_coords[0], btn_coords[0] * 2) and \
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


screen = pygame.display.set_mode((WIDTH, HEIGHT))
