import random
from pico2d import *

import game_framework
import game_world
from character import Character
from slime import spawn_slimes
from background import Background

startscreen = None
show_startscreen = True
character = None
background = None
slimes = []

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
            show_startscreen = False
        elif not show_startscreen:
            # 2번 키 - 모든 슬라임 death 토글
            if event.type == SDL_KEYDOWN and event.key == SDLK_2:
                for slime in slimes:
                    slime.state_machine.handle_state_event(('DEATH', None))
            else:
                character.handle_event(event)

def add_background():
    global background
    if background is None:
        background = Background()
        game_world.add_object(background, 0)

def init():
    global startscreen, character
    startscreen = load_image("./Resource/startscreen/startscreen.png")
    character = Character()
    game_world.add_object(character, 2)

    slimes = spawn_slimes(5)

    game_world.add_collision_pair('character:slime', character, None)
    for slime in slimes:
        game_world.add_collision_pair('character:slime', None, slime)
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