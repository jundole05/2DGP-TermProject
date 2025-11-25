import random
from pico2d import *
import game_world
import game_framework
from behavior_tree import BehaviorTree, Selector, Sequence, Condition, Action
import common

from state_machine import StateMachine

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION

IDLE_FRAMES = 6
RUN_FRAMES = 8
ATTACK_FRAMES = 10
FRAME_W = 64
FRAME_H = 64
DEATH_FRAMES = 10

# durations
IDLE_DURATION = 3.0
RUN_DURATION = 2.0
ATTACK_DURATION = 0.5

PIXEL_PER_METER = (10.0 / 0.3)
RUN_SPEED_KMPH = 5.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

def run_event(e): return e[0] == 'RUN'
def idle_event(e): return e[0] == 'IDLE'
def death_event(e): return e[0] == 'DEATH'
def attack_event(e): return e[0] == 'ATTACK'

class Attack:
    def __init__(self, slime):
        self.slime = slime

    def enter(self, e):
        self.slime.frame = 0
        self.slime.dir_x = 0
        self.slime.dir_y = 0
        self.animation_finished = False

    def exit(self, e):
        pass

    def do(self):
        if not self.animation_finished:
            attack_action_per_time = 0.5 / ATTACK_DURATION
            self.slime.frame += ATTACK_FRAMES * attack_action_per_time * game_framework.frame_time
            if self.slime.frame >= ATTACK_FRAMES:
                self.slime.frame = ATTACK_FRAMES - 1
                self.animation_finished = True

    def draw(self):
        img = self.slime.attack_image
        # 공격 시 1.5배 크게 그리기
        attack_w = self.slime.draw_w * 2.0
        attack_h = self.slime.draw_h * 2.0
        img.clip_draw(int(self.slime.frame) * FRAME_W,
                      self.slime.face_dir * FRAME_H,
                      FRAME_W, FRAME_H,
                      self.slime.x, self.slime.y,
                      attack_w, attack_h)


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

class Death:
    def __init__(self, slime):
        self.slime = slime

    def enter(self, e):
        self.slime.frame = 0
        self.slime.dir_x = 0
        self.slime.dir_y = 0
        self.animation_finished = False

    def exit(self, e):
        pass

    def do(self):
        if not self.animation_finished:
            self.slime.frame += DEATH_FRAMES * ACTION_PER_TIME * game_framework.frame_time
            if self.slime.frame >= DEATH_FRAMES:
                self.slime.frame = DEATH_FRAMES - 1  # 마지막 프레임에 고정
                self.animation_finished = True

    def draw(self):
        img = self.slime.death_image
        img.clip_draw(int(self.slime.frame) * FRAME_W,
                      self.slime.face_dir * FRAME_H,
                      FRAME_W, FRAME_H,
                      self.slime.x, self.slime.y,
                      self.slime.draw_w, self.slime.draw_h)

class Slime:
    SLIME_IMAGES = [
        ('./Resource/slime/Slime1/idle.png', './Resource/slime/Slime1/run.png', './Resource/slime/Slime1/death.png',
         './Resource/slime/Slime1/attack.png'),
        ('./Resource/slime/Slime2/idle.png', './Resource/slime/Slime2/run.png', './Resource/slime/Slime2/death.png',
         './Resource/slime/Slime2/attack.png'),
        ('./Resource/slime/Slime3/idle.png', './Resource/slime/Slime3/run.png', './Resource/slime/Slime3/death.png',
         './Resource/slime/Slime3/attack.png'),
    ]

    def __init__(self, slime_type=0, x=100, y=100, draw_w=100, draw_h=100, speed=RUN_SPEED_PPS):
        idle_path, run_path, death_path, attack_path = Slime.SLIME_IMAGES[slime_type]
        self.idle_image = load_image(idle_path)
        self.run_image = load_image(run_path)
        self.death_image = load_image(death_path)
        self.attack_image = load_image(attack_path)

        self.x, self.y = x, y
        self.prev_x, self.prev_y = x, y
        self.draw_w, self.draw_h = draw_w, draw_h
        self.speed = speed

        self.frame = 0
        # 초기 face_dir은 랜덤, idle 상태 시작 시 이 값이 사용됨
        self.face_dir = random.randint(0, 3)  # 0:right,1:left,2:up,3:down
        self.dir_x = 0
        self.dir_y = 0
        self.tx, self.ty = x, y

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.DEATH = Death(self)
        self.ATTACK = Attack(self)
        self.state_machine = StateMachine(
            self.IDLE,
            {
                self.IDLE: {run_event: self.RUN, death_event: self.DEATH, attack_event: self.ATTACK},
                self.RUN: {idle_event: self.IDLE, death_event: self.DEATH, attack_event: self.ATTACK},
                self.ATTACK: {run_event: self.RUN, idle_event: self.IDLE, death_event: self.DEATH},
                self.DEATH: {death_event: self.IDLE}
            }
        )

        # 상태 지속 시간 타이머: 처음은 Idle로 시작하므로 IDLE_DURATION
        self.state_timer = IDLE_DURATION
        self.build_behavior_tree()

    def build_behavior_tree(self):
        c1 = Condition('캐릭터가 10 이내에 있는가?', self.is_character_nearby, 10)
        c2 = Condition('캐릭터가 3 이내에 있는가?', self.is_character_nearby, 3)
        a1 = Action('캐릭터 공격', self.attack_character)
        a2 = Action('캐릭터 추적', self.move_to_character)

        attack_or_chase = Sequence('공격 또는 추적', c1,
                                   Selector('공격 우선',
                                            Sequence('공격', c2, a1),
                                            a2))

        a3 = Action('랜덤 위치 설정', self.set_random_location)
        a4 = Action('목표 위치로 이동', self.move_to_target)
        wander = Sequence('배회', a3, a4)

        root = Selector('추적/공격 또는 배회', attack_or_chase, wander)
        self.bt = BehaviorTree(root)

    def distance_less_than(self, x1, y1, x2, y2, r):
        distance2 = (x1 - x2) ** 2 + (y1 - y2) ** 2
        return distance2 < (r * PIXEL_PER_METER) ** 2

    def is_character_nearby(self, distance):
        if not common.character:
            return BehaviorTree.FAIL
        if self.distance_less_than(common.character.x, common.character.y, self.x, self.y, distance):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def set_random_location(self):
        self.tx = random.randint(100, 1500)
        self.ty = random.randint(100, 900)
        return BehaviorTree.SUCCESS

    def move_little_to(self, tx, ty):
        dx = tx - self.x
        dy = ty - self.y
        distance = math.sqrt(dx**2 + dy**2)

        if distance > 0:
            self.dir_x = dx / distance
            self.dir_y = dy / distance

            if abs(dx) > abs(dy):
                self.face_dir = 0 if dx > 0 else 1
            else:
                self.face_dir = 2 if dy > 0 else 3

            move_distance = self.speed * game_framework.frame_time
            self.x += self.dir_x * move_distance
            self.y += self.dir_y * move_distance

    def move_to_target(self, r=0.5):
        self.state_machine.handle_state_event(('RUN', None))
        self.move_little_to(self.tx, self.ty)

        if self.distance_less_than(self.tx, self.ty, self.x, self.y, r):
            self.state_machine.handle_state_event(('IDLE', None))
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.RUNNING

    def move_to_character(self, r=3.0):
        if not common.character:
            return BehaviorTree.FAIL

        # 3 이내면 공격으로 전환
        if self.distance_less_than(common.character.x, common.character.y, self.x, self.y, 3):
            return BehaviorTree.SUCCESS

        self.state_machine.handle_state_event(('RUN', None))
        self.move_little_to(common.character.x, common.character.y)

        return BehaviorTree.RUNNING

    def attack_character(self):
        if not common.character:
            return BehaviorTree.FAIL

        # Attack 상태로 전환
        if self.state_machine.cur_state != self.ATTACK:
            self.state_machine.handle_state_event(('ATTACK', None))
            return BehaviorTree.RUNNING

        # 공격 애니메이션이 진행 중이면 무조건 RUNNING 반환 (애니메이션 완료까지 대기)
        if not self.state_machine.cur_state.animation_finished:
            return BehaviorTree.RUNNING

        # 공격 애니메이션 완료 후 거리 확인
        if self.distance_less_than(common.character.x, common.character.y, self.x, self.y, 3):
            # 3 이내면 공격 반복 (새로운 공격 시작)
            self.state_machine.cur_state.enter(None)  # 애니메이션 초기화
            return BehaviorTree.RUNNING
        else:
            # 3 이상이면 공격 종료 (추적 또는 배회로 전환)
            return BehaviorTree.SUCCESS

    def update(self):
        self.prev_x, self.prev_y = self.x, self.y

        # Death나 Attack 상태일 때는 BT 실행 조정
        if self.state_machine.cur_state == self.DEATH:
            self.state_machine.update()
            return

        # Behavior Tree 실행
        self.bt.run()
        self.state_machine.update()

        # 화면 경계 체크
        self.x = max(50, min(self.x, 1600 - 50))
        self.y = max(50, min(self.y, 900 - 50))

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        half_w = self.draw_w / 2 - 30
        half_h = self.draw_h / 2 - 30
        return (self.x - half_w, self.y - half_h, self.x + half_w, self.y + half_h)

    def handle_collision(self, group, other):
        if group == 'character:slime':
            self.x = self.prev_x
            self.y = self.prev_y
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