import random
from pico2d import *

import game_framework
import game_world

startscreen = None
show_startscreen = True

def handle_events():
    global show_startscreen
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        elif event.type == SDL_MOUSEBUTTONDOWN and show_startscreen:
            show_startscreen = False

def init():
    global startscreen
    startscreen = load_image("./Resource/startscreen/startscreen.png")
    pass

def update():
    if not show_startscreen:
        game_world.update()
        game_world.handle_collisions()

def draw():
    clear_canvas()
    if show_startscreen:
        startscreen.draw(800, 450)
    else:
        game_world.render()
    update_canvas()

def finish():
    game_world.clear()

def pause(): pass
def resume(): pass