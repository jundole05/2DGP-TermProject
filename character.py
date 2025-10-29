from pico2d import *
from sdl2 import *

import game_world
import game_framework

from state_machine import StateMachine

def space_down(e): # e is space down ?
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_SPACE

def time_out(e):
    return e[0] == 'TIME_OUT'

def up_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_UP

def up_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_UP

def down_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_DOWN

def down_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key == SDLK_DOWN

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

IDLE_FRAMES = [4, 12, 12, 12]
RUN_FRAMES = 8
ATTACK_FRAMES = 8

class Idle:
    def __init__(self, character):
        self.character = character
        self.image = load_image('./Resource/character/Lv1/idle.png')

    def enter(self, e):
        self.character.dir_x = 0
        self.character.dir_y = 0

    def exit(self, e):
        pass

    def do(self):
        max_frames = IDLE_FRAMES[self.character.face_dir]
        self.character.frame = (self.character.frame + max_frames * ACTION_PER_TIME * game_framework.frame_time) % max_frames


    def draw(self):
        self.image.clip_draw(int(self.character.frame) * 64, self.character.face_dir * 64, 64, 64, self.character.x, self.character.y, 150, 150)

class Run:
    def __init__(self, character):
        self.character = character
        self.image = load_image('./Resource/character/Lv1/run.png')

    def enter(self, e):
        if up_down(e) or up_up(e):
            self.character.dir_y = 1
            self.character.face_dir = 0
        elif down_down(e) or down_up(e):
            self.character.dir_y = -1
            self.character.face_dir = 3
        elif right_down(e) or right_up(e):
            self.character.dir_x = 1
            self.character.face_dir = 1
        elif left_down(e) or left_up(e):
            self.character.dir_x = -1
            self.character.face_dir = 2

    def exit(self, e):
        pass

    def do(self):
        self.character.frame = (self.character.frame + RUN_FRAMES * ACTION_PER_TIME * game_framework.frame_time) % RUN_FRAMES
        self.character.x += self.character.dir_x * RUN_SPEED_PPS * game_framework.frame_time
        self.character.y += self.character.dir_y * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        self.image.clip_draw(int(self.character.frame) * 64, self.character.face_dir * 64, 64, 64, self.character.x, self.character.y, 150, 150)

class Attack:
    def __init__(self, character):
        self.character = character
        self.image = load_image('./Resource/character/Lv1/attack.png')
        self.timer = 0

    def enter(self, e):
        self.character.frame = 0
        self. timer = 0
        self.prev_state = type(self.character.state_machine.cur_state)



class Character:
    def __init__(self):
        self.x, self.y = 500, 500
        self.frame = 0
        self.face_dir = 2
        self.dir_x = 0
        self.dir_y = 0

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {up_down: self.RUN, down_down: self.RUN, right_down: self.RUN, left_down: self.RUN},
                self.RUN: {up_up: self.IDLE, down_up: self.IDLE, right_up: self.IDLE, left_up: self.IDLE}
            }
        )

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
