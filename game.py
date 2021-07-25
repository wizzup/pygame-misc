#!/usr/bin/env nix-shell
#!nix-shell -i python

from enum import Enum
from random import choice, randint

import pygame as g
import pygame.sprite as s
import pygame.time as t

def center(wh):
    w,h = wh
    return (int(w/2), int(h/2))

def half(f):
    return int(f/2)

SCREEN_WIDTH = 800
SCREEN_HEIGH = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGH)
SCREEN_CENTER = center(SCREEN_SIZE)

MARGIN = 25
MARGIN_L = MARGIN
MARGIN_R = SCREEN_WIDTH - MARGIN
MARGIN_T = MARGIN
MARGIN_B = SCREEN_HEIGH - MARGIN

FPS = 60

# debugging utility
def draw_magin(screen):
    g.draw.polygon(screen, 'red',[
       (MARGIN_L,MARGIN_T), (MARGIN_R,MARGIN_T),
       (MARGIN_R,MARGIN_B), (MARGIN_L,MARGIN_B),
      ], 1)

def rand_pos():
    x = randint(MARGIN_L, MARGIN_R)
    y = randint(MARGIN_T, MARGIN_B)
    return x,y

ENTITY_WIDTH = MARGIN * 2
ENTITY_HEIGHT = ENTITY_WIDTH
ENTITY_SIZE = (ENTITY_WIDTH,ENTITY_HEIGHT)
ENTITY_CENTER = center(ENTITY_SIZE)

EntityState = Enum('EntityState', 'STOP MOVE')

def rand_state():
    return choice(list(State))

def rand_dir():
    return choice(list(Direction))

VECTOR_COLOR = 'green'
VECTOR_SCALE = 10

# TODO: draw vectors arrow
def draw_vector(screen, point, value):
    x,y = point
    dx,dy = value
    s = VECTOR_SCALE
    h = (x+dx*s, y+dy*s)
    g.draw.line(screen, VECTOR_COLOR, point, h, 1)
    g.draw.circle(screen, VECTOR_COLOR, h, 2)


class Ball(s.Sprite):
    def __init__(self):
        s.Sprite.__init__(self)
        # NOTE: physics accurateed value my not work as expected
        #       need to investigate more
        self.x, self.y = rand_pos()
        self.vx, self.vy = (randint(-10,10),randint(-10,10))
        self.ax, self.ay = (0,0.1)

        self.image = g.Surface(ENTITY_SIZE, g.SRCALPHA)
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


        font = g.font.SysFont('sans', 15)
        vy_text = font.render(f'vy:{self.vy:.0f}', False,
          'green' if self.vy > 0 else 'blue')
        vx_text = font.render(f'vx:{self.vx:.0f}', False,
          'green' if self.vy > 0 else 'blue')

        half_w = half(ENTITY_WIDTH)
        self.image.fill((255,255,255,1))
        g.draw.circle(self.image, 'red' if self.state == EntityState.MOVE else 'pink',
                ENTITY_CENTER, half_w)
        self.image.blit(vx_text, (0,0))
        self.image.blit(vy_text, (0,20))
        draw_vector(self.image, ENTITY_CENTER, (self.vx,self.vy))
        self.rect.centery = self.y
        self.rect.centerx = self.x

GameState = Enum('GameState', 'QUIT RUN')


class Game(object):
    def __init__(self):
        g.init()
        self.screen = g.display.set_mode(SCREEN_SIZE)
        self.tick_count = 0  # number of timer tick,
                             # use t.get_ticks() for elapse time since init
        self.state = GameState.RUN

    def main_loop(self):
        clock = t.Clock()

        sprites = s.Group()
        for _ in range(10):
            sprites.add(Ball())

        ## timer event every half second
        tme = g.USEREVENT + 1
        t.set_timer(tme, 500)

        # drawing loop
        while self.state == GameState.RUN:
            for event in g.event.get():
                if event.type == g.QUIT:
                    self.state = GameState.QUIT
                    # return
                if event.type == g.KEYDOWN\
                and event.key == g.K_ESCAPE:
                    self.state = GameState.QUIT
                    # return
                if event.type == tme:
                    # print('tick', self.tick_count, t.get_ticks() // 1000)
                    for i in sprites.sprites():
                        if i.state == EntityState.STOP:
                            # print(i.vx, i.vy)
                            i.kill()
                            sprites.add(Ball())
                    self.tick_count += 1

            self.screen.fill('grey')
            draw_magin(self.screen)

            sprites.update(clock.get_time())

            sprites.draw(self.screen)

            g.display.update()


            clock.tick(FPS)

        if self.state == GameState.QUIT:
            g.quit()
            exit()


if __name__ == '__main__':
    print(f'resolution: {SCREEN_SIZE}')
    print(f'frame rate: {FPS} fps')

    game = Game()
    game.main_loop()
