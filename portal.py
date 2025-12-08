from pico2d import *

class Portal:
    def __init__(self, x, y, width=100, height=100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active = False
        self.image = load_image('./Resource/map/portal1.png')

    def update(self):
        pass

    def draw(self):
        # 투명 포탈이지만 디버깅용 바운딩박스 (초록색)
        if self.active:
            self.image.draw(self.x, self.y, self.width, self.height)
            left = self.x - self.width // 2
            right = self.x + self.width // 2
            bottom = self.y - self.height // 2
            top = self.y + self.height // 2
            draw_rectangle(left, bottom, right, top, 0, 255, 0)

    def get_bb(self):
        return (self.x - self.width // 2,
                self.y - self.height // 2,
                self.x + self.width // 2,
                self.y + self.height // 2)

    def activate(self):
        self.active = True

    def handle_collision(self, group, other):
        pass