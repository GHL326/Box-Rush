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


@dataclass
class Player:
    x: float = LANES[1]
    lane: int = 1
    boxes: int = 3
    health: int = INITIAL_HEALTH
    move_left: float = 0.0
    start_x: float = LANES[1]
    cooldown: float = 0.0
    cooldown_period: float = COOLDOWNS[3]
    invulnerable: float = 0.0

    @property
    def ready(self):
        return self.move_left <= 1e-9 and self.cooldown <= 1e-9


    def move(self, direction):
        target = self.lane + direction
        if direction not in (-1, 1) or not self.ready or not 0 <= target < 3:
            return False
        self.start_x = self.x
        self.lane = target
        self.move_left = LANE_CHANGE_SECONDS
        return True


    def update(self, dt):
        self.invulnerable = max(0.0, self.invulnerable - dt)
        if self.move_left > 1e-9:
            used = min(dt, self.move_left)
            self.move_left = max(0.0, self.move_left - used)
            t = 1.0 - self.move_left / LANE_CHANGE_SECONDS
            smooth = t * t * (3 - 2 * t)
            self.x = self.start_x + (LANES[self.lane] - self.start_x) * smooth
            if self.move_left <= 1e-9:
                self.move_left = 0.0
                self.x = LANES[self.lane]
                # 이동 완료 시 현재 적재량 기준으로 쿨타임을 시작한다.
                self.cooldown_period = COOLDOWNS[self.boxes]
                self.cooldown = max(0.0, self.cooldown_period - (dt - used))
        else:
            self.cooldown = max(0.0, self.cooldown - dt)


    def hit(self):
        if self.invulnerable > 1e-9:
            return False
        self.health = max(0, self.health - 1)
        self.boxes = max(0, self.boxes - 1)
        self.invulnerable = INVULNERABLE_SECONDS
        return True


@dataclass
class Obstacle:
    lane: int
    kind: str
    y: float

    @property
    def x(self):
        return LANES[self.lane]


    def collides(self, player):
        w, h = OBSTACLE_HITBOXES[self.kind]
        pw, ph = PLAYER_HITBOX
        return abs(self.x - player.x) < (w + pw) / 2 and abs(self.y - PLAYER_Y) < (h + ph) / 2


class Game:
    def __init__(self, stage_seconds=STAGE_SECONDS, seed=None):
        if not math.isfinite(stage_seconds) or stage_seconds <= 0:
            raise ValueError("구간 시간은 양수여야 합니다.")
        self.stage_seconds = stage_seconds
        self.rng = random.Random(seed)
        self.reset()


    def reset(self):
        self.state = "title"
        self.stage = 1
        self.selected = 3
        self.score = 0
        self.elapsed = 0.0
        self.spawn_elapsed = 0.0
        self.scroll = 0.0
        self.player = Player()
        self.obstacles = []
        self.history = []
        self.success = False
        self.reason = ""
        self.last_boxes = 0
        self.last_points = 0


    @property
    def remaining(self):
        return max(0.0, self.stage_seconds - self.elapsed)


    def command(self, key):
        if self.state == "title" and key == "enter":
            self.state = "select"
        elif self.state == "select":
            if key == "up":
                self.selected = min(5, self.selected + 1)
            elif key == "down":
                self.selected = max(1, self.selected - 1)
            elif key == "enter":
                self.start_stage()
        elif self.state == "play" and key in ("left", "right"):
            self.player.move(-1 if key == "left" else 1)
        elif self.state == "stage_end" and key == "enter":
            if self.stage == len(STAGES):
                self.state = "result"
            else:
                self.stage += 1
                self.state = "select"
        elif self.state == "result" and key == "r":
            self.reset()


