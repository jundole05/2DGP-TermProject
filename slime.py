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

