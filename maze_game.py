import random
from typing import NamedTuple

import pygame
from enum import Enum


class Cell(str, Enum):
    EMPTY = " "
    BLOCKED = "X"
    START = "S"
    GOAL = "G"
    PATH = "*"


class Location(NamedTuple):
    row: int
    col: int


class Cube:
    rows = 20
    width = 500

    def __init__(
        self,
        pos: Location,
        color: tuple = (255, 0, 0),
    ):
        self.pos = pos
        self.color = color

    def draw(self, surface):
        length = self.width // self.rows

        pygame.draw.rect(
            surface,
            self.color,
            (self.pos.row * length + 1, self.pos.col * length + 1, length - 2, length - 2),
        )


class Maze:
    ...


def generate_maze(size: (int, int), sparseness: float = 0.3) -> list:
    rows, cols = size

    grid = [[Cube(Location(c, r), color=(5, 5, 5)) for c in range(cols)] for r in range(rows)]
    for row in range(rows):
        for col in range(cols):
            if random.uniform(0, 1.0) < sparseness:
                grid[row][col].color = (127, 127, 127)

    return grid


# def manhattan_distance(goal: MazeLocation) -> Callable[[MazeLocation], float]:
#     def distance(ml: MazeLocation) -> float:
#         xdist: int = abs(ml.column - goal.column)
#         ydist: int = abs(ml.row - goal.row)
#         return xdist + ydist
#
#     return distance

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


def main():

    size = (500, 500)
    background_colour = (20, 20, 20)

    # instantiate the rendering object (surface), BG colour, and title
    screen = pygame.display.set_mode(size)
    screen.fill(background_colour)
    pygame.display.set_caption("Maze Game")

    # Create initial board
    draw_grid(screen, size, 20)

    # Need a clock to control the tick's per second
    clock = pygame.time.Clock()
    walls = generate_maze(size, sparseness=0.32)

    # Setup the one time background
    draw_grid(screen, size, 20)

    # Setup the randomized walls
    for r in walls:
        for c in r:
            c.draw(screen)

    # Game Loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(30)  # 30 would be real time - slower < 30 > faster

        # clear and redraw entire grid (seems inefficient).
        # screen.fill(background_colour)

        pygame.display.update()


if __name__ == "__main__":
    main()
