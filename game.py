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

Direction = Enum('Direction', 'N S E W NE NW SE SW')
EntityState = Enum('EntityState', 'STOP MOVE')

# random helpers
def rand_enum(e):
    return choice(list(e))

def rand_state():
    return rand_enum(EntityState)

def rand_dir():
    return rand_enum(Direction)


# velocity vector visual
VECTOR_COLOR = 'green'
VECTOR_SCALE = 10

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
        # NOTE: physics accurate value my not work as expected
        #       need to investigate more
        self.x, self.y = rand_pos()
        self.vx, self.vy = (0,0)
        self.ax, self.ay = (0,0)
        self.target = self.x, self.y

        self.image = g.Surface(ENTITY_SIZE, g.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = int(self.x), int(self.y)

        self.tick = 0
        self.state = EntityState.STOP

    def update(self, delta_t, target):
        self.target = target
        self.tick += 1

        def signum(x):
            if int(x) < 0:
                return -1
            elif int(x) > 0:
                return 1
            else:
                return x

        def is_stop():
            if (self.vx, self.vy) == (0,0):
                self.ax, self.ay = (0,0)
                self.state = EntityState.STOP
                return True
            else:
                self.state = EntityState.MOVE

        def compute_state():
            # TODO: for re-enforcement learning AI
            # input: entity state (x,y,health,...)
            # output: new target to move to
            pass

        def move_to_target():
            def do(v,a,d):
                # stop when touching
                r = half(ENTITY_WIDTH)
                if abs(d) <= r:
                    a = 0
                    v = 0
                # keep moving in the same direction
                # or pull if not currently moving
                elif d >= r:
                    a = 100 if v == 0 else -100 if v < 0 else a
                # FIXME: don't sure if this is right
                #        movement is strange when turning back to target
                #        but can't find what is wrong
                elif d <= r:
                    a = -100 if v ==0 else -100 if v > 0 else a

                return (v,a)

            target_x, target_y = self.target
            dx = target_x - self.x
            dy = target_y - self.y

            self.vx, self.ax = do(self.vx,self.ax,dx)
            self.vy, self.ay = do(self.vy,self.ay,dy)

        def do_physics():
            # move according to physics
            # NOTE: the microsec (/1000) timestep
            #       sometime cause numerical instability
            #       less problem when velocity magnitude is low
            #       current acceleration is hand-tune
            def do(p,v,a):
                v += a * delta_t / 1000
                p += v * delta_t / 1000
                return (p,v)

            self.x, self.vx = do(self.x,self.vx,self.ax)
            self.y, self.vy = do(self.y,self.vy,self.ay)

        def apply_constrain():
            # limit maximum absolute value
            def lim_max(v,mx):
                v = min(abs(v), mx) * signum(v)
                return v

            # maximum velocity allow
            # no need to limit acceleration since
            # this will always become terminal speed
            MAX_VEL = 500
            self.vx = lim_max(self.vx,MAX_VEL)
            self.vy = lim_max(self.vy,MAX_VEL)

            # don't move beyond margin box
            # also don't try to move out the margin
            if self.x <= MARGIN_L:
                self.x = max(self.x, MARGIN_L)
                self.vx = 0 if self.vx < 0 else self.vx
                self.ax = 0 if self.ax < 0 else self.ax
            elif self.x >= MARGIN_R:
                self.x = min(self.x, MARGIN_R)
                self.vx = 0 if self.vx > 0 else self.vx
                self.ax = 0 if self.ax > 0 else self.ax

            if self.y <= MARGIN_T:
                self.y = max(self.y, MARGIN_T)
                self.vy = 0 if self.vy < 0 else self.vy
                self.ay = 0 if self.ay < 0 else self.ay
            elif self.y >= MARGIN_B:
                self.y = min(self.y, MARGIN_B)
                self.vy = 0 if self.vy > 0 else self.vy
                self.ay = 0 if self.ay > 0 else self.ay

        is_stop()
        compute_state()
        move_to_target()
        apply_constrain()
        do_physics()

        half_w = half(ENTITY_WIDTH)
        self.image.fill((255,255,255,1))
        g.draw.circle(self.image, 'red' if self.state == EntityState.MOVE else 'pink',
                ENTITY_CENTER, half_w)

        font = g.font.SysFont('sans', 12)
        vy_text = font.render(f'vy:{self.vy:+.1f}', False,
          'green' if self.vy > 0 else 'blue')
        vx_text = font.render(f'vx:{self.vx:+.1f}', False,
          'green' if self.vx > 0 else 'blue')
        self.image.blit(vx_text, (0,0))
        self.image.blit(vy_text, (0,20))

        draw_vector(self.image, ENTITY_CENTER, (self.vx,self.vy))
        self.rect.center = int(self.x), int(self.y)
        # print(f'update x{self.x:.1f} y{self.y:.1f} vx{self.vx:.1f} vy{self.vy:.1f}')


GameState = Enum('GameState', 'QUIT RUN')


class Game(object):
    def __init__(self):
        g.init()
        self.screen = g.display.set_mode(SCREEN_SIZE)
        self.tick_count = 0  # number of timer tick,
                             # use t.get_ticks() for elapse time since init
        self.state = GameState.RUN
        self.target = (SCREEN_CENTER)

    def main_loop(self):

        def handle_evens():
            if g.event.get(g.QUIT):
                self.state = GameState.QUIT

            for e in g.event.get(g.KEYDOWN):
                if e.key == g.K_ESCAPE:
                    self.state = GameState.QUIT
                else:
                    g.event.post(e)

            # # no matter how many timer events in queue
            # # assume timer is not faster than drawing loop
            # if g.event.get(TIMER):
            #     for i in sprites.sprites():
            #         if i.state == EntityState.STOP:
            #             # print(i.vx, i.vy)
            #                 i.kill()
            #                 sprites.add(Ball())
            #         self.tick_count += 1

            for e in  g.event.get(g.MOUSEBUTTONUP):
                self.target = e.pos

        def draw_target():
            g.draw.circle(self.screen, 'green', self.target, 5)
            pass

        clock = t.Clock()

        sprites = s.Group()
        for _ in range(10):
            sprites.add(Ball())
        # sprites.add(Ball())

        ## timer event every half second
        TIMER = g.USEREVENT + 1
        t.set_timer(TIMER, 500)


        # drawing loop
        while self.state == GameState.RUN:
            handle_evens()

            # # catch unhandled events
            # for event in g.event.get():
            #     print(event)

            self.screen.fill('grey')

            draw_magin(self.screen)

            draw_target()

            sprites.update(clock.get_time(), self.target)

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
