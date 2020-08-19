#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
PyTetris: Python version of Tetris

MIT License

Copyright (c) 2020 William Lee

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from collections import namedtuple
from typing import Optional, Tuple

import pygame

ROWS = 22
COLUMNS = 10
SQUARE_SIZE = 30
LINE_WIDTH = 1

# Padding around the grid, as the number of squares,
# left and right, and up and down respectively
PADDING = (3, 4)

Dimensions = namedtuple("Dimensions", "width height")
Position = namedtuple("Position", "x y")

DISPLAY_SIZE = Dimensions(
    *((v + 2 * pad) * SQUARE_SIZE for v, pad in zip((COLUMNS, ROWS), PADDING))
)
GRID_SIZE = Dimensions(COLUMNS * SQUARE_SIZE, ROWS * SQUARE_SIZE)
GRID_POS = Position(*(pad * SQUARE_SIZE for pad in PADDING))

WHITE = 3 * (255,)
BLACK = 3 * (0,)
GREY = 3 * (127,)


class GridSquare:
    """
    Represents a square on the Tetris grid
    """
    def __init__(self, x: int, y: int, color: Optional[Tuple[int, int, int]] = None):
        self.x = x
        self.y = y
        self.color = color

    def draw(self, surface):
        pygame.draw.rect(
            surface,
            GREY,
            (self.x * SQUARE_SIZE, self.y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE,),
            LINE_WIDTH,
        )
        if self.color is not None:
            pygame.draw.rect(
                surface,
                self.color,
                (self.x * SQUARE_SIZE, self.y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE,),
            )


class Tetris:
    """
    Represents a game of Tetris
    """

    def __init__(self):
        self.grid = [[GridSquare(x, y) for x in range(COLUMNS)] for y in range(ROWS)]

    def draw_grid(self):
        grid_surface = pygame.Surface(GRID_SIZE)
        for row in self.grid:
            for square in row:
                square.draw(grid_surface)

        self.display.blit(grid_surface, GRID_POS)

    def render(self):
        self.display.fill(WHITE)
        self.draw_grid()

    def run(self):
        pygame.init()
        self.display = pygame.display.set_mode(DISPLAY_SIZE)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
            if running:
                self.render()
                pygame.display.update()

        pygame.quit()


def main():
    game = Tetris()
    game.run()


if __name__ == "__main__":
    main()
