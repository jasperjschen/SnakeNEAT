import random

cube_width = 20
cube_height = 20
body_margin = 0
width = 600
height = 600


class Snake:
    speed = cube_width
    body = []
    score = 0
    hunger = 200
    fitness = 0
    time_alive = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.body = [[self.x, self.y],
                     [self.x + cube_width + body_margin, self.y],
                     [self.x + 2 * cube_width + 2 * body_margin, self.y]]
        self.x = self.x + 2 * cube_width + 2 * body_margin

    def move_up(self):
        self.x = self.body[-1][0]
        self.y = self.body[-1][1] - self.speed
        self.body.append([self.x, self.y])

    def move_down(self):
        self.x = self.body[-1][0]
        self.y = self.body[-1][1] + self.speed
        self.body.append([self.x, self.y])

    def move_right(self):
        self.x = self.body[-1][0] + self.speed
        self.y = self.body[-1][1]
        self.body.append([self.x, self.y])

    def move_left(self):
        self.x = self.body[-1][0] - self.speed
        self.y = self.body[-1][1]
        self.body.append([self.x, self.y])

    def update(self):
        self.body.pop(0)


class Fruit:
    x = 0
    y = 0
    fruit_spawned = True

    def generate_new_fruit(self):
        self.x = random.randrange(60, width - 60, cube_width)
        self.y = random.randrange(60, width - 60, cube_width)
