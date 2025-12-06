from pico2d import *

class Wall:
    def __init__(self, x, y, width, height):
        self.x = x  # 중심 x 좌표
        self.y = y  # 중심 y 좌표
        self.width = width
        self.height = height

    def update(self):
        pass

    def draw(self):
        # 바운딩박스 그리기 (디버깅용 - 빨간색)
        left = self.x - self.width // 2
        right = self.x + self.width // 2
        bottom = self.y - self.height // 2
        top = self.y + self.height // 2
        draw_rectangle(left, bottom, right, top)

    def get_bb(self):
        return (self.x - self.width // 2,
                self.y - self.height // 2,
                self.x + self.width // 2,
                self.y + self.height // 2)

    def handle_collision(self, group, other):
        pass