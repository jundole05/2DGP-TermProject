from pico2d import *
import game_framework

import play_mode as start_mode

open_canvas(1600, 1000)
startscreen = load_image ("./Resource/startscreen/startscreen.png")
startscreen.draw_now(800, 500)
game_framework.run(start_mode)
delay(5)