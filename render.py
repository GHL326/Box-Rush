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


    def draw(self, game):
        p.clear_canvas()
        if game.state == 'play':
            self.play(game)
        else:
            self.image('ui_background', 400, 300, 800, 600)
            getattr(self, game.state)(game)
        p.update_canvas()


    def title(self, game):
        # 오른쪽 도로 미리보기는 배경 위에 실제 오브젝트를 조합한다.
        self.image('road', 651, 300, 330, 600)
        self.image('tree', 501, 430, 92, 98)
        self.image('tree', 790, 170, 92, 98)
        self.image('barrier', 651, 430, 74, 74)
        self.image('box', 714, 300, 38, 38)
        self.truck(640, 179, 5, 1.6)
        self.text('SPECIAL DELIVERY / 01', 45, 526, 14, ORANGE)
        self.text('BOX', 42, 452, 56)
        self.text('RUSH', 42, 391, 56, ORANGE)
        self.text('박스 러시', 47, 326, 28)
        self.text('많이 싣고, 끝까지 지켜라.', 48, 270, 22)
        self.text('3개 구간  ·  90초  ·  목표 200점', 48, 231, 16, MUTED)
        self.rect(47, 129, 330, 51, (234, 124, 43))
        self.text('ENTER   배송 시작', 212, 154, 18, NAVY, center=True)
        self.text('↑ ↓  적재량 선택     ← →  차선 이동', 48, 92, 14, MUTED)
        self.text('ESC  종료', 48, 59, 14, MUTED)
        if self.test_mode:
            self.text('테스트 모드 · 구간 3초', 48, 559, 14, ORANGE)


    def select(self, game):
        self.image('panel', 400, 310, 650, 470)
        self.text(f'DELIVERY 0{game.stage} / 03', 400, 508, 14, ORANGE, True)
        self.text('이번 구간, 얼마나 실을까요?', 400, 464, 28, center=True)
        self.text(f'누적 {game.score}점   ·   내구도 {game.player.health}/{INITIAL_HEALTH}', 400, 423, 16, MUTED, True)
        self.truck(238, 302, game.selected, 1.6)
        self.text(f'{game.selected}개', 482, 354, 56, ORANGE, True)
        self.text('↑  늘리기      ↓  줄이기', 482, 299, 16, MUTED, True)
        self.text(f'최대 점수     {game.selected * POINTS_PER_BOX}점', 381, 250, 18)
        self.text(f'변경 쿨타임   {COOLDOWNS[game.selected]:g}초', 381, 216, 18)
        self.text('상자가 많을수록 차선을 다시 바꾸기까지 오래 걸립니다.', 400, 173, 14, MUTED, True)
        self.button('ENTER   적재 완료 · 출발', 117)
        self.footer()


    def play(self, game):
        self.scenery(game.scroll)
        for obstacle in game.obstacles:
            self.image(obstacle.kind, obstacle.x, obstacle.y, *OBSTACLE_SIZES[obstacle.kind])
        player = game.player
        visible = player.invulnerable <= 0 or int(player.invulnerable * 12) % 2 == 0
        self.truck(player.x, PLAYER_Y, player.boxes, visible=visible)
        # HUD는 도로의 위/아래에만 위치한다.
        self.rect(0, 526, 800, 74, NAVY)
        self.rect(0, 524, 800, 2, (226, 131, 58))
        self.text(f'구간 0{game.stage} / 03', 28, 566, 22)
        self.text(f'{math.ceil(game.remaining):02d}초', 400, 566, 28, ORANGE, True)
        self.text(f'{game.score:03d} / {TARGET_SCORE}점', 603, 566, 22)
        self.rect(25, 535, 750, 4, (49, 67, 85))
        self.rect(25, 535, 750 * game.remaining / game.stage_seconds, 4, (239, 150, 67))
        self.rect(0, 0, 800, 76, NAVY)
        self.text('내구도', 24, 49, 14, MUTED)
        for i in range(INITIAL_HEALTH):
            self.rect(83 + i * 23, 42, 16, 14, GREEN if i < player.health else (54, 65, 81))
        self.image('box', 221, 48, 23, 23)
        self.text(f'{player.boxes}개', 242, 48, 22)
        self.text(f'배송 예상 +{player.boxes * POINTS_PER_BOX}점', 207, 19, 12, MUTED)
        if player.move_left > 0:
            label, color = '차선 이동 중', ORANGE
        elif not player.ready:
            label, color = f'대기  {player.cooldown:.2f}초', ORANGE
        else:
            label, color = '차선 변경 가능', GREEN
        self.text(label, 390, 48, 18, color)
        fraction = 1.0 if player.ready else (0.0 if player.move_left else 1 - player.cooldown / player.cooldown_period)
        self.rect(390, 20, 180, 5, (49, 67, 85))
        self.rect(390, 20, max(0, min(1, fraction)) * 180, 5, color)
        self.text('← →  차선 이동', 643, 48, 14, MUTED)
        self.text('ESC  종료', 643, 21, 12, MUTED)
        if self.test_mode:
            self.text('테스트 · 3초', 28, 506, 12, ORANGE)


    def stage_end(self, game):
        self.image('panel', 400, 311, 650, 470)
        self.text(f'DELIVERY 0{game.stage} COMPLETE', 400, 505, 14, ORANGE, True)
        self.text(f'{game.stage}구간 배송 완료', 400, 460, 36, center=True)
        for i in range(game.last_boxes):
            self.image('box', 400 + (i - (game.last_boxes - 1) / 2) * 51, 385, 42, 42)
        self.text(f'남은 상자 {game.last_boxes}개 × 20점', 400, 331, 18, MUTED, True)
        self.text(f'+{game.last_points}점', 400, 275, 56, ORANGE, True)
        self.text(f'현재 누적 점수  {game.score} / {TARGET_SCORE}점', 400, 214, 22, center=True)
        label = 'ENTER   최종 결과 보기' if game.stage == 3 else 'ENTER   다음 구간 준비'
        self.button(label, 124)
        self.footer()


    def result(self, game):
        self.image('panel', 400, 311, 650, 470)
        color = GREEN if game.success else ORANGE
        self.text('DELIVERY REPORT', 400, 504, 14, color, True)
        self.text('배송 성공!' if game.success else '배송 실패', 400, 453, 36, color, True)
        self.text(f'{game.score}점', 400, 381, 56, center=True)
        self.text(game.reason, 400, 324, 16, MUTED, True)
        self.text('구간                 배송 상자                 획득 점수', 400, 276, 14, MUTED, True)
        for row, (stage, boxes, points) in enumerate(game.history):
            self.text(f'{stage}구간', 215, 244 - row * 29, 16)
            self.text(f'{boxes}개', 394, 244 - row * 29, 16)
            self.text(f'{points}점', 544, 244 - row * 29, 16)
        if not game.history:
            self.text('완료한 구간이 없습니다.', 400, 229, 16, MUTED, True)
        self.button('R   처음부터 다시 시작', 119)
        self.footer()


