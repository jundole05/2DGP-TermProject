import random
from pico2d import *
import game_world
import game_framework

from state_machine import StateMachine

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION

IDLE_FRAMES = 6
RUN_FRAMES = 8
FRAME_W = 64
FRAME_H = 64

# durations
IDLE_DURATION = 3.0
RUN_DURATION = 2.0

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 20.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

def run_event(e): return e[0] == 'RUN'
def idle_event(e): return e[0] == 'IDLE'

class Idle:
    def __init__(self, slime):
        self.slime = slime

    def enter(self, e):
        # idle시에는 이동 벡터 0, face_dir는 유지(마지막 run 방향)
        self.slime.dir_x = 0
        self.slime.dir_y = 0

    def exit(self, e):
        pass

    def do(self):
        max_frames = IDLE_FRAMES
        self.slime.frame = (self.slime.frame + max_frames * ACTION_PER_TIME * game_framework.frame_time) % max_frames

    def draw(self):
        img = self.slime.idle_image
        img.clip_draw(int(self.slime.frame) * FRAME_W,
                      self.slime.face_dir * FRAME_H,
                      FRAME_W, FRAME_H,
                      self.slime.x, self.slime.y,
                      self.slime.draw_w, self.slime.draw_h)

class Run:
    def __init__(self, slime):
        self.slime = slime

    def enter(self, e):
        # face_dir는 Slime에서 이미 정해져 있음; 방향 벡터만 설정
        dir_map = {0: (1, 0), 1: (-1, 0), 2: (0, 1), 3: (0, -1)}
        self.slime.dir_x, self.slime.dir_y = dir_map.get(self.slime.face_dir, (0, 0))

    def exit(self, e):
        # 멈출 때 이동 벡터 초기화는 Idle.enter에서 처리
        pass

    def do(self):
        max_frames = RUN_FRAMES
        self.slime.frame = (self.slime.frame + max_frames * ACTION_PER_TIME * game_framework.frame_time) % max_frames
        self.slime.x += self.slime.dir_x * self.slime.speed * game_framework.frame_time
        self.slime.y += self.slime.dir_y * self.slime.speed * game_framework.frame_time
        # 화면 밖으로 나가지 않게 클램프 (캔버스 크기 고정 1600x1000)
        self.slime.x = max(self.slime.draw_w/2, min(1600 - self.slime.draw_w/2, self.slime.x))
        self.slime.y = max(self.slime.draw_h/2, min(1000 - self.slime.draw_h/2, self.slime.y))

    def draw(self):
        img = self.slime.run_image
        img.clip_draw(int(self.slime.frame) * FRAME_W,
                      self.slime.face_dir * FRAME_H,
                      FRAME_W, FRAME_H,
                      self.slime.x, self.slime.y,
                      self.slime.draw_w, self.slime.draw_h)

class Slime:
    SLIME_IMAGES = [
        ('./Resource/slime/Slime1/idle.png', './Resource/slime/Slime1/run.png'),
        ('./Resource/slime/Slime2/idle.png', './Resource/slime/Slime2/run.png'),
        ('./Resource/slime/Slime3/idle.png', './Resource/slime/Slime3/run.png'),
    ]

    def __init__(self, slime_type=0, x=100, y=100, draw_w=100, draw_h=100, speed=RUN_SPEED_PPS):
        idle_path, run_path = Slime.SLIME_IMAGES[slime_type]
        self.idle_image = load_image(idle_path)
        self.run_image = load_image(run_path)

        self.x, self.y = x, y
        self.draw_w, self.draw_h = draw_w, draw_h
        self.speed = speed

        self.frame = 0
        # 초기 face_dir은 랜덤, idle 상태 시작 시 이 값이 사용됨
        self.face_dir = random.randint(0, 3)  # 0:right,1:left,2:up,3:down
        self.dir_x = 0
        self.dir_y = 0

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {run_event: self.RUN},
                self.RUN: {idle_event: self.IDLE}
            }
        )

        # 상태 지속 시간 타이머: 처음은 Idle로 시작하므로 IDLE_DURATION
        self.state_timer = IDLE_DURATION

    def update(self):
        # 상태 내부 동작(프레임/이동)
        self.state_machine.update()

        # 상태 타이머 감소 및 전환 처리
        self.state_timer -= game_framework.frame_time
        if self.state_timer <= 0:
            # 현재 상태 판별
            cur = self.state_machine.cur_state
            if cur == self.IDLE:
                # Run으로 전환: 새 방향 선택(이때 face_dir 갱신)
                self.face_dir = random.randint(0, 3)
                self.state_machine.handle_state_event(('RUN', None))
                self.state_timer = RUN_DURATION
            elif cur == self.RUN:
                # Idle으로 전환: face_dir는 유지(마지막 run 방향)
                self.state_machine.handle_state_event(('IDLE', None))
                self.state_timer = IDLE_DURATION

    def draw(self):
        self.state_machine.draw()

    def get_bb(self):
        half_w = self.draw_w / 2
        half_h = self.draw_h / 2
        return (self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h)

    def handle_collision(self, group, other):
        pass

def spawn_slimes(count = 5, depth = 1):
    slimes = []
    for _ in range(count):
        stype = random.randint(0, 2)
        x = random.randint(50, 1550)
        y = random.randint(50, 950)
        s = Slime(slime_type = stype, x = x, y = y, draw_w = 100, draw_h = 100)
        slimes.append(s)
        game_world.add_object(s, depth)
    return slimes