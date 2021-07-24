#!/usr/bin/env nix-shell
#!nix-shell -i python

import pygame as g
import pygame.sprite as s
import pygame.time as t

SCREEN_WIDTH = 800
SCREEN_HEIGH = 600
SCREEN = (SCREEN_WIDTH, SCREEN_HEIGH)
START = (int(SCREEN_WIDTH / 2), int(SCREEN_HEIGH / 2))

FPS = 60

class Ball(s.Sprite):
    def __init__(self):
        s.Sprite.__init__(self)
        self.x, self.y = (200,100)
        self.vx, self.vy = (0,0)
        self.ax, self.ay = (0,0.1)

        ball_tiles = g.image.load('./bouncng_basketball.png').convert_alpha()
        self.ball_images = g.Surface.subsurface(ball_tiles,0,0,200,200)
        self.ball_images = g.transform.scale(self.ball_images, (50, 50))
        self.image = g.Surface((50,50))
        self.rect = self.image.get_rect()
        self.rect.centerx = self.x
        self.rect.centery = self.y

    def update(self, delta_t):
        # NOTE: the microsec (/1000) timestep cause numerical instability
        #       less problem when velocity magnitude is low
        #       current acceleration is hand-tune
        self.vy += self.ay * delta_t / 10
        self.y += self.vy * delta_t / 10
        self.vx += self.ax * delta_t / 10
        self.x += self.vx * delta_t / 10
        # print('ball update', delta_t, self.y, self.vy)

        if self.y >= SCREEN_HEIGH - 100:
            self.y = SCREEN_HEIGH - 100
            self.vy = - self.vy * 0.8


        font = g.font.SysFont('sans', 15)
        vy_text = font.render(f'{self.vy:.0f}', False, 'green' if self.vy > 0 else 'blue')
        ay_text = font.render(f'{self.ay:.0f}', False, 'green' if self.ay > 0 else 'blue')
        self.image.fill('grey')
        self.image.blit(self.ball_images,(0,0))
        # self.image.blit(vy_text, (0,0))
        # self.image.blit(ay_text, (0,20))
        self.rect.centery = self.y
        pass

class Game(object):
    def __init__(self):
        g.init()
        self.screen = g.display.set_mode(SCREEN)
        self.tick_count = 0  # number of timer tick,
                             # use t.get_ticks() for elapse time since init

    def main_loop(self):
        clock = t.Clock()

        sprites = s.Group()
        sprites.add(Ball())

        # self.player = Player(sprites)

        ## timer event every half second
        tme = g.USEREVENT + 1
        t.set_timer(tme, 500)

        while True:
            for event in g.event.get():
                if event.type == g.QUIT:
                    return
                if event.type == g.KEYDOWN\
                and event.key == g.K_ESCAPE:
                    return
                if event.type == tme:
                    print('tick', self.tick_count, t.get_ticks() // 1000)
                    self.tick_count += 1

            self.screen.fill('grey')

            sprites.update(clock.get_time())

            sprites.draw(self.screen)

            g.display.update()


            clock.tick(FPS)


# class Player(s.Sprite):
#     def __init__(self, *groups):
#         super(Player, self).__init__(*groups)
#         self.image = g.image.load('player.png')
#         self.rect = g.rect.Rect(START, self.image.get_size())

#     def tick(self):
#         """
#         idle state update by timer
#         """
#         # print('plyer idle')
#         self.rect.x, self.rect.y = START


#     def update(self):
#         """
#         position update
#         """
#         key = g.key.get_pressed()
#         if key[g.K_LEFT] or key[g.K_h]:
#             self.rect.x -= 10
#         if key[g.K_RIGHT]or key[g.K_l]:
#             self.rect.x += 10
#         if key[g.K_UP] or key[g.K_k]:
#             self.rect.y -= 10
#         if key[g.K_DOWN] or key[g.K_j]:
#             self.rect.y += 10


if __name__ == '__main__':
    print(f'resolution: {SCREEN}')
    print(f'frame rate: {FPS} fps')

    game = Game()
    game.main_loop()
