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
