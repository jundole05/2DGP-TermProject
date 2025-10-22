from pico2d import *
from sdl2 import *

import game_world
import game_framework

from state_machine import StateMachine

def space_down(e): # e is space down ?
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

time_out = lambda e: e[0] == 'TIMEOUT'

def right_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_RIGHT

def right_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_RIGHT

def left_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_LEFT

def left_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_LEFT


PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 20.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = 8

class Idle:
    def __init__(self, character):
        self.character = character
        self.image = load_image('./Resource/character/Lv1/idle.png')

    def enter(self, e):
        self.character.dir = 0

    def exit(self, e):
        pass

    def do(self):
        self.character.frame = (self.character.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8

    def draw(self):
        if self.character.face_dir == 1:
            self.image.clip_draw(int(self.character.frame) * 100, 0, 100, 100, self.character.x, self.character.y)
        else:
            self.image.clip_draw(int(self.character.frame) * 100, 100, 100, 100, self.character.x, self.character.y)

class Run:
    def __init__(self, character):
        self.character = character
        self.image = load_image('./Resource/character/Lv1/run.png')

    def enter(self, e):
        if right_down(e) or left_up(e):
            self.character.dir = self.character.face_dir = 1
        elif left_down(e) or right_up(e):
            self.character.dir = self.character.face_dir = -1

    def exit(self, e):
        pass

    def do(self):
        self.character.frame = (self.character.frame + FRAMES_PER_ACTION * ACTION_PER_TIME * game_framework.frame_time) % 8
        self.character.x += self.character.dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        if self.character.face_dir == 1:
            self.image.clip_draw(int(self.character.frame) * 100, 0, 100, 100, self.character.x, self.character.y)
        else:
            self.image.clip_draw(int(self.character.frame) * 100, 100, 100, 100, self.character.x, self.character.y)

class Character:
    def __init__(self):
        self.x, self.y = 50, 90
        self.frame = 0
        self.face_dir = 1
        self.dir = 0

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {right_down: self.RUN, left_down: self.RUN, right_up: self.IDLE, left_up: self.IDLE},
                self.RUN: {right_up: self.IDLE, left_up: self.IDLE, right_down: self.RUN, left_down: self.RUN}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
