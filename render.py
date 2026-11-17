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


