"""기획서 수치. 난이도 조정은 이 파일에서만 한다."""
WIDTH, HEIGHT = 800, 600
LANES = (250, 400, 550)
PLAYER_Y = 155
PLAYER_SIZE = (66, 130)
PLAYER_HITBOX = (50, 112)
STAGE_SECONDS = 30.0
INITIAL_HEALTH = 3
POINTS_PER_BOX = 20
TARGET_SCORE = 200
LANE_CHANGE_SECONDS = 0.2
INVULNERABLE_SECONDS = 1.0
# 0개는 충돌로 모든 상자를 잃은 상태. 1개와 같은 쿨타임을 사용한다.
COOLDOWNS = {0: 0.4, 1: 0.4, 2: 0.5, 3: 0.6, 4: 0.7, 5: 0.85}
STAGES = ((200.0, 1.5), (230.0, 1.4), (260.0, 1.3))
OBSTACLE_SIZES = {"box": (48, 48), "barrier": (94, 94)}
OBSTACLE_HITBOXES = {"box": (36, 40), "barrier": (82, 78)}
