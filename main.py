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


def main():
    parser = argparse.ArgumentParser(description='박스 러시 · Python + pico2d')
    parser.add_argument('--test-mode', action='store_true', help='구간 시간만 3초로 단축')
    args = parser.parse_args()
    import pico2d as p
    from render import Renderer

    game = Game(stage_seconds=3.0 if args.test_mode else STAGE_SECONDS)
    view = None
    p.open_canvas(WIDTH, HEIGHT, sync=True)
    p.hide_lattice()
    try:
        view = Renderer(args.test_mode)
        previous = time.perf_counter()
        running = True
        while running:
            now = time.perf_counter()
            dt = now - previous
            previous = now
            old_state = game.state
            running = handle_events(p.get_events(), game, p)
            if not running:
                break
            # 선택 화면에 머문 시간은 새 구간 시간에 포함하지 않는다.
            if game.state == old_state:
                game.update(dt)
            view.draw(game)
            p.delay(0.001)
    finally:
        if view is not None:
            view.close()
        p.close_canvas()


if __name__ == '__main__':
    main()
