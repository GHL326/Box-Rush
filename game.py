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


    def start_stage(self):
        self.player = Player(boxes=self.selected, health=self.player.health)
        self.elapsed = 0.0
        self.spawn_elapsed = 0.0
        self.scroll = 0.0
        self.obstacles.clear()
        self.state = "play"


    def spawn_obstacle(self):
        kind = self.rng.choice(tuple(OBSTACLE_SIZES))
        y = HEIGHT + OBSTACLE_SIZES[kind][1] / 2
        # 같은 차선의 생성 영역이 비어 있는 경우에만 한 개 생성한다.
        lanes = [lane for lane in range(3) if all(
            o.lane != lane or abs(o.y - y) > (OBSTACLE_SIZES[o.kind][1] + OBSTACLE_SIZES[kind][1]) / 2 + 24
            for o in self.obstacles)]
        if lanes:
            self.obstacles.append(Obstacle(self.rng.choice(lanes), kind, y))


    def update(self, dt):
        if self.state != "play" or not math.isfinite(dt) or dt <= 0:
            return
        # 긴 프레임에서도 충돌을 건너뛰지 않도록 시간을 작은 단위로 나눈다.
        # dt를 버리지 않으므로 정상 플레이는 실제 경과 시간으로 30초이다.
        remaining_dt = min(dt, self.remaining)
        while remaining_dt > 1e-10 and self.state == "play":
            step = min(remaining_dt, 1 / 120)
            self._step(step)
            remaining_dt -= step


    def _step(self, dt):
        speed, interval = STAGES[self.stage - 1]
        self.player.update(dt)
        self.elapsed = min(self.stage_seconds, self.elapsed + dt)
        self.scroll = (self.scroll + speed * dt) % HEIGHT
        self.spawn_elapsed += dt
        for obstacle in self.obstacles:
            obstacle.y -= speed * dt
        if self.spawn_elapsed + 1e-9 >= interval:
            self.spawn_elapsed -= interval
            self.spawn_obstacle()
        survivors = []
        for obstacle in self.obstacles:
            if obstacle.collides(self.player):
                self.player.hit()
                # 접촉한 장애물은 제거해 무적 종료 후 중복 피격을 막는다.
            elif obstacle.y + OBSTACLE_SIZES[obstacle.kind][1] / 2 >= 0:
                survivors.append(obstacle)
        self.obstacles = survivors
        if self.player.health == 0:
            self.success = False
            self.reason = "차량 내구도가 모두 소진되었습니다."
            self.state = "result"
        elif self.remaining <= 1e-8:
            self.finish_stage()


