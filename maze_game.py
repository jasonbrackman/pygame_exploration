import enum
import random
from typing import NamedTuple, Callable, List

import pygame
import pathfinding


class Colour(tuple, enum.Enum):
    EMPTY = (5, 5, 5)
    BLOCKED = (127, 127, 127)
    START = (250, 5, 5)
    GOAL = (5, 5, 250)
    PATH = (40, 200, 40)


class Location(NamedTuple):
    row: int
    col: int


class Cube:
    rows = 20
    width = 500

    def __init__(
        self,
        pos: Location,
        color: Colour = Colour.EMPTY,
    ):
        self.pos = pos
        self.color = color

    def draw(self, surface):
        length = self.width // self.rows
        # length = 10
        # print(self.pos.row, self.pos.col)
        pygame.draw.rect(
            surface,
            self.color,
            (self.pos.row * length + 1, self.pos.col * length + 1, length - 2, length - 2),
        )


class Maze:
    def __init__(self, size, cell_size):
        self.size = size
        self.cell_size = cell_size
        self.rows, self.cols = self._get_rows_and_cols()
        self.start = Location(0, 0)
        self.goal = Location(10, 10)

        self.cells = self._randomly_fill()

    def _randomly_fill(self, sparseness: float = 0.2) -> list:
        grid = [[Cube(Location(c, r), color=Colour.EMPTY) for c in range(self.cols)] for r in range(self.rows)]

        for row in range(self.rows):
            for col in range(self.cols):
                if random.uniform(0, 1.0) < sparseness:
                    grid[row][col].color = Colour.BLOCKED

        # Setup the start and end of the maze points
        self.goal = Location(self.rows-1, self.cols-1)
        grid[self.start.row][self.start.col].color = Colour.START
        grid[self.goal.row][self.goal.col].color = Colour.GOAL

        return grid

    def _get_rows_and_cols(self):
        rows, cols = self.size
        rows = rows // self.cell_size
        cols = cols // self.cell_size
        return cols, rows

    def draw_grid(self, surface) -> None:
        """
        Draw a generic grid based on the length/rows passed in.

        :param surface: Pygame screen
        :return: None
        """

        width, height = self.size

        x, y = 0, 0
        while x < width:
            x += self.cell_size
            y += self.cell_size
            pygame.draw.line(surface, (255, 255, 255), (x, 0), (x, height))
            pygame.draw.line(surface, (255, 255, 255), (0, y), (width, y))

    def draw_cells(self, surface) -> None:
        for r in self.cells:
            for c in r:
                c.draw(surface)

    def goal_test(self, location: Location) -> bool:
        return location == self.goal

    def successors(self, loc: Location) -> List[Location]:
        successors: List[Location] = []
        # Test UP
        if loc.row - 1 >= 0 and self.cells[loc.row-1][loc.col].color != Colour.BLOCKED:
            successors.append(Location(loc.row-1, loc.col))

        # Test DOWN
        if loc.row + 1 < self.rows and self.cells[loc.row+1][loc.col].color != Colour.BLOCKED:
            successors.append(Location(loc.row+1, loc.col))

        # Test LEFT
        if loc.col - 1 >= 0 and self.cells[loc.row][loc.col-1].color != Colour.BLOCKED:
            successors.append(Location(loc.row, loc.col-1))

        # Test RIGHT
        if loc.col + 1 < self.cols:
            if self.cells[loc.row][loc.col+1].color != Colour.BLOCKED:
                successors.append(Location(loc.row, loc.col+1))

        return successors


def manhattan_distance(goal: Location) -> Callable[[Location], float]:
    def distance(ml: Location) -> float:
        xdist: int = abs(ml.col - goal.col)
        ydist: int = abs(ml.row - goal.row)
        return xdist + ydist

    return distance


def main():

    size = (500, 500)
    cell_size = 25
    background_colour = (20, 20, 20)

    # instantiate the rendering object (surface), BG colour, and title
    screen = pygame.display.set_mode(size)
    screen.fill(background_colour)
    pygame.display.set_caption("Maze Game")
    clock = pygame.time.Clock()

    # Create Maze
    maze = Maze(size, cell_size)

    maze.draw_grid(screen)
    maze.draw_cells(screen)

    distance = manhattan_distance(maze.goal)
    solution = pathfinding.astar(maze.start, maze.goal_test, maze.successors, distance)
    print(solution)
    cached_path = pathfinding.node_to_path(solution) if solution is not None else []

    # Game Loop
    running = True  # len(cached_path) > 0
    # current = cached_path.pop(0)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        clock.tick(5)  # 30 would be real time - slower < 30 > faster
        current = cached_path.pop(0)

        if maze.cells[current.row][current.col].color == Colour.EMPTY:
            maze.cells[current.row][current.col].color = Colour.PATH
        # if maze.cells[current.row][current.col].color != Colour.EMPTY:
        #     # need to invalidate the cache and start again
        #     print("wh?")
        #     solution = pathfinding.astar(current, maze.goal_test, maze.successors, distance)
        #     if solution is None:
        #         print("No solution found using A*!")
        #     else:
        #         cached_path = pathfinding.node_to_path(solution)
        #         if len(cached_path) > 1:
        #
        #             past = cached_path[0]
        #             maze.cells[past.row][past.col].color = Colour.EMPTY
        #
        #             move = cached_path[1]
        #             maze.start = move
        #             maze.cells[move.row][move.col].color = Colour.PATH

        maze.draw_cells(screen)
        # clear and redraw entire grid (seems inefficient).
        # screen.fill(background_colour)

        pygame.display.update()


if __name__ == "__main__":
    main()
