#!/usr/bin/env nix-shell
#!nix-shell -i python

import pygame as g
import pygame.sprite as s
import pygame.time as t

SCREEN_WIDTH = 800
SCREEN_HEIGH = 600
SCREEN = (SCREEN_WIDTH, SCREEN_HEIGH)

FPS = 60

TILE_BASE = 32

class World(s.Sprite):
    def __init__(self):
        super().__init__()

        self.image = g.Surface(SCREEN)
        self.image.fill((40,40,40))

        ground_tile = g.image.load('./assets/Texture/TX Tileset Ground.png').convert_alpha()
        step = TILE_BASE
        g1 = ground_tile.subsurface(0,0,step,step)
        g2 = ground_tile.subsurface(step,0,step,step)
        g3 = ground_tile.subsurface(step * 2,0,step,step)
        # g3.fill('red')
        self.image.blit(ground_tile, (0,0))

        bold = [x for x in range(0, SCREEN_WIDTH, TILE_BASE * 3)]
        # draw helper grid point every TILE_BASE pixel
        for i in range(0,SCREEN_WIDTH, TILE_BASE):
            for j in range(0,SCREEN_HEIGH, TILE_BASE):
                g.draw.circle(self.image,
                  'green' if i in bold or j in bold else 'red', (i,j), 2)

        # ground floor
        for i in range(0,SCREEN_WIDTH,TILE_BASE*2):
            self.image.blit(g3,(i,SCREEN_HEIGH - 100))

        self.images = [g1,g2]
        self.rect = self.image.get_rect()


class Game(object):
    def __init__(self):
        g.init()
        self.screen = g.display.set_mode(SCREEN)

    def main_loop(self):
        clock = t.Clock()

        sprites = s.Group()
        sprites.add(World())

        while True:
            for event in g.event.get():
                if event.type == g.QUIT:
                    return
                if event.type == g.KEYDOWN\
                and event.key == g.K_ESCAPE:
                    return

            self.screen.fill('grey')

            sprites.draw(self.screen)

            g.display.update()

            clock.tick(FPS)

if __name__ == '__main__':
    print(f'resolution: {SCREEN}')
    print(f'frame rate: {FPS} fps')

    game = Game()
    game.main_loop()
