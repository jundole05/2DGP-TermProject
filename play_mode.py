import random
from pico2d import *

import game_framework
import game_world
import common
from character import Character
from slime import spawn_slimes
from background import Background
from wall import Wall
from portal import Portal

startscreen = None
show_startscreen = True
character = None
background = None
slimes = []
walls = []
portal = None
current_stage = 1

def handle_events():
    global show_startscreen
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEBUTTONDOWN and show_startscreen:
            init_stage_1()
            show_startscreen = False
        elif not show_startscreen:
            if event.type == SDL_KEYDOWN and event.key == SDLK_2:
                for slime in slimes:
                    slime.state_machine.handle_state_event(('DEATH', None))
            else:
                common.character.handle_event(event)

def check_attack_collision():
    if isinstance(common.character.state_machine.cur_state, common.character.ATTACK.__class__):
        attack_state = common.character.state_machine.cur_state
        if attack_state.attack_bb:
            attack_left, attack_bottom, attack_right, attack_top = attack_state.attack_bb
            for slime in slimes:
                slime_left, slime_bottom, slime_right, slime_top = slime.get_bb()

                # 바운딩박스 충돌 검사
                if not (attack_right < slime_left or attack_left > slime_right or
                        attack_top < slime_bottom or attack_bottom > slime_top):
                    # 충돌 발생 - 슬라임을 death 상태로 변경
                    slime.state_machine.handle_state_event(('DEATH', None))
def add_background():
    global background
    if background is None:
        background = Background()
        game_world.add_object(background, 0)


def add_walls():
    global walls
    # 벽 추가 - 여기에 원하는 만큼 벽을 추가
    walls.append(Wall(80, 700, 22, 750))


    for wall in walls:
        game_world.add_object(wall, 1)
        game_world.add_collision_pair('character:wall', common.character, wall)
        for slime in slimes:
            game_world.add_collision_pair('slime:wall', slime, wall)


def init_stage_1():
    global background, slimes, walls, portal, current_stage
    current_stage = 1

    # 배경 추가
    if background is None:
        background = Background()
        game_world.add_object(background, 0)
    else:
        background.image = load_image('./Resource/map/map1.png')

    # 기존 슬라임 제거
    for slime in slimes:
        game_world.remove_object(slime)
    slimes.clear()

    # 기존 벽 제거
    for wall in walls:
        game_world.remove_object(wall)
    walls.clear()



    # 1스테이지 벽 생성
    walls.append(Wall(80, 700, 22, 750))
    walls.append(Wall(1520, 700, 22, 750))
    walls.append(Wall(350, 360, 560, 50))
    walls.append(Wall(1240, 360, 560, 50))

    walls.append(Wall(430, 630, 400, 50))
    walls.append(Wall(240, 800, 22, 350))
    walls.append(Wall(1160, 630, 400, 50))
    walls.append(Wall(1360, 800, 22, 350))

    walls.append(Wall(570, 830, 240, 50))
    walls.append(Wall(450, 900, 22, 170))
    walls.append(Wall(1030, 830, 240, 50))
    walls.append(Wall(1150, 900, 22, 170))
    for wall in walls:
        game_world.add_object(wall, 1)

    avoid = [common.character] + walls if common.character else walls
    slimes = spawn_slimes(5, depth=1, avoid_objects=avoid)

    # 포탈 생성 (좌표: 1400, 800)
    if portal is None:
        portal = Portal(800, 950, 100, 100)
        game_world.add_object(portal, 1)

    # 충돌 쌍 재설정
    setup_collisions()


def init_stage_2():
    global background, slimes, walls, portal, current_stage
    current_stage = 2

    # 배경 변경
    background.image = load_image('./Resource/map/map2.png')

    # 기존 슬라임 제거
    for slime in slimes:
        game_world.remove_object(slime)
    slimes.clear()

    # 기존 벽 제거
    for wall in walls:
        game_world.remove_object(wall)
    walls.clear()

    # 포탈 제거
    if portal:
        game_world.remove_object(portal)
        portal = None


    # 2스테이지 벽 생성 (예시)
    walls.append(Wall(800, 500, 150, 300))
    walls.append(Wall(400, 700, 200, 100))
    for wall in walls:
        game_world.add_object(wall, 1)

    avoid = [common.character] + walls if common.character else walls
    slimes = spawn_slimes(7, depth=1, avoid_objects=avoid)

    # 캐릭터 위치 초기화
    common.character.x = 200
    common.character.y = 200

    # 충돌 쌍 재설정
    setup_collisions()


def setup_collisions():
    # 기존 충돌 쌍 초기화
    game_world.collision_pairs.clear()

    # 캐릭터 관련 충돌
    game_world.add_collision_pair('character:slime', common.character, None)
    game_world.add_collision_pair('attack:slime', common.character, None)
    game_world.add_collision_pair('slime_attack:character', None, common.character)
    game_world.add_collision_pair('character:wall', common.character, None)
    game_world.add_collision_pair('slime:wall', None, None)

    # 포탈 충돌 (1스테이지만)
    if portal and current_stage == 1:
        game_world.add_collision_pair('character:portal', common.character, portal)

    # 슬라임 충돌 등록
    for slime in slimes:
        game_world.add_collision_pair('character:slime', None, slime)
        game_world.add_collision_pair('attack:slime', None, slime)
        game_world.add_collision_pair('slime_attack:character', slime, None)
        game_world.add_collision_pair('slime:wall', slime, None)

    # 벽 충돌 등록
    for wall in walls:
        game_world.add_collision_pair('character:wall', None, wall)
        for slime in slimes:
            game_world.add_collision_pair('slime:wall', None, wall)


def init():
    global startscreen
    startscreen = load_image("./Resource/startscreen/startscreen.png")
    common.character = Character()
    game_world.add_object(common.character, 2)


def update():
    if not show_startscreen:
        game_world.update()
        game_world.handle_collisions()

        # 캐릭터가 레벨 2가 되면 포탈 활성화
        if portal and common.character.level >= 2:
            portal.activate()

        # 포탈 트리거 확인 (충돌 처리 후 실행)
        if hasattr(common.character, 'portal_triggered') and common.character.portal_triggered:
            delattr(common.character, 'portal_triggered')
            init_stage_2()

def draw():
    clear_canvas()
    if show_startscreen:
        startscreen.draw_to_origin(0, 0, 1600, 1000)
    else:
        game_world.render()
    update_canvas()

def finish():
    game_world.clear()

def pause(): pass
def resume(): pass