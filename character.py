from time import sleep

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

def one_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key == SDLK_1

def any_key_down(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYDOWN and e[1].key in [SDLK_UP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT]

def any_key_up(e):
    return e[0] == 'INPUT' and e[1].type == SDL_KEYUP and e[1].key in [SDLK_UP, SDLK_DOWN, SDLK_LEFT, SDLK_RIGHT]

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
DEATH_FRAMES = 7

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
        self.update_key_state(e)
        self.update_direction()

    def update_key_state(self, e):
        if up_down(e):
            self.character.key_up = True
        elif up_up(e):
            self.character.key_up = False

        if down_down(e):
            self.character.key_down = True
        elif down_up(e):
            self.character.key_down = False

        if right_down(e):
            self.character.key_right = True
        elif right_up(e):
            self.character.key_right = False

        if left_down(e):
            self.character.key_left = True
        elif left_up(e):
            self.character.key_left = False

    def update_direction(self):
        self.character.dir_x = 0
        self.character.dir_y = 0

        if self.character.key_up:
            self.character.dir_y = 1
        elif self.character.key_down:
            self.character.dir_y = -1

        if self.character.key_right:
            self.character.dir_x = 1
        elif self.character.key_left:
            self.character.dir_x = -1

        if self.character.dir_y > 0:
            self.character.face_dir = 0
        elif self.character.dir_y < 0:
            self.character.face_dir = 3
        elif self.character.dir_x > 0:
            self.character.face_dir = 1
        elif self.character.dir_x < 0:
            self.character.face_dir = 2

    def exit(self, e):
        pass

    def do(self):
        self.character.frame = (self.character.frame + RUN_FRAMES * ACTION_PER_TIME * game_framework.frame_time) % RUN_FRAMES

        # 대각선 이동 시 속도 보정 (√2로 나눔)
        speed = RUN_SPEED_PPS
        if self.character.dir_x != 0 and self.character.dir_y != 0:
            speed = RUN_SPEED_PPS / 1.414  # √2 ≈ 1.414

        self.character.x += self.character.dir_x * speed * game_framework.frame_time
        self.character.y += self.character.dir_y * speed * game_framework.frame_time

    def draw(self):
        self.image.clip_draw(int(self.character.frame) * 64, self.character.face_dir * 64, 64, 64, self.character.x, self.character.y, 150, 150)

    def handle_event(self, e):
        self.update_key_state(e)
        self.update_direction()

        return not (self.character.key_up or self.character.key_down or self.character.key_left or self.character.key_right)

class Attack:
    def __init__(self, character):
        self.character = character
        self.image = load_image('./Resource/character/Lv1/attack.png')
        self.timer = 0
        self.attack_bb = None

    def enter(self, e):
        self.character.frame = 0
        self.timer = 0
        self.prev_state = type(self.character.state_machine.cur_state)
        for obj in game_world.world[1]:  # 슬라임이 있는 레이어
            if hasattr(obj, 'is_hit'):
                obj.is_hit = False

    def exit(self, e):
        self.attack_bb = None
        pass

    def get_attack_bb(self):
        char_x, char_y = self.character.x, self.character.y
        bb_extend = 10

        if self.character.face_dir == 0:  # Up
            return (char_x - 25 , char_y + 25, char_x + 25, char_y + 35 + bb_extend)
        elif self.character.face_dir == 1:  # Right
            return (char_x + 25, char_y - 40, char_x + 40 + bb_extend, char_y + 35)
        elif self.character.face_dir == 2:  # 왼쪽
            return (char_x - 40 - bb_extend , char_y - 40, char_x - 25, char_y + 35)
        elif self.character.face_dir == 3:  # 아래쪽
            return (char_x - 25, char_y - 45 - bb_extend, char_x + 25, char_y - 35)

    def do(self):
        self.character.frame += ATTACK_FRAMES * ACTION_PER_TIME * game_framework.frame_time
        self.attack_bb = self.get_attack_bb()
        if self.character.frame >= ATTACK_FRAMES:
            if self.prev_state == Idle:
                self.character.state_machine.change_state(self.character.IDLE)
            else:
                self.character.state_machine.change_state(self.character.RUN)

    def draw(self):
        self.image.clip_draw(int(self.character.frame) * 64, self.character.face_dir * 64, 64, 64, self.character.x, self.character.y, 150, 150)
        if self.attack_bb:
            draw_rectangle(*self.attack_bb)

    def handle_event(self, e):

        pass

class Death:
    def __init__(self, character):
        self.character = character
        self.image = load_image('./Resource/character/Lv1/death.png')

    def enter(self, e):
        self.character.frame = 0
        self.character.dir_x = 0
        self.character.dir_y = 0
        self.animation_finished = False

    def exit(self, e):
        pass

    def do(self):
        if not self.animation_finished:
            self.character.frame += DEATH_FRAMES * ACTION_PER_TIME * game_framework.frame_time
            if self.character.frame >= DEATH_FRAMES:
                self.character.frame = DEATH_FRAMES - 1  # 마지막 프레임에 고정
                self.animation_finished = True

    def draw(self):
        self.image.clip_draw(int(self.character.frame) * 64, self.character.face_dir * 64, 64, 64, self.character.x,
                             self.character.y, 150, 150)

class Hurt:
    def __init__(self, character):
        self.character = character
        self.image = load_image('./Resource/character/Lv1/hurt.png')

    def enter(self, e):
        self.character.frame = 0
        self.character.dir_x = 0
        self.character.dir_y = 0
        self.animation_finished = False

    def exit(self, e):
        pass

    def do(self):
        if not self.animation_finished:
            hurt_frames = 5
            # ACTION_PER_TIME 대신 더 작은 값을 사용하여 애니메이션 속도를 늦춤
            hurt_action_per_time = ACTION_PER_TIME * 0.8  # 0.3을 조정하여 속도 변경 (작을수록 느림)
            self.character.frame += hurt_frames * hurt_action_per_time * game_framework.frame_time
            if self.character.frame >= hurt_frames:
                self.character.frame = hurt_frames - 1
                self.animation_finished = True
                self.character.state_machine.change_state(self.character.IDLE)

    def draw(self):
        self.image.clip_draw(int(self.character.frame) * 64, self.character.face_dir * 64, 64, 64,
                             self.character.x, self.character.y, 150, 150)

class Character:
    def __init__(self):
        self.x, self.y = 500, 500
        self.prev_x, self.prev_y = 500, 500
        self.frame = 0
        self.face_dir = 2
        self.dir_x = 0
        self.dir_y = 0

        self.key_up = False
        self.key_down = False
        self.key_left = False
        self.key_right = False

        # 체력 시스템 추가
        self.max_hp = 10
        self.current_hp = 10

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.ATTACK = Attack(self)
        self.DEATH = Death(self)
        self.HURT = Hurt(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {any_key_down: self.RUN, space_down: self.ATTACK, one_down: self.DEATH},
                self.RUN: {any_key_up: self.IDLE, space_down: self.ATTACK, one_down: self.DEATH},
                self.ATTACK: {one_down: self.DEATH},
                self.DEATH: {one_down: self.IDLE},
                self.HURT: {}
            }
        )

    def draw_hp_bar(self):
        # 체력바 위치
        bar_x = self.x
        bar_y = self.y + 60
        bar_width = 60
        bar_height = 8

        # 체력 비율 계산
        hp_ratio = self.current_hp / self.max_hp
        current_bar_width = bar_width * hp_ratio

        for i in range(int(bar_height)):
            draw_line(bar_x - bar_width // 2, bar_y - bar_height // 2 + i,
                      bar_x + bar_width // 2, bar_y - bar_height // 2 + i)

        # 체력 바
        if self.current_hp > 0:
            for i in range(int(bar_height)):

                draw_line(bar_x - bar_width // 2, bar_y - bar_height // 2 + i,
                          bar_x - bar_width // 2 + current_bar_width, bar_y - bar_height // 2 + i, 255, 0, 0)

    def update(self):
        self.prev_x, self.prev_y = self.x, self.y
        self.state_machine.update()

    def handle_event(self, event):
        cur_state = self.state_machine.cur_state
        if isinstance(cur_state, Attack):
            cur_state.handle_event(('INPUT', event))
        elif isinstance(cur_state, Run):
            # Run 상태에서 키 처리
            should_stop = cur_state.handle_event(('INPUT', event))
            # 모든 키가 떼어졌으면 IDLE로 전환
            if should_stop:
                self.state_machine.change_state(self.IDLE)
        else:
            self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())
        self.draw_hp_bar()

    def get_bb(self):
        return self.x - 25, self.y - 40, self.x + 25, self.y + 35

    def get_attack_bb(self):
        if isinstance(self.state_machine.cur_state, Attack):
            return self.state_machine.cur_state.get_attack_bb()

    def handle_collision(self, group, other):
        if group == 'character:slime':
            self.x, self.y = self.prev_x, self.prev_y
        elif group == 'attack:slime':
            pass
        elif group == 'slime_attack:character':
            if self.state_machine.cur_state != self.HURT and self.state_machine.cur_state != self.DEATH:
                self.current_hp -= 1
                if self.current_hp <= 0:
                    self.current_hp = 0
                    self.state_machine.change_state(self.DEATH)
                else:
                    self.state_machine.change_state(self.HURT)
