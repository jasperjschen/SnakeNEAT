import random

import pygame

cube_width = 20
cube_height = 20
body_margin = 0


class Snake:
    x = 100
    y = 100
    speed = 20
    body = []

    def __init__(self):
        self.body = [[self.x, self.y],
                     [self.x + cube_width + body_margin, self.y],
                     [self.x + 2 * cube_width + 2 * body_margin, self.y]]

    def move_up(self):
        x_temp = self.body[-1][0]
        y_temp = self.body[-1][1] - self.speed
        self.body.append([x_temp, y_temp])

    def move_down(self):
        x_temp = self.body[-1][0]
        y_temp = self.body[-1][1] + self.speed
        self.body.append([x_temp, y_temp])

    def move_right(self):
        x_temp = self.body[-1][0] + self.speed + body_margin
        y_temp = self.body[-1][1]
        self.body.append([x_temp, y_temp])

    def move_left(self):
        x_temp = self.body[-1][0] - self.speed
        y_temp = self.body[-1][1]
        self.body.append([x_temp, y_temp])

    def update(self):
        self.body.pop(0)


class Fruit:
    x = 0
    y = 0
    fruit_spawned = True

    def generate_new_fruit(self):
        self.x = random.randint(60, 1280 - 60)
        self.y = random.randint(60, 960 - 60)


def main():
    pygame.init()
    pygame.display.set_caption("Snake NEAT")
    screen = pygame.display.set_mode((1280, 960))

    score = 0

    snake = Snake()
    fruit = Fruit()

    running = True

    clock = pygame.time.Clock()

    direction = "right"

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            key = pygame.key.get_pressed()

            if key[pygame.K_RIGHT] and direction != "left":
                direction = "right"
            if key[pygame.K_LEFT] and direction != "right":
                direction = "left"
            if key[pygame.K_UP] and direction != "down":
                direction = "up"
            if key[pygame.K_DOWN] and direction != "up":
                direction = "down"

        screen.fill((0, 0, 0))

        for body in snake.body:
            pygame.draw.rect(screen, (255, 255, 255), (body[0], body[1], cube_height, cube_width))

        if direction == "right":
            snake.move_right()
        elif direction == "left":
            snake.move_left()
        elif direction == "up":
            snake.move_up()
        elif direction == "down":
            snake.move_down()

        if fruit.fruit_spawned:
            fruit.generate_new_fruit()
            fruit.fruit_spawned = False

        pygame.draw.rect(screen, (255, 0, 0), (fruit.x, fruit.y, cube_height, cube_width))

        if pygame.Rect(snake.body[-1][0], snake.body[-1][1], cube_height, cube_width).colliderect\
                (fruit.x, fruit.y, cube_height, cube_width):
            fruit.fruit_spawned = True
            score += 1
        else:
            snake.update()

        pygame.display.update()
        clock.tick(20)

    pygame.quit()


def check_border_death():
    return None


def check_body_death():
    return None


if __name__ == "__main__":
    main()
