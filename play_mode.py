import random
from pico2d import *

import game_framework
import game_world
import common
from character import Character
from slime import spawn_slimes
from background import Background
from wall import Wall

startscreen = None
show_startscreen = True
character = None
background = None
slimes = []
walls = []

def handle_events():
    global show_startscreen
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEBUTTONDOWN and show_startscreen:
            add_background()
            add_walls()  # 추가
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
    walls.append(Wall(800, 500, 100, 300))
    walls.append(Wall(400, 300, 200, 50))
    walls.append(Wall(1200, 700, 150, 100))

    for wall in walls:
        game_world.add_object(wall, 1)
        game_world.add_collision_pair('character:wall', common.character, wall)
        for slime in slimes:
            game_world.add_collision_pair('slime:wall', slime, wall)

def init():
    global startscreen, slimes
    startscreen = load_image("./Resource/startscreen/startscreen.png")
    common.character = Character()
    game_world.add_object(common.character, 2)

    slimes = spawn_slimes(5)

    game_world.add_collision_pair('character:slime', common.character, None)
    game_world.add_collision_pair('attack:slime', common.character, None)
    game_world.add_collision_pair('slime_attack:character', None, common.character)
    game_world.add_collision_pair('character:wall', common.character, None)
    game_world.add_collision_pair('slime:wall', None, None)

    for slime in slimes:
        game_world.add_collision_pair('character:slime', None, slime)
        game_world.add_collision_pair('attack:slime', None, slime)
        game_world.add_collision_pair('slime_attack:character', slime, None)
    pass

def update():
    if not show_startscreen:
        game_world.update()
        game_world.handle_collisions()

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