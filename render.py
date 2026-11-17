"""이미지를 한 번 로드하고 각 상태의 화면을 그린다. 좌표 원점은 왼쪽 아래."""
import ctypes
import math
import os
from pathlib import Path

import pico2d as p
from sdl2.sdlttf import TTF_SizeUTF8

from config import (
    COOLDOWNS, INITIAL_HEALTH, OBSTACLE_SIZES, PLAYER_SIZE, PLAYER_Y,
    POINTS_PER_BOX, TARGET_SCORE,
)

ROOT = Path(__file__).resolve().parent
WHITE = (246, 242, 229)
MUTED = (166, 184, 202)
ORANGE = (255, 164, 79)
GREEN = (115, 221, 174)
RED = (255, 130, 115)
NAVY = (16, 31, 49)


def find_font():
    candidates = [
        os.environ.get('BOX_RUSH_FONT', ''),
        str(ROOT / 'resources' / 'font.ttf'),
        str(Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts' / 'malgun.ttf'),
        '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
        '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
        '/System/Library/Fonts/AppleSDGothicNeo.ttc',
    ]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            return candidate
    raise FileNotFoundError('한글 폰트를 찾지 못했습니다. BOX_RUSH_FONT 환경 변수에 한글 TTF/OTF 경로를 지정하세요.')


class Renderer:
    def __init__(self, test_mode=False):
        self.images = {name: p.load_image(str(ROOT / 'resources' / f'{name}.png'))
                       for name in ('road', 'truck', 'box', 'barrier', 'tree', 'cone', 'panel', 'ui_background')}
        font_path = find_font()
        self.fonts = {size: p.load_font(font_path, size) for size in (12, 14, 16, 18, 22, 28, 36, 56)}
        self.test_mode = test_mode


    def text(self, value, x, y, size=18, color=WHITE, center=False):
        font = self.fonts[size]
        if center:
            width, height = ctypes.c_int(), ctypes.c_int()
            TTF_SizeUTF8(font.font, str(value).encode('utf-8'), ctypes.byref(width), ctypes.byref(height))
            x -= width.value / 2
        font.draw(x, y, str(value), color)


    @staticmethod
    def rect(x, y, w, h, color):
        p.draw_rectangle(x, y, x + w, y + h, *color, filled=True)


    def image(self, name, x, y, w=None, h=None):
        self.images[name].draw(x, y, w, h)


    def truck(self, x, y, boxes, scale=1.0, visible=True):
        if not visible:
            return
        self.image('truck', x, y, PLAYER_SIZE[0] * scale, PLAYER_SIZE[1] * scale)
        # 2열 3행으로 배치해 0~5개의 적재량을 실제 스프라이트로 표현한다.
        positions = [(-10, 4), (10, 4), (-10, -15), (10, -15), (0, -34)]
        for dx, dy in positions[:boxes]:
            self.image('box', x + dx * scale, y + dy * scale, 18 * scale, 18 * scale)


    def scenery(self, scroll=0):
        offset = scroll % 600
        self.image('road', 400, 300 - offset, 800, 600)
        self.image('road', 400, 900 - offset, 800, 600)
        for index in range(4):
            y = (index * 210 - scroll * 0.8) % 840 - 100
            self.image('tree', 62, y, 100, 106)
            self.image('tree', 738, y + 90, 100, 106)
            self.image('cone', 124, y + 90, 24, 30)
            self.image('cone', 683, y + 12, 24, 30)


    def footer(self, text='ESC  종료'):
        self.text(text, 400, 28, 14, MUTED, center=True)
        if self.test_mode:
            self.text('테스트 모드 · 구간 3초', 400, 575, 14, ORANGE, center=True)


    def button(self, text, y=126):
        self.rect(230, y - 25, 340, 50, (234, 124, 43))
        self.text(text, 400, y, 18, NAVY, center=True)


