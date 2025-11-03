from pico2d import *

class Background:
    def __init__(self):
        self.image = load_image('./Resource/map/map1.png')

    def update(self):
        pass  # 배경은 움직이지 않으니 비워둠

    def draw(self):
        # 화면 전체에 그리기
        self.image.draw_to_origin(0, 0, 1600, 1000)