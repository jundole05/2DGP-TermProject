import random
from pico2d import *
import game_world
import game_framework
from character import IDLE_FRAMES

from state_machine import StateMachine

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION

IDLE_FRAMES = 6
RUN_FRAMES = 8
FRAME_W = 64
FRAME_H = 64
CHANGE_INTERVAL = 3.0

def run_event(e): return e[0] == 'RUN'
def idle_event(e): return e[0] == 'IDLE'

class Idle:
    def __init__(self, slime):
        self.slime = slime

    def enter(self, e):
        self.slime.dir_x = 0
        self.slime.dir_y = 0

    def exit(self, e):
        pass

    def do(self):
        max_frames = IDLE_FRAMES
        self.slime.frame = (self.slime.frame + max_frames * ACTION_PER_TIME * game_framework.frame_time) % max_frames

    def draw(self):
        img = self.slime.idle_image
        img.clip_draw(int(self.slime.frame) * FRAMW_W, self.slime.face_dir * FRAME_H, FRAME_W, FRAME_H, self.slime.x, self.slime.y, self.slime.draw_w, self.slime.draw_h)

class Run:
    def __init__(self, slime):
        self.slime = slime

    def enter(self, e):
        dir_map = {0: (0, 1), 1: (1, 0), 2: (-1, 0), 3: (0, -1)}
        self.slime.dir_x, self.slime.dir_y = dir_map.get(self.slime.face_dir, (0, 0))

    def exit(self, e):
        pass

    def do(self):
        max_frames = RUN_FRAMES
        self.slime.frame = (self.slime.frame + max_frames * ACTION_PER_TIME * game_framework.frame_time) % max_frames
        self.slime.x += self.slime.dir_x * self.slime.speed * game_framework.frame_time
        self.slime.y += self.slime.dir_y * self.slime.speed * game_framework.frame_time
        # 화면 밖으로 나가지 않게 클램프
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
    """
    slime_type: 0,1,2 (각각의 이미지 쌍을 사용)
    이미지 경로는 아래 SLIME_IMAGES 리스트에서 수정하십시오.
    """
    SLIME_IMAGES = [
        ('./Resource/slime/slime1_idle.png', './Resource/slime/slime1_run.png'),
        ('./Resource/slime/slime2_idle.png', './Resource/slime/slime2_run.png'),
        ('./Resource/slime/slime3_idle.png', './Resource/slime/slime3_run.png'),
    ]

    def __init__(self, slime_type=0, x=100, y=100, draw_w=100, draw_h=100, speed=RUN_SPEED_PPS := 200):
        # 이미지 로드 (파일 경로는 필요에 맞게 수정)
        idle_path, run_path = Slime.SLIME_IMAGES[slime_type]
        self.idle_image = load_image(idle_path)
        self.run_image = load_image(run_path)

        self.x, self.y = x, y
        self.draw_w, self.draw_h = draw_w, draw_h
        self.speed = speed

        self.frame = 0
        self.face_dir = random.randint(0, 3)  # 0:up,1:right,2:left,3:down
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

        self.change_timer = CHANGE_INTERVAL

    def update(self):
        # 상태별 동작(이동/프레임 업데이트)은 state에 맡김
        self.state_machine.update()

        # 주기 타이머 감소
        self.change_timer -= game_framework.frame_time
        if self.change_timer <= 0:
            self.change_timer = CHANGE_INTERVAL
            # 방향 변경
            self.face_dir = random.randint(0, 3)
            # 랜덤으로 run 또는 idle 선택
            if random.choice([True, False]):
                self.state_machine.handle_state_event(('RUN', None))
            else:
                self.state_machine.handle_state_event(('IDLE', None))

    def draw(self):
        self.state_machine.draw()

    def get_bb(self):
        half_w = self.draw_w / 2
        half_h = self.draw_h / 2
        return (self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h)

    def handle_collision(self, group, other):
        pass