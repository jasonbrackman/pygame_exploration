"""
Looking at exploring Pygame library with regards to:
- creating a surface,
- creating basic shapes,
- moving shapes around,
- 'updating/flipping' the screen,


Used the following resources:
-- The videos are OK, but I would not recommend this for people new to
programming, it does raise a lot of questions about how Pygame works and
it got me to start investigating things.
https://techwithtim.net/tutorials/game-development-with-python/snake-pygame/tutorial-1/

"""


import pygame


class Cube:
    rows = 20
    width = 500

    def __init__(self, start, dirnx=1, dirny=0, color=(255, 0, 0)):
        self.pos = start
        self.dirnx = dirnx
        self.dirny = dirny
        self.color = color

    def move(self, dirnx, dirny):
        self.dirnx = dirnx
        self.dirny = dirny
        self.pos = (self.pos[0] + self.dirnx, self.pos[1] + self.dirny)

    def draw(self, surface, eyes=False):
        length = self.width // self.rows
        row, col = self.pos
        pygame.draw.rect(surface,
                         self.color,
                         (row * length+1,
                          col * length+1,
                          length - 2,
                          length - 2))


class Snake:
    body = []
    turns = dict()

    def __init__(self, color, pos):
        self.color = color
        self.head = Cube(pos)
        self.body.append(self.head)
        self.dirnx = 0
        self.dirny = 1

    def move(self, event):

        choices = {
            pygame.K_LEFT: (-1, 0),
            pygame.K_RIGHT: (1, 0),
            pygame.K_UP: (0, -1),
            pygame.K_DOWN: (0, 1),
        }
        
        pos = event.dict.get("key", None) if event.type == pygame.KEYDOWN else None
        pos = choices.get(pos, None)
        if pos is not None:
            self.turns[self.head.pos[:]] = pos

            for i, cube in enumerate(self.body):
                position = cube.pos[:]
                if position in self.turns:
                    turn = self.turns[position]
                    cube.move(turn[0], turn[1])

                    if i == len(self.body) - 1:
                        self.turns.pop(position)
                else:
                    # Ensure we don't hit the end of the world
                    if cube.dirnx == -1 and cube.pos[0] <= 0:
                        cube.pos = (cube.rows-1, cube.pos[1])

                    elif cube.dirnx == 1 and cube.pos[0] >= cube.rows-1:
                        cube.pos = (0, cube.pos[1])

                    elif cube.dirny == -1 and cube.pos[1] <= 0:
                        cube.pos = (cube.pos[0], 0)

                    elif cube.dirny == 1 and cube.pos[1] <= cube.rows-1:
                        cube.pos = (cube.pos[0], cube.rows-1)

                    else:
                        cube.move(cube.dirnx, cube.dirny)

    def reset(self, pos):
        ...

    def add_cube(self):
        tail = self.body[-1]

        # get direction of tail cube
        dx, dy = tail.dirnx, tail.dirny

        # Get old position -- and update it using the direction of movement
        new_pos = tail.pos
        new_pos[0] = 0 if dx == 0 else (new_pos[0] + -dx)
        new_pos[1] = 0 if dy == 0 else (new_pos[1] + -dy)

        # add one more cube to the snake body trailing behind the
        self.body.append(Cube(new_pos))

    def draw(self, surface):
        for index, cube in enumerate(self.body):
            if index == 0:
                cube.draw(surface, True)
            else:
                cube.draw(surface)


def draw_square_grid(surface, size: (int, int), rows: int) -> None:
    """
    Draw a generic grid based on the length/rows passed in.

    :param surface: Pygame screen
    :param size: defines the width/height of the screen
    :param rows: the number of divisions that will make up the rows/cols
    :return: None
    """

    length = size[0]

    gap = length // rows
    x, y = 0, 0

    for r in range(rows):
        x += gap
        y += gap
        pygame.draw.line(surface, (255, 255, 255), (x, 0), (y, length))
        pygame.draw.line(surface, (255, 255, 255), (0, x), (length, y))


def main():

    size = (500, 500)
    background_colour = (20, 20, 20)

    # instantiate the rendering object (surface), BG colour, and title
    screen = pygame.display.set_mode(size)
    screen.fill(background_colour)
    pygame.display.set_caption('Snake Game')

    # Create initial board
    draw_square_grid(screen, size, 20)

    # Create a snake character
    snake = Snake((240, 0, 0), (0, 0))

    # Game Loop
    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                snake.move(event)
                snake.draw(screen)
                # pygame.display.flip()  # updates the entire surface
                pygame.display.update()  # updates the entire surface (Or rect area passed in)


if __name__ == "__main__":
    main()
