import pickle

import neat
import snake
import pygame

high_score = 0


class SnakeGame:
    def __init__(self, net):
        pygame.init()
        pygame.display.set_caption("Snake NEAT")

        self.width = 800
        self.height = 600
        self.cube_size = 20
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.font = pygame.font.SysFont("roboto", 15)
        self.FPS = 1000
        self.clock = pygame.time.Clock()
        self.running = True

        self.snake = snake.Snake(100, 100)
        self.fruit = snake.Fruit()
        self.direction = "right"

        self.generation = 0
        self.fitness = 0
        self.network = net

    def eval_fitness(self):

        while self.running:
            global high_score

            self.screen.fill((0, 0, 0))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.get_direction()
            self.get_snake_action()

            self.draw_vision(self.get_inputs(return_dict=True))
            self.draw_snake()
            self.draw_fruit()
            self.print_stats()
            self.check_fruit_collision()

            if self.snake.score > high_score:
                high_score = self.snake.score

            if self.check_wall_collision() or self.check_body_collision():
                self.running = False

            pygame.display.update()
            self.clock.tick(self.FPS)

            self.fitness = self.snake.time_alive + 100 * self.snake.score

            if self.fitness < 0 or not self.running or self.snake.hunger <= 0:
                return self.fitness

        pygame.quit()

    def get_direction(self):
        key = self.get_outputs()

        if key[pygame.K_RIGHT] and self.direction != "left":
            self.direction = "right"
        elif key[pygame.K_LEFT] and self.direction != "right":
            self.direction = "left"
        elif key[pygame.K_UP] and self.direction != "down":
            self.direction = "up"
        elif key[pygame.K_DOWN] and self.direction != "up":
            self.direction = "down"

    def get_snake_action(self):
        if self.direction == "right":
            self.snake.move_right()
        elif self.direction == "left":
            self.snake.move_left()
        elif self.direction == "up":
            self.snake.move_up()
        elif self.direction == "down":
            self.snake.move_down()
        self.snake.hunger -= 1
        self.snake.time_alive += 1

    def draw_snake(self):
        counter = 0
        gradient_rate = 255 // (len(self.snake.body) * 2)
        for body in self.snake.body[::-1]:
            colour = (255 - (counter * gradient_rate), 255 - (counter * gradient_rate), 255 - (counter * gradient_rate))
            pygame.draw.rect(self.screen, colour, (body[0], body[1], self.cube_size, self.cube_size))
            counter += 1

    def draw_fruit(self):
        if self.fruit.fruit_spawned:
            self.fruit.generate_new_fruit()
            while [self.fruit.x, self.fruit.y] in self.snake.body:
                self.fruit.generate_new_fruit()
            self.fruit.fruit_spawned = False

        pygame.draw.rect(self.screen, (255, 0, 0), (self.fruit.x, self.fruit.y, self.cube_size, self.cube_size))

    def check_fruit_collision(self):
        if pygame.Rect(self.snake.body[-1][0], self.snake.body[-1][1], self.cube_size, self.cube_size).colliderect \
                    (self.fruit.x, self.fruit.y, self.cube_size, self.cube_size):
            self.fruit.fruit_spawned = True
            self.snake.score += 1
            if self.snake.hunger <= 400:
                self.snake.hunger += 100
        else:
            self.snake.update()

    def check_wall_collision(self):
        if self.snake.body[-1][0] + self.cube_size <= 0 or self.snake.body[-1][0] >= self.width:
            return True
        if self.snake.body[-1][1] + self.cube_size <= 0 or self.snake.body[-1][1] >= self.height:
            return True
        return False

    def check_body_collision(self):
        for body in self.snake.body[:len(self.snake.body) - 1]:
            if pygame.Rect(self.snake.body[-1][0], self.snake.body[-1][1], self.cube_size, self.cube_size).colliderect\
                        (body[0], body[1], self.cube_size, self.cube_size):
                return True
        return False

    def print_stats(self):
        global high_score

        fitness_text = self.font.render("FITNESS: " + str(self.fitness), True, (255, 255, 255))
        self.screen.blit(fitness_text, (10, 10))
        score_text = self.font.render("SCORE: " + str(self.snake.score), True, (255, 255, 255))
        self.screen.blit(score_text, (10, 30))
        time_alive_text = self.font.render("TIME ALIVE: " + str(self.snake.time_alive), True, (255, 255, 255))
        self.screen.blit(time_alive_text, (10, 50))
        hunger_text = self.font.render("HUNGER: " + str(self.snake.hunger), True, (255, 255, 255))
        self.screen.blit(hunger_text, (10, 70))
        high_score_text = self.font.render("HIGH SCORE: " + str(high_score), True, (255, 255, 255))
        self.screen.blit(high_score_text, (10, 90))


    def get_inputs(self, return_dict=False):
        input_dict = {
            "snake_wall_n": self.calc_wall_distance("n"),
            "snake_wall_ne": self.calc_wall_distance("ne"),
            "snake_wall_e": self.calc_wall_distance("e"),
            "snake_wall_se": self.calc_wall_distance("se"),
            "snake_wall_s": self.calc_wall_distance("s"),
            "snake_wall_sw": self.calc_wall_distance("sw"),
            "snake_wall_w": self.calc_wall_distance("w"),
            "snake_wall_nw": self.calc_wall_distance("nw"),

            "snake_fruit_n": self.calc_fruit_distance("n"),
            "snake_fruit_ne": self.calc_fruit_distance("ne"),
            "snake_fruit_e": self.calc_fruit_distance("e"),
            "snake_fruit_se": self.calc_fruit_distance("se"),
            "snake_fruit_s": self.calc_fruit_distance("s"),
            "snake_fruit_sw": self.calc_fruit_distance("sw"),
            "snake_fruit_w": self.calc_fruit_distance("w"),
            "snake_fruit_nw": self.calc_fruit_distance("nw"),

            "snake_tail_n": self.calc_tail_distance("n"),
            "snake_tail_ne": self.calc_tail_distance("ne"),
            "snake_tail_e": self.calc_tail_distance("e"),
            "snake_tail_se": self.calc_tail_distance("se"),
            "snake_tail_s": self.calc_tail_distance("s"),
            "snake_tail_sw": self.calc_tail_distance("sw"),
            "snake_tail_w": self.calc_tail_distance("w"),
            "snake_tail_nw": self.calc_tail_distance("nw"),
        }

        if return_dict:
            return input_dict
        else:
            return list(input_dict.values())

    def calc_wall_distance(self, direction):
        dist_list = []

        dist = 0
        dist_list.append(dist)

        if direction == "n":
            y = self.snake.y

            while y >= 0:
                dist += 1
                y -= self.cube_size
                dist_list.append(dist)

        elif direction == "ne":
            x = self.snake.x
            y = self.snake.y

            while x <= self.width - self.cube_size and y >= 0:
                dist += 1
                x += self.cube_size
                y -= self.cube_size
                dist_list.append(dist)
        elif direction == "e":
            x = self.snake.x

            while x <= self.width - self.cube_size:
                dist += 1
                x += self.cube_size
                dist_list.append(dist)
        elif direction == "se":
            x = self.snake.x
            y = self.snake.y

            while x <= self.width - self.cube_size and y <= self.height - self.cube_size:
                dist += 1
                x += self.cube_size
                y += self.cube_size
                dist_list.append(dist)
        elif direction == "s":
            y = self.snake.y

            while y <= self.height - self.cube_size:
                dist += 1
                y += self.cube_size
                dist_list.append(dist)
        elif direction == "sw":
            x = self.snake.x
            y = self.snake.y

            while x >= 0 and y <= self.height - self.cube_size:
                dist += 1
                x -= self.cube_size
                y += self.cube_size
                dist_list.append(dist)
        elif direction == "w":
            x = self.snake.x

            while x >= 0:
                dist += 1
                x -= self.cube_size
                dist_list.append(dist)
        elif direction == "nw":
            x = self.snake.x
            y = self.snake.y

            while x >= 0 and y >= 0:
                dist += 1
                x -= self.cube_size
                y -= self.cube_size
                dist_list.append(dist)
        return dist_list[-1]

    def calc_fruit_distance(self, direction):
        if direction == "n":
            if self.snake.x == self.fruit.x:
                for dist in range(1, self.calc_wall_distance("n") + 1):
                    if self.snake.y - dist * self.cube_size == self.fruit.y:
                        return dist
        elif direction == "ne":
            for dist in range(1, self.calc_wall_distance("ne") + 1):
                if self.snake.y - dist * self.cube_size == self.fruit.y \
                        and self.snake.x + dist * self.cube_size == self.fruit.x:
                    return dist
        elif direction == "e":
            if self.snake.y == self.fruit.y:
                for dist in range(1, self.calc_wall_distance("e") + 1):
                    if self.snake.x + dist * self.cube_size == self.fruit.x:
                        return dist
        elif direction == "se":
            for dist in range(1, self.calc_wall_distance("se") + 1):
                if self.snake.y + dist * self.cube_size == self.fruit.y \
                        and self.snake.x + dist * self.cube_size == self.fruit.x:
                    return dist
        elif direction == "s":
            if self.snake.x == self.fruit.x:
                for dist in range(1, self.calc_wall_distance("s") + 1):
                    if self.snake.y + dist * self.cube_size == self.fruit.y:
                        return dist
        elif direction == "sw":
            for dist in range(1, self.calc_wall_distance("sw") + 1):
                if self.snake.y + dist * self.cube_size == self.fruit.y \
                        and self.snake.x - dist * self.cube_size == self.fruit.x:
                    return dist
        elif direction == "w":
            if self.snake.y == self.fruit.y:
                for dist in range(1, self.calc_wall_distance("w") + 1):
                    if self.snake.x - dist * self.cube_size == self.fruit.x:
                        return dist
        elif direction == "nw":
            for dist in range(1, self.calc_wall_distance("nw") + 1):
                if self.snake.y - dist * self.cube_size == self.fruit.y \
                        and self.snake.x - dist * self.cube_size == self.fruit.x:
                    return dist
        return 0

    def calc_tail_distance(self, direction):

        if direction == "n":
            if self.snake.x == self.snake.body[0][0]:
                for dist in range(1, self.calc_wall_distance("n") + 1):
                    if self.snake.y - dist * self.cube_size == self.snake.body[0][1]:
                        return dist
        elif direction == "ne":
            for dist in range(1, self.calc_wall_distance("ne") + 1):
                if self.snake.y - dist * self.cube_size == self.snake.body[0][1] \
                        and self.snake.x + dist * self.cube_size == self.snake.body[0][0]:
                    return dist
        elif direction == "e":
            if self.snake.y == self.snake.body[0][1]:
                for dist in range(1, self.calc_wall_distance("e") + 1):
                    if self.snake.x + dist * self.cube_size == self.snake.body[0][0]:
                        return dist
        elif direction == "se":
            for dist in range(1, self.calc_wall_distance("se") + 1):
                if self.snake.y + dist * self.cube_size == self.snake.body[0][1] \
                        and self.snake.x + dist * self.cube_size == self.snake.body[0][0]:
                    return dist
        elif direction == "s":
            if self.snake.x == self.snake.body[0][0]:
                for dist in range(1, self.calc_wall_distance("s") + 1):
                    if self.snake.y + dist * self.cube_size == self.snake.body[0][1]:
                        return dist
        elif direction == "sw":
            for dist in range(1, self.calc_wall_distance("sw") + 1):
                if self.snake.y + dist * self.cube_size == self.snake.body[0][1] \
                        and self.snake.x - dist * self.cube_size == self.snake.body[0][0]:
                    return dist
        elif direction == "w":
            if self.snake.y == self.snake.body[0][1]:
                for dist in range(1, self.calc_wall_distance("w") + 1):
                    if self.snake.x - dist * self.cube_size == self.snake.body[0][0]:
                        return dist
        elif direction == "nw":
            for dist in range(1, self.calc_wall_distance("nw") + 1):
                if self.snake.y - dist * self.cube_size == self.snake.body[0][1] \
                        and self.snake.x - dist * self.cube_size == self.snake.body[0][0]:
                    return dist
        return 0

    def get_outputs(self):
        out_lst = self.network.activate(self.get_inputs())

        output = []
        for out in out_lst:
            if out >= 0.5:
                output.append(True)
            else:
                output.append(False)

        keys = {pygame.K_UP: output[0],
                pygame.K_DOWN: output[1],
                pygame.K_RIGHT: output[2],
                pygame.K_LEFT: output[3]}

        return keys

    def draw_vision(self, input_dict):

        gray = (50, 50, 50)
        orange = (255, 100, 0)
        blue = (0, 0, 200)
        # draw distance to wall
        for dist in range(0, input_dict["snake_wall_n"]):
            pygame.draw.rect(self.screen, gray,
                             (self.snake.x, dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_wall_ne"]):
            pygame.draw.rect(self.screen, gray,
                             (self.snake.x + dist * self.cube_size, self.snake.y - dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_wall_e"]):
            pygame.draw.rect(self.screen, gray,
                             (self.snake.x + dist * self.cube_size, self.snake.y,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_wall_se"]):
            pygame.draw.rect(self.screen, gray,
                             (self.snake.x + dist * self.cube_size, self.snake.y + dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_wall_s"]):
            pygame.draw.rect(self.screen, gray,
                             (self.snake.x, self.snake.y + dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_wall_sw"]):
            pygame.draw.rect(self.screen, gray,
                             (self.snake.x - dist * self.cube_size, self.snake.y + dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_wall_w"]):
            pygame.draw.rect(self.screen, gray,
                             (dist * self.cube_size, self.snake.y,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_wall_nw"]):
            pygame.draw.rect(self.screen, gray,
                             (self.snake.x - dist * self.cube_size, self.snake.y - dist * self.cube_size,
                              self.cube_size, self.cube_size))

        # draw dist to fruit
        for dist in range(0, input_dict["snake_fruit_n"]):
            pygame.draw.rect(self.screen, orange,
                             (self.snake.x, self.snake.y - dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_fruit_ne"]):
            pygame.draw.rect(self.screen, orange,
                             (self.snake.x + dist * self.cube_size, self.snake.y - dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_fruit_e"]):
            pygame.draw.rect(self.screen, orange,
                             (self.snake.x + dist * self.cube_size, self.snake.y,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_fruit_se"]):
            pygame.draw.rect(self.screen, orange,
                             (self.snake.x + dist * self.cube_size, self.snake.y + dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_fruit_s"]):
            pygame.draw.rect(self.screen, orange,
                             (self.snake.x, self.snake.y + dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_fruit_sw"]):
            pygame.draw.rect(self.screen, orange,
                             (self.snake.x - dist * self.cube_size, self.snake.y + dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_fruit_w"]):
            pygame.draw.rect(self.screen, orange,
                             (self.snake.x - dist * self.cube_size, self.snake.y,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_fruit_nw"]):
            pygame.draw.rect(self.screen, orange,
                             (self.snake.x - dist * self.cube_size, self.snake.y - dist * self.cube_size,
                              self.cube_size, self.cube_size))

        # draw dist to tail

        for dist in range(0, input_dict["snake_tail_n"]):
            pygame.draw.rect(self.screen, blue,
                             (self.snake.x, self.snake.y - dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_tail_ne"]):
            pygame.draw.rect(self.screen, blue,
                             (self.snake.x + dist * self.cube_size, self.snake.y - dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_tail_e"]):
            pygame.draw.rect(self.screen, blue,
                             (self.snake.x + dist * self.cube_size, self.snake.y,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_tail_se"]):
            pygame.draw.rect(self.screen, blue,
                             (self.snake.x + dist * self.cube_size, self.snake.y + dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_tail_s"]):
            pygame.draw.rect(self.screen, blue,
                             (self.snake.x, self.snake.y + dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_tail_sw"]):
            pygame.draw.rect(self.screen, blue,
                             (self.snake.x - dist * self.cube_size, self.snake.y + dist * self.cube_size,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_tail_w"]):
            pygame.draw.rect(self.screen, blue,
                             (self.snake.x - dist * self.cube_size, self.snake.y,
                              self.cube_size, self.cube_size))

        for dist in range(0, input_dict["snake_tail_nw"]):
            pygame.draw.rect(self.screen, blue,
                             (self.snake.x - dist * self.cube_size, self.snake.y - dist * self.cube_size,
                              self.cube_size, self.cube_size))


def eval_genome(genome, config):
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    game = SnakeGame(net)

    return game.eval_fitness()


if __name__ == "__main__":

    config_path = "config-feedforward.txt"
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_path)

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    pe = neat.ParallelEvaluator(10, eval_genome)
    best_evolution = p.run(pe.evaluate, 1000)

    with open("snake.neat", "wb+") as f:
        f.write(pickle.dumps(best_evolution))
