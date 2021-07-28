#!/usr/bin/env nix-shell
#!nix-shell -i python

from pygame import init, quit, event, key, display, QUIT, K_ESCAPE
from pygame.time import Clock
from pygame.display import set_mode

from enum import Enum

SCREEN_WIDTH = 800
SCREEN_HEIGH = 600
SCREEN = (SCREEN_WIDTH, SCREEN_HEIGH)

FPS = 60

GameState = Enum('GameState', 'Load Run Quit')

def main():
    print(f'resolution: {SCREEN}')
    print(f'frame rate: {FPS} fps')

    print('loading ...')
    game_state = GameState.Load
    init()
    clock = Clock()
    screen = set_mode(SCREEN)

    print('running ...')
    game_state = GameState.Run
    while game_state == GameState.Run:
        if event.get(QUIT):
            game_state = GameState.Quit

        if key.get_pressed()[K_ESCAPE]:
            game_state = GameState.Quit

        clock.tick(FPS)
        screen.fill('grey')
        display.update()

    print('goodbye.')
    quit()

if __name__ == '__main__':
    main()
