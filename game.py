#!/usr/bin/env nix-shell
#!nix-shell -i python

import pygame

from enum import Enum

SCREEN_WIDTH = 800
SCREEN_HEIGH = 600
SCREEN = (SCREEN_WIDTH, SCREEN_HEIGH)

FPS = 60

GameState = Enum('GameState', 'Load Run Quit')

class Game():
    def __init__(self):
        self.state = GameState.Load
        pygame.init()

    def run(self):
        self.state = GameState.Run
        clock = pygame.time.Clock()
        screen = pygame.display.set_mode(SCREEN)

        while self.state == GameState.Run:
            if pygame.event.get(pygame.QUIT):
                self.state = GameState.Quit

            if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                self.state = GameState.Quit

            clock.tick(FPS)
            screen.fill('grey')
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
