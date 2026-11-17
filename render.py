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


