from pico2d import *
import game_world
import common

# Boss State Machine
class StateMachine:
    def __init__(self, boss):
        self.boss = boss
        self.cur_state = Walk
        self.transitions = {
            Walk: {ATTACK: Attack, DEATH: Death},
            Attack: {WALK: Walk, DEATH: Death},
            Death: {}
        }

    def start(self):
        self.cur_state.enter(self.boss, ('WALK', 0))

    def update(self):
        self.cur_state.do(self.boss)

    def handle_event(self, e):
        for check_event, next_state in self.transitions[self.cur_state].items():
            if check_event(e):
                self.cur_state.exit(self.boss, e)
                self.cur_state = next_state
                self.cur_state.enter(self.boss, e)
                return True
        return False

    def draw(self):
        self.cur_state.draw(self.boss)


# State Events
def WALK(e):
    return e[0] == 'WALK'

def ATTACK(e):
    return e[0] == 'ATTACK'

def DEATH(e):
    return e[0] == 'DEATH'


# Boss States
class Walk:
    @staticmethod
    def enter(boss, e):
        boss.frame = 0
        boss.walk_time = 0

    @staticmethod
    def exit(boss, e):
        pass

    @staticmethod
    def do(boss):
        boss.frame = (boss.frame + 8 * 0.5 * game_framework.frame_time) % 8
        boss.walk_time += game_framework.frame_time

        # 캐릭터 방향으로 이동
        if common.character:
            dx = common.character.x - boss.x
            dy = common.character.y - boss.y
            distance = (dx**2 + dy**2) ** 0.5

            if distance > 0:
                boss.dir_x = dx / distance
                boss.dir_y = dy / distance
                boss.x += boss.dir_x * boss.speed * game_framework.frame_time
                boss.y += boss.dir_y * boss.speed * game_framework.frame_time

                # 방향 결정 (왼쪽/오른쪽)
                boss.face_dir = 1 if dx > 0 else -1

        # 2초 후 공격
        if boss.walk_time >= 2.0:
            boss.state_machine.handle_event(('ATTACK', 0))

    @staticmethod
    def draw(boss):
        if boss.face_dir == 1:
            boss.walk_image.clip_draw(int(boss.frame) * 150, 0, 150, 150, boss.x, boss.y, 200, 200)
        else:
            boss.walk_image.clip_composite_draw(int(boss.frame) * 150, 0, 150, 150, 0, 'h', boss.x, boss.y, 200, 200)


class Attack:
    @staticmethod
    def enter(boss, e):
        boss.frame = 0
        boss.attack_finished = False

    @staticmethod
    def exit(boss, e):
        pass

    @staticmethod
    def do(boss):
        boss.frame += 12 * 0.5 * game_framework.frame_time

        if int(boss.frame) >= 12:
            boss.attack_finished = True
            boss.state_machine.handle_event(('WALK', 0))

    @staticmethod
    def draw(boss):
        if boss.face_dir == 1:
            boss.attack_image.clip_draw(int(boss.frame) * 150, 0, 150, 150, boss.x, boss.y, 200, 200)
        else:
            boss.attack_image.clip_composite_draw(int(boss.frame) * 150, 0, 150, 150, 0, 'h', boss.x, boss.y, 200, 200)


class Death:
    @staticmethod
    def enter(boss, e):
        boss.frame = 0

    @staticmethod
    def exit(boss, e):
        pass

    @staticmethod
    def do(boss):
        boss.frame += 10 * 0.5 * game_framework.frame_time

        if int(boss.frame) >= 10:
            boss.frame = 9  # 마지막 프레임에서 멈춤
            # 일정 시간 후 게임 월드에서 제거
            if not hasattr(boss, 'death_timer'):
                boss.death_timer = 0
            boss.death_timer += game_framework.frame_time
            if boss.death_timer >= 1.0:
                game_world.remove_object(boss)

    @staticmethod
    def draw(boss):
        if boss.face_dir == 1:
            boss.death_image.clip_draw(int(boss.frame) * 150, 0, 150, 150, boss.x, boss.y, 200, 200)
        else:
            boss.death_image.clip_composite_draw(int(boss.frame) * 150, 0, 150, 150, 0, 'h', boss.x, boss.y, 200, 200)


class Boss:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 100
        self.hp = 15
        self.max_hp = 15
        self.frame = 0
        self.face_dir = 1
        self.dir_x = 0
        self.dir_y = 0
        self.walk_time = 0

        # 이미지 로드 (경로는 실제 리소스 경로에 맞게 수정)
        self.walk_image = load_image('./Resource/boss/walk.png')
        self.attack_image = load_image('./Resource/boss/attack.png')
        self.death_image = load_image('./Resource/boss/death.png')

        self.state_machine = StateMachine(self)
        self.state_machine.start()

    def update(self):
        self.state_machine.update()

    def draw(self):
        self.state_machine.draw()
        # 체력바 그리기
        draw_rectangle(self.x - 50, self.y + 120, self.x + 50, self.y + 130)
        hp_width = (self.hp / self.max_hp) * 100
        draw_rectangle(self.x - 50, self.y + 120, self.x - 50 + hp_width, self.y + 130)

    def get_bb(self):
        return self.x - 75, self.y - 75, self.x + 75, self.y + 75

    def handle_collision(self, group, other):
        if group == 'attack:boss':
            if self.state_machine.cur_state != Death:
                self.hp -= 1
                if self.hp <= 0:
                    self.state_machine.handle_event(('DEATH', 0))