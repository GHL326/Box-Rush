"""실행: python main.py / 빠른 구간 테스트: python main.py --test-mode"""
import argparse
import time

from config import HEIGHT, STAGE_SECONDS, WIDTH
from game import Game


def handle_events(events, game, api):
    keys = {api.SDLK_RETURN: 'enter', api.SDLK_KP_ENTER: 'enter',
            api.SDLK_UP: 'up', api.SDLK_DOWN: 'down',
            api.SDLK_LEFT: 'left', api.SDLK_RIGHT: 'right', api.SDLK_r: 'r'}
    for event in events:
        if event.type == api.SDL_QUIT:
            return False
        if event.type == api.SDL_KEYDOWN:
            if event.key == api.SDLK_ESCAPE:
                return False
            command = keys.get(event.key)
            if command:
                game.command(command)
    return True


