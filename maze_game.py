import enum
import random
from typing import NamedTuple, Callable, List

import pygame
import pathfinding

# __ Building Blocks __


class Colour(tuple, enum.Enum):
    EMPTY = (5, 5, 5)
    BLOCKED = (127, 127, 127)
    WALL = (200, 127, 127)
    TOWER = (50, 250, 50)
    SNACK = (187, 197, 255)
    START = (250, 5, 5)
    GOAL = (5, 5, 250)
    ZOMBIE = (40, 200, 40)
    LINE = (100, 100, 100)
    BULLET = (0, 0, 255)


class Location(NamedTuple):
    row: int
    col: int

# __ Characters __


class Cube:
    rows = 20
    width = 500

    def __init__(
        self,
        pos: Location,
        color: Colour = Colour.EMPTY,
        # rows: int = 20 * 5,
    ):
        self.pos = pos
        self.color = color
        # self.rows = rows

    def draw(self, surface):
        length = self.width // self.rows
        # length = 10
        # print(self.pos.row, self.pos.col)
        pygame.draw.rect(
            surface,
            self.color,
            (self.pos.row * length + 1, self.pos.col * length + 1, length - 2, length - 2),
        )


class Tower(Cube):
    def __init__(self, pos, color):
        super(Cube, self).__init__()
        self.pos = pos
        self.color = color
        self.bullets = []

    def shoot(self, surface):
        # Scan 5 spaced away for target
        # if found start shooting at target
        if len(self.bullets) == 0:
            bullet = Bullet(self.pos, Colour.BULLET)
            self.bullets.append(bullet)

        for bullet in self.bullets:
            bullet.move(surface)
            if bullet.life == 0:
                self.bullets.remove(bullet)

    def draw(self, surface):

        length = self.width // self.rows
        pygame.draw.rect(
            surface,
            self.color,
            (self.pos.row * length + 1, self.pos.col * length + 1, length - 2, length - 2),
        )

        # only shoot from center of tower
        if self.color == Colour.TOWER:
            self.shoot(surface)


class Snack(Cube):
    def __init__(self, pos, color):
        super(Cube, self).__init__()
        self.pos = pos
        self.color = color

    def draw(self, surface):
        length = self.width // self.rows
        pygame.draw.rect(
            surface,
            self.color,
            (self.pos.row * length + 1, self.pos.col * length + 1, length - 2, length - 2),
        )


class Zombie(Cube):
    def __init__(self, pos, color):
        super(Cube, self).__init__()
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
    def __init__(self, size, cell_size):
        self.size = size
        self.cell_size = cell_size
        self.rows, self.cols = self._get_rows_and_cols()
        self.start = Location(0, 0)
        self.goal = Location(10, 10)
        self.zombies = []
        self.cells = self._randomly_fill()

    def _randomly_fill(self, sparseness: float = 0.3) -> list:
        grid = [[Cube(Location(c, r), color=Colour.EMPTY) for c in range(self.cols)] for r in range(self.rows)]

        for row in range(self.rows):
            for col in range(self.cols):
                if random.uniform(0, 1.0) < sparseness:
                    if random.randint(0, 5) == 5:
                        grid[row][col].color = Colour.SNACK
                    else:
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
            pygame.draw.line(surface, Colour.LINE, (x, 0), (x, height))
            pygame.draw.line(surface, Colour.LINE, (0, y), (width, y))

    def draw_cells(self, surface) -> None:
        for r in self.cells:
            for c in r:
                c.draw(surface)

    def _process_click_point(self, x, y):
        x = x // self.cell_size  # gives the correct bucket for extremes -- but not middle
        y = y // self.cell_size

        return x, y

    def click_create_wall(self, x, y) -> None:
        x, y = self._process_click_point(x, y)

        # note the x, y is reversed -- its a bug need to revisit.
        self.cells[y][x].color = Colour.WALL

    def click_create_tower(self, x, y) -> None:
        x, y = self._process_click_point(x, y)
        try:
            for i in range(2):
                c = Colour.TOWER if i == 0 else Colour.WALL
                self.cells[y-i][x] = Tower(Location(x, y-i), c)
                self.cells[y+i][x] = Tower(Location(x, y+i), c)
                self.cells[y][x-i] = Tower(Location(x-i, y), c)
                self.cells[y][x+i] = Tower(Location(x+i, y), c)
        except Exception:
            pass

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

# __ Gameplay __


class Bullet(Cube):
    def __init__(self, pos, color):
        super(Cube, self).__init__()
        self.pos = pos
        self.color = color
        self.life = 10

    def draw(self, surface):
        length = self.width // self.rows
        pygame.draw.rect(
            surface,
            self.color,
            (self.pos.row * length + 1,
             self.pos.col * length + 1,
             length - 2,
             length - 2),
        )

    def move(self, surface):
        self.life -= 1
        self.pos = Location(self.pos.row + 0.5, self.pos.col + 0.5)
        self.draw(surface)


def manhattan_distance(goal: Location) -> Callable[[Location], float]:
    def distance(ml: Location) -> float:
        xdist: int = abs(ml.col - goal.col)
        ydist: int = abs(ml.row - goal.row)
        return xdist + ydist

    return distance


def main():
    tick_time = 10
    size = (500, 500)  # can't change this yet without creating an issue with the board scale
    cell_size = 10
    Cube.rows = size[0] // cell_size
    background_colour = (20, 20, 20)

    # instantiate the rendering object (surface), BG colour, and title
    screen = pygame.display.set_mode(size)
    screen.fill(background_colour)
    pygame.display.set_caption("Maze Game")
    clock = pygame.time.Clock()

    # Create Maze
    maze = Maze(size, cell_size)

    distance = manhattan_distance(maze.goal)

    maze.zombies.append(Zombie(maze.start, Colour.ZOMBIE))

    solution = pathfinding.astar(maze.start, maze.goal_test, maze.successors, distance)
    cached_path = pathfinding.node_to_path(solution) if solution is not None else []

    # Game Loop
    running = True  # len(cached_path) > 0
    current = None

    while running:
        screen.fill(background_colour)
        maze.draw_grid(screen)
        maze.draw_cells(screen)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

        # Check for a left mouse click down
        mouse_pressed = pygame.mouse.get_pressed()
        if mouse_pressed == (1, 0, 0):
            (x, y) = pygame.mouse.get_pos()
            maze.click_create_tower(x, y)

        clock.tick(tick_time)  # 30 would be real time - slower < 30 > faster

        _temp = current
        if _temp is not None and maze.cells[_temp.row][_temp.col].color != Colour.BLOCKED:
            maze.cells[_temp.row][_temp.col].color = Colour.EMPTY

        current = cached_path.pop(0)

        if maze.cells[current.row][current.col].color == Colour.EMPTY:
            maze.cells[current.row][current.col].color = Colour.ZOMBIE

        elif maze.cells[current.row][current.col].color != Colour.EMPTY:
            # need to invalidate the cache and start again
            if _temp is not None:
                # maze.cells[_temp.row][_temp.col].color = Colour.PATH
                maze.cells[current.row][current.col].color = Colour.BLOCKED
                solution = pathfinding.astar(_temp, maze.goal_test, maze.successors, distance)
            else:
                solution = pathfinding.astar(current, maze.goal_test, maze.successors, distance)

            if solution is None:
                print("No solution found using A*!")
                break
            else:
                # print("Problem: Recalculating!")
                cached_path = pathfinding.node_to_path(solution)

        maze.draw_cells(screen)
        pygame.display.update()


if __name__ == "__main__":
    main()
