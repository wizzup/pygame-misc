#!/usr/bin/env nix-shell
#!nix-shell -i python

import pygame

from enum import Enum
from random import randint

def center(wh):
    w,h = wh
    return (half(w), half(h))

def half(f):
    return int(f/2)

SCREEN_WIDTH = 800
SCREEN_HEIGH = 600
SCREEN = (SCREEN_WIDTH, SCREEN_HEIGH)
SCREEN_CENTER = center(SCREEN)

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

ENTITY_WIDTH = MARGIN * 2
ENTITY_HEIGHT = ENTITY_WIDTH
ENTITY_SIZE = (ENTITY_WIDTH,ENTITY_HEIGHT)
ENTITY_CENTER = center(ENTITY_SIZE)

# velocity vector visual
VECTOR_COLOR = 'green'
VECTOR_SCALE = 10

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

EntityState = Enum('EntityState', 'STOP MOVE EAT')


class Ball(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.pos = pygame.Vector2(rand_pos())
        self.vel = pygame.Vector2(0,0)
        self.acl = pygame.Vector2(0,0)

        self.image = pygame.Surface(ENTITY_SIZE, pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        self.state = EntityState.STOP
        self.health = 100

    def update(self, delta_t, target):
        self.target = pygame.Vector2(target)
        self.heading = (self.target - self.pos).normalize()

        if (self.pos - self.target).magnitude() < half(ENTITY_WIDTH):
            self.vel.update((0,0))
            self.state = EntityState.EAT
            self.health += 10
        elif self.health <= 0:
            self.state = EntityState.STOP
        else:
            self.state = EntityState.MOVE

        def do_physics():
            ## constant acceleration
            self.acl = self.heading * 100
            self.vel += self.acl * delta_t

            # constant speed movement
            # SPEED = 200
            # self.vel += self.heading * SPEED * delta_t

            delta_p = self.vel * delta_t
            self.pos += delta_p
            self.health -= delta_p.magnitude() * 0.01

        def apply_constrain():
            # don't move beyond margin box
            # slow down and bounce back
            if self.pos.x <= MARGIN_L:
                self.vel.reflect_ip(pygame.Vector2(1,0))
                self.vel *= 0.8
            elif self.pos.x >= MARGIN_R:
                self.vel.reflect_ip(pygame.Vector2(-1,0))
                self.vel *= 0.8

            if self.pos.y <= MARGIN_T:
                self.vel.reflect_ip(pygame.Vector2(0,1))
                self.vel *= 0.8
            elif self.pos.y >= MARGIN_B:
                self.vel.reflect_ip(pygame.Vector2(0,-1))
                self.vel *= 0.8

        def draw_ball():
            half_w = half(ENTITY_WIDTH)
            self.image.fill((255,255,255,1))
            colors = {
                EntityState.STOP: 'grey',
                EntityState.MOVE: 'red',
                EntityState.EAT: 'blue'
                }
            color = colors[self.state]
            pygame.draw.circle(self.image, color, ENTITY_CENTER, half_w)
            self.rect.center = int(self.pos.x), int(self.pos.y)

        # TODO: move to overlay layer
        def draw_vel():
            font = pygame.font.SysFont('sans', 12)
            vy_text = font.render(f'vy:{self.vel.y:+.1f}', False,
              'green' if self.vel.y > 0 else 'blue')
            vx_text = font.render(f'vx:{self.vel.x:+.1f}', False,
              'green' if self.vel.x > 0 else 'blue')
            self.image.blit(vx_text, (0,0))
            self.image.blit(vy_text, (0,20))

            draw_vector(self.image, ENTITY_CENTER, (self.vel.x,self.vel.y))
            draw_vector(self.image, ENTITY_CENTER, self.heading)

        def draw_health():
            font = pygame.font.SysFont('sans', 12)
            text = font.render(f'h:{self.health:.0f}', False, 'green' if self.health > 10 else 'blue')
            text_rect = text.get_rect()
            text_rect.center = ENTITY_CENTER
            self.image.blit(text, text_rect)

        if self.state != EntityState.STOP:
            do_physics()
            # draw_vel()

        draw_ball()
        draw_health()
        apply_constrain()



GameState = Enum('GameState', 'Load Run Quit')

class Game():
    def __init__(self):
        self.state = GameState.Load
        pygame.init()

    def run(self):
        self.state = GameState.Run

        target = (SCREEN_CENTER)
        def draw_target():
            pygame.draw.circle(screen, 'green', target, 5)

        screen = pygame.display.set_mode(SCREEN)
        clock = pygame.time.Clock()

        balls = pygame.sprite.Group()
        for _ in range(10):
            balls.add(Ball())

        while self.state == GameState.Run:
            if pygame.event.get(pygame.QUIT):
                self.state = GameState.Quit

            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                self.state = GameState.Quit

            delta_t = clock.tick(FPS) / 1000

            screen.fill('grey')
            draw_magin(screen)

            draw_target()

            # if randint(1,100) == 5:
            #     target = rand_pos()

            # pop a new food if somebody ate it
            for b in balls:
                if b.state == EntityState.EAT:
                    target = rand_pos()

            balls.update(delta_t, target)
            balls.draw(screen)

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
