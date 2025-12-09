from pico2d import load_image, draw_line, draw_rectangle
import random
import math
import game_world
import game_framework
import common

PIXEL_PER_METER = 10.0 / 0.3
WALK_SPEED_KMPH = 10.0
WALK_SPEED_MPM = WALK_SPEED_KMPH * 1000.0 / 60.0
WALK_SPEED_MPS = WALK_SPEED_MPM / 60.0
WALK_SPEED_PPS = WALK_SPEED_MPS * PIXEL_PER_METER

FRAME_W = 64
FRAME_H = 64
WALK_FRAMES = 8
ATTACK_FRAMES = 8

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION

CHASE_DURATION = 2.0

class Death:
    def __init__(self, boss):
        self.boss = boss
        self.image = load_image('./Resource/boss/death.png')

    def enter(self, e):
        self.boss.frame = 0
        self.boss.dir_x = 0
        self.boss.dir_y = 0
        self.animation_finished = False

    def exit(self, e):
        pass

    def do(self):
        if not self.animation_finished:
            death_frames = 12  # death 이미지의 프레임 수
            death_duration = 3.0  # 3초 동안 애니메이션 재생
            frames_per_second = death_frames / death_duration

            self.boss.frame += frames_per_second * game_framework.frame_time
            if self.boss.frame >= death_frames:
                self.boss.frame = death_frames - 1
                self.animation_finished = True

    def draw(self):
        self.image.clip_draw(int(self.boss.frame) * 64, 0, 64, 64,
                           self.boss.x, self.boss.y, 200, 200)

class Ball:
    def __init__(self, x, y, dir_x, dir_y):
        self.x = x
        self.y = y
        self.image = load_image('./Resource/boss/ball.png')
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.speed = 300
        self.size = 20

    def update(self):
        self.x += self.dir_x * self.speed * game_framework.frame_time
        self.y += self.dir_y * self.speed * game_framework.frame_time

        if self.x < 0 or self.x > 1600 or self.y < 0 or self.y > 1000:
            game_world.remove_object(self)

    def draw(self):
        # 이미지 크기에 맞게 조정 (예: 40x40)
        self.image.draw(self.x, self.y, self.size * 2, self.size * 2)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return (self.x - self.size//2, self.y - self.size//2,
                self.x + self.size//2, self.y + self.size//2)

    def handle_collision(self, group, other):
        if group == 'boss_ball:character':
            game_world.remove_object(self)

class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.prev_x = x  # 추가
        self.prev_y = y  # 추가
        self.walk_image = load_image('./Resource/boss/walk.png')
        self.attack_image = load_image('./Resource/boss/attack.png')
        self.is_hit = False  # 추가
        self.frame = 0
        self.face_dir = 0
        self.state = 'CHASE'
        self.chase_timer = 0
        self.DEATH = Death(self)
        self.max_hp = 15
        self.current_hp = 15

    def update(self):
        self.prev_x, self.prev_y = self.x, self.y

        if not common.character:
            return

        # HP가 0 이하일 때 Death 상태로 전환
        if self.current_hp <= 0 and self.state != 'DEATH':
            self.state = 'DEATH'
            self.DEATH.enter(None)
            return

        # Death 상태일 때는 애니메이션만 실행
        if self.state == 'DEATH':
            self.DEATH.do()
            return

        if self.state == 'CHASE':
            self.chase_timer += game_framework.frame_time
            self.frame = (self.frame + WALK_FRAMES * ACTION_PER_TIME * game_framework.frame_time) % WALK_FRAMES

            dx = common.character.x - self.x
            dy = common.character.y - self.y
            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance > 0:
                dir_x = dx / distance
                dir_y = dy / distance

                if abs(dx) > abs(dy):
                    self.face_dir = 0 if dx > 0 else 1
                else:
                    self.face_dir = 2 if dy > 0 else 3

                self.x += dir_x * WALK_SPEED_PPS * game_framework.frame_time
                self.y += dir_y * WALK_SPEED_PPS * game_framework.frame_time

            if self.chase_timer >= CHASE_DURATION:
                self.state = 'ATTACK'
                self.frame = 0
                self.chase_timer = 0

        elif self.state == 'ATTACK':
            self.frame += ATTACK_FRAMES * ACTION_PER_TIME * game_framework.frame_time

            if int(self.frame) == 4 and not hasattr(self, 'balls_fired'):
                self.fire_balls()
                self.balls_fired = True

            if self.frame >= ATTACK_FRAMES:
                self.state = 'CHASE'
                self.frame = 0
                if hasattr(self, 'balls_fired'):
                    delattr(self, 'balls_fired')

        elif self.state == 'ATTACK':
            self.frame += ATTACK_FRAMES * ACTION_PER_TIME * game_framework.frame_time

            if int(self.frame) == 4 and not hasattr(self, 'balls_fired'):
                self.fire_balls()
                self.balls_fired = True

            if self.frame >= ATTACK_FRAMES:
                self.state = 'CHASE'
                self.frame = 0
                if hasattr(self, 'balls_fired'):
                    delattr(self, 'balls_fired')

    def fire_balls(self):
        directions = [
            (1, 0), (-1, 0), (0, 1), (0, -1),
            (0.707, 0.707), (-0.707, 0.707),
            (0.707, -0.707), (-0.707, -0.707)
        ]

        for dir_x, dir_y in directions:
            ball = Ball(self.x, self.y, dir_x, dir_y)
            game_world.add_object(ball, 1)
            game_world.add_collision_pair('boss_ball:character', ball, None)

    def draw(self):
        if self.state == 'DEATH':
            self.DEATH.draw()
            return

        if self.state == 'CHASE':
            self.walk_image.clip_draw(int(self.frame) * FRAME_W, self.face_dir * FRAME_H,
                                      FRAME_W, FRAME_H, self.x, self.y, 200, 200)
        elif self.state == 'ATTACK':
            self.attack_image.clip_draw(int(self.frame) * FRAME_W, self.face_dir * FRAME_H,
                                        FRAME_W, FRAME_H, self.x, self.y, 200, 200)

        draw_rectangle(*self.get_bb())
        self.draw_hp_bar()

    def draw_hp_bar(self):
        bar_x = self.x
        bar_y = self.y + 120
        bar_width = 100
        bar_height = 10

        for i in range(int(bar_height)):
            draw_line(bar_x - bar_width // 2, bar_y - bar_height // 2 + i,
                     bar_x + bar_width // 2, bar_y - bar_height // 2 + i)

        hp_ratio = self.current_hp / self.max_hp
        current_bar_width = bar_width * hp_ratio

        if self.current_hp > 0:
            for i in range(int(bar_height)):
                draw_line(bar_x - bar_width // 2, bar_y - bar_height // 2 + i,
                         bar_x - bar_width // 2 + current_bar_width, bar_y - bar_height // 2 + i, 255, 0, 0)

    def get_bb(self):
        return self.x - 50, self.y - 50, self.x + 50, self.y + 50

    def handle_collision(self, group, other):
        if group == 'character:boss':
            # 캐릭터와 겹치지 않도록 이전 위치로 복원
            self.x = self.prev_x
            self.y = self.prev_y
        elif group == 'attack:boss':
            if not self.is_hit:
                attack_bb = other.get_attack_bb()
                if attack_bb:
                    self.current_hp -= 1
                    self.is_hit = True
                    if self.current_hp <= 0:
                        self.current_hp = 0
        pass