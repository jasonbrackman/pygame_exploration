"""
Looking at exploring Pygame library with regards to:
- creating a surface,
- creating basic shapes,
- moving shapes around,
- 'updating/flipping' the screen,


Used the following resources:
https://techwithtim.net/tutorials/game-development-with-python/snake-pygame/tutorial-1/

"""
import collections
import random
import typing

import pygame

Facing = collections.namedtuple("facing", ("left", "right", "up", "down"))
FACING = Facing(left=(-1, 0), right=(1, 0), up=(0, -1), down=(0, 1))


class Position(typing.NamedTuple):
    row: int
    col: int


class Cube:
    rows = 20
    width = 500

    def __init__(
        self,
        start_pos: Position,
        direction: Facing = FACING.right,
        color: tuple = (255, 0, 0),
    ):
        self.pos = start_pos
        self.direction = direction
        self.color = color

    def move(self, direction: Facing):
        self.direction = direction
        self.pos = Position(self.pos.row + self.direction[0], self.pos.col + self.direction[1])

    def draw(self, surface, eyes=False):
        length = self.width // self.rows

        pygame.draw.rect(
            surface,
            self.color,
            (self.pos.row * length + 1, self.pos.col * length + 1, length - 2, length - 2),
        )

        if eyes:
            centre = length // 2
            radius = 3
            eye_01 = (self.pos.row * length + centre - radius, self.pos.col * length + 8)
            eye_02 = (self.pos.row * length + centre + 8 - radius, self.pos.col * length + 8)
            pygame.draw.circle(surface, (0, 0, 0), eye_01, radius)
            pygame.draw.circle(surface, (0, 0, 0), eye_02, radius)


class Snake:
    body = []
    turns = dict()

    def __init__(self, color, pos: (int, int)):
        self.color = color
        self.head = Cube(pos)
        self.body.append(self.head)
        self.direction = FACING.right

    def move(self):
        """
        Sets the current position of each cube of the snake body and then moves
        each cube in the direction it should go.
        :return:
        """

        # Keypresses that are interesting and their direction values.
        choices = {
            pygame.K_LEFT: FACING.left,
            pygame.K_RIGHT: FACING.right,
            pygame.K_UP: FACING.up,
            pygame.K_DOWN: FACING.down,
        }

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            else:
                pos = (
                    event.dict.get("key", None)
                    if event.type == pygame.KEYDOWN
                    else None
                )
                pos = choices.get(pos, None)
                if pos is not None:
                    self.turns[self.head.pos] = pos

        for i, cube in enumerate(self.body):

            position = cube.pos
            if position in self.turns:
                turn = self.turns[position]
                cube.move(turn)

                if i == len(self.body) - 1:
                    self.turns.pop(position)
            else:
                # Ensure when we hit the edge of the world we wrap around to the other side
                # x = left/right
                # y = up/down

                # Left Wall
                if cube.direction == FACING.left and cube.pos[0] <= 0:
                    cube.pos = Position(cube.rows, cube.pos[1])

                # Right Wall
                elif cube.direction == FACING.right and cube.pos[0] >= cube.rows - 1:
                    cube.pos = Position(-1, cube.pos[1])

                elif cube.direction == FACING.up and cube.pos[1] <= 0:
                    cube.pos = Position(cube.pos[0], cube.rows)

                elif cube.direction == FACING.down and cube.pos[1] >= cube.rows - 1:
                    cube.pos = Position(cube.pos[0], -1)
                # this needs to be updated to take FACING instead
                cube.move(cube.direction)

        return True

    def reset(self, pos):
        ...

    def add_cube(self):
        tail = self.body[-1]

        # get direction of tail cube
        dx, dy = tail.direction

        # Get old position -- and update it using the direction of movement
        new_pos = tail.pos
        new_pos.row = 0 if dx == 0 else (new_pos.row + -dx)
        new_pos.col = 0 if dy == 0 else (new_pos.col + -dy)

        # add one more cube to the snake body trailing behind the
        self.body.append(Cube(new_pos))

    def draw(self, surface):
        for index, cube in enumerate(self.body):
            cube.draw(surface, index == 0)

    def add_tail(self):
        tail = self.body[-1]

        tail_pos = list(tail.pos)

        if tail.direction == FACING.left:
            tail_pos[0] += 1
        elif tail.direction == FACING.right:
            tail_pos[0] -= 1
        elif tail.direction == FACING.up:
            tail_pos[1] += 1
        elif tail.direction == FACING.down:
            tail_pos[1] -= 1

        tail_pos = Position(tail_pos[0], tail_pos[1])
        new_tail = Cube(tail_pos, tail.direction)
        self.body.append(new_tail)


def draw_grid(surface, size: (int, int), rows: int) -> None:
    """
    Draw a generic grid based on the length/rows passed in.

    :param surface: Pygame screen
    :param size: defines the width/height of the screen
    :param rows: the number of divisions that will make up the rows/cols
    :return: None
    """

    width, height = size

    gap_w = width // rows
    gap_h = height // rows
    x, y = 0, 0
    for _ in range(rows):
        x += gap_w
        y += gap_h
        pygame.draw.line(surface, (255, 255, 255), (x, 0), (x, height))
        pygame.draw.line(surface, (255, 255, 255), (0, y), (width, y))


def random_snack(rows, snake: Snake) -> Position:
    positions = [s.pos for s in snake.body]

    while True:
        x = random.randrange(rows)
        y = random.randrange(rows)
        if (x, y) in positions:
            continue
        else:
            break

    return Position(x, y)


def main():

    size = (500, 500)
    background_colour = (20, 20, 20)

    # instantiate the rendering object (surface), BG colour, and title
    screen = pygame.display.set_mode(size)
    screen.fill(background_colour)
    pygame.display.set_caption("Snake Game")

    # Need a clock to control the tick's per second
    clock = pygame.time.Clock()

    # Create initial board
    draw_grid(screen, size, 20)

    # Create a snake character
    snake = Snake((240, 0, 0), Position(0, 0))
    snack = Cube(random_snack(20, snake), color=(10, 210, 10))

    # Game Loop
    running = True
    while running:
        clock.tick(10)  # 30 would be real time - slower < 30 > faster

        # clear and redraw entire grid (seems inefficient).
        screen.fill(background_colour)
        draw_grid(screen, size, 20)

        # Update snake position
        running = snake.move()
        # Check if head of snake eats the snack
        if snake.body[0].pos == snack.pos:
            snake.add_tail()
            snack = Cube(random_snack(20, snake), color=(10, 210, 10))

        positions = [s.pos for s in snake.body]
        if len(positions) != len(set(positions)):
            print(f"Your Snake length got to be {len(snake.body)} units long!")
            print("Game Over!")

            running = False
        snake.draw(screen)
        snack.draw(screen)
        # pygame.display.flip()  # updates the entire surface
        pygame.display.update()  # updates the entire surface (Or rect area passed in)


if __name__ == "__main__":
    main()
