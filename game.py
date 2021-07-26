#!/usr/bin/env nix-shell
#!nix-shell -i python

from enum import Enum

import pygame as g
import pygame.time as t

def center(wh):
    w,h = wh
    return (int(w/2), int(h/2))

def half(f):
    return int(f/2)

STEP = 50
SCREEN_WIDTH = 16 * STEP
SCREEN_HEIGH = SCREEN_WIDTH
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGH)
SCREEN_CENTER = center(SCREEN_SIZE)

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

        def handle_events():
            if g.event.get(g.QUIT):
                self.state = GameState.QUIT

            for e in g.event.get(g.KEYDOWN):
                if e.key == g.K_ESCAPE:
                    self.state = GameState.QUIT
                else:
                    g.event.post(e)

            for e in  g.event.get(g.MOUSEBUTTONUP):
                self.target = e.pos

        def make_grids():
            grids = []
            for i in range(0,SCREEN_HEIGH,STEP):
                for j in range(0,SCREEN_HEIGH,STEP):
                    s = g.Surface((STEP,STEP))
                    s.fill('white')
                    r = s.get_rect()
                    r.topleft = (i,j)
                    grids.append((s,r))
            return grids

        def draw_grids():
            for i in range(0,SCREEN_HEIGH,STEP):
                g.draw.line(self.screen,'black',(0,i),(SCREEN_WIDTH, i))
                g.draw.line(self.screen,'black',(i,0),(i,SCREEN_HEIGH))

        clock = t.Clock()
        grids = make_grids()

        # drawing loop
        while self.state == GameState.RUN:
            clock.tick()

            handle_events()

            # # catch unhandled events
            # for event in g.event.get():
            #     print(event)

            self.screen.fill('grey')

            for i in grids:
                mb = g.mouse.get_pressed()
                mp = g.mouse.get_pos()
                if mb[0] and i[1].collidepoint(mp):
                    i[0].fill('black')
                if mb[2] and i[1].collidepoint(mp):
                    i[0].fill('white')
                self.screen.blit(i[0], i[1])

            draw_grids()

            g.display.update()

        if self.state == GameState.QUIT:
            g.quit()
            exit()


if __name__ == '__main__':
    print(f'resolution: {SCREEN_SIZE}')

    game = Game()
    game.main_loop()
