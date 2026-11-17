"""pico2d에 의존하지 않는 게임 규칙. 테스트에서도 같은 코드를 사용한다."""
from dataclasses import dataclass
import math
import random

from config import (
    COOLDOWNS, INITIAL_HEALTH, INVULNERABLE_SECONDS, LANES,
    LANE_CHANGE_SECONDS, OBSTACLE_HITBOXES, OBSTACLE_SIZES,
    PLAYER_HITBOX, PLAYER_Y, POINTS_PER_BOX, STAGES, STAGE_SECONDS,
    TARGET_SCORE, HEIGHT,
)


