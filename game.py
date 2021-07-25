#!/usr/bin/env nix-shell
#!nix-shell -i python

import pygame

from enum import Enum
from random import choice, randint

def center(wh):
    w,h = wh
    return (int(w/2), int(h/2))

def half(f):
    return int(f/2)

SCREEN_WIDTH = 800
SCREEN_HEIGH = 600
SCREEN = (SCREEN_WIDTH, SCREEN_HEIGH)

FPS = 60


MARGIN = 25
MARGIN_L = MARGIN
MARGIN_R = SCREEN_WIDTH - MARGIN
MARGIN_T = MARGIN
MARGIN_B = SCREEN_HEIGH - MARGIN

FPS = 60

# debugging utility
def draw_magin(screen):
    pygame.draw.polygon(screen, 'red',[
       (MARGIN_L,MARGIN_T), (MARGIN_R,MARGIN_T),
       (MARGIN_R,MARGIN_B), (MARGIN_L,MARGIN_B),
      ], 1)

def rand_pos():
    x = randint(MARGIN_L, MARGIN_R)
    y = randint(MARGIN_T, MARGIN_B)
    return x,y

VECTOR_COLOR = 'green'
VECTOR_SCALE = 10

# TODO: draw vectors arrow
def draw_vector(screen, point, value):
    x,y = point
    dx,dy = value
    s = VECTOR_SCALE
    h = (x+dx*s, y+dy*s)
    pygame.draw.line(screen, VECTOR_COLOR, point, h, 1)
    pygame.draw.circle(screen, VECTOR_COLOR, h, 2)


ENTITY_WIDTH = MARGIN * 2
ENTITY_HEIGHT = ENTITY_WIDTH
ENTITY_SIZE = (ENTITY_WIDTH,ENTITY_HEIGHT)
ENTITY_CENTER = center(ENTITY_SIZE)

EntityState = Enum('EntityState', 'STOP MOVE')

def rand_enum(s):
    return choice(list(s))


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # pygame.sprites.Sprite.__init__(self)
        # NOTE: physics accurateed value my not work as expected
        #       need to investigate more
        self.x, self.y = rand_pos()
        self.vx, self.vy = (randint(-10,10),randint(-10,10))
        self.ax, self.ay = (0,0.1)

        self.image = pygame.Surface(ENTITY_SIZE, pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y

    def update(self, delta_t):
        def is_vzero(v):
            VZ_TSH = 0.1
            return abs(v) < VZ_TSH
        def is_stop():
            return is_vzero(self.vx) and is_vzero(self.vy)

        self.state = EntityState.STOP if is_stop() else EntityState.MOVE

        # NOTE: the microsec (/1000) timestep cause numerical instability
        #       less problem when velocity magnitude is low
        #       current acceleration is hand-tune
        self.vy += self.ay * delta_t / 10
        self.y += self.vy * delta_t / 10
        self.vx += self.ax * delta_t / 10
        self.x += self.vx * delta_t / 10
        # print('ball update', delta_t, self.y, self.vy)

        # floor resistance (when ball is sliding on the floor)
        if is_vzero(self.vy):
            self.vx = self.vx * 0.8

        # check for screen bound and bouncing
        # vertical wall is slipper (less momentum lossed)
        # while horizontal wall have more resistance
        if self.y >= SCREEN_HEIGH - ENTITY_WIDTH:
            self.y = SCREEN_HEIGH - ENTITY_WIDTH
            self.vy = - self.vy * 0.8
        elif self.y <= ENTITY_WIDTH:
            self.y = ENTITY_WIDTH
            self.vy = - self.vy * 0.8

        if self.x <= ENTITY_WIDTH:
            self.x = ENTITY_WIDTH
            self.vx = - self.vx * 0.95
        elif self.x >= SCREEN_WIDTH - ENTITY_WIDTH:
            self.x = SCREEN_WIDTH - ENTITY_WIDTH
            self.vx = - self.vx * 0.95


        font = pygame.font.SysFont('sans', 15)
        vy_text = font.render(f'vy:{self.vy:.0f}', False,
          'green' if self.vy > 0 else 'blue')
        vx_text = font.render(f'vx:{self.vx:.0f}', False,
          'green' if self.vy > 0 else 'blue')

        half_w = half(ENTITY_WIDTH)
        self.image.fill((255,255,255,1))
        pygame.draw.circle(self.image, 'red' if self.state == EntityState.MOVE else 'pink',
                ENTITY_CENTER, half_w)
        self.image.blit(vx_text, (0,0))
        self.image.blit(vy_text, (0,20))
        draw_vector(self.image, ENTITY_CENTER, (self.vx,self.vy))
        self.rect.centery = self.y
        self.rect.centerx = self.x


GameState = Enum('GameState', 'Load Run Quit')

class Game():
    def __init__(self):
        self.state = GameState.Load
        pygame.init()

    def run(self):
        self.state = GameState.Run
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode(SCREEN)

        sprites = pygame.sprite.Group()
        for _ in range(10):
            sprites.add(Ball())

        while self.state == GameState.Run:
            if pygame.event.get(pygame.QUIT):
                self.state = GameState.Quit

            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                self.state = GameState.Quit

            delta_t = clock.tick(FPS)

            screen.fill('grey')

            sprites.update(delta_t)
            sprites.draw(screen)

            pygame.display.update()

        pygame.quit()


def main():
    print(f'resolution: {SCREEN}')
    print(f'frame rate: {FPS} fps')

    print('loading ...')
    game = Game()

    print('running ...')
    game.run()

    print('goodbye.')


if __name__ == '__main__':
    main()
