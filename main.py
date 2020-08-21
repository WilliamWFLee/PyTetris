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

import random
from collections import namedtuple
from enum import Enum
from typing import List, Optional

import pygame

# Various game dimensions
VISIBLE_ROWS = 20
ROWS = 40
COLUMNS = 10
SQUARE_SIZE = 30
LINE_WIDTH = 1

# The length of time before a shape locks
LOCK_DELAY = 500

# Padding around the grid, as the number of squares,
# left and right, and up and down respectively
PADDING = (3, 4)

# Named tuples to make things easier to read
Dimensions = namedtuple("Dimensions", "width height")
Position = namedtuple("Position", "x y")

# The size of the display surface
DISPLAY_SIZE = Dimensions(
    *((v + 2 * pad) * SQUARE_SIZE for v, pad in zip((COLUMNS, VISIBLE_ROWS), PADDING))
)
# The size of the playfield
PLAYFIELD_SIZE = Dimensions(COLUMNS * SQUARE_SIZE, ROWS * SQUARE_SIZE)
# The visible size of the playfield
VISIBLE_PLAYFIELD_SIZE = Dimensions(COLUMNS * SQUARE_SIZE, VISIBLE_ROWS * SQUARE_SIZE)
# The position of the playfield relative to the display surface
GRID_POS = Position(*(pad * SQUARE_SIZE for pad in PADDING))
# The position that new tetrominoes appear
SPAWN_POS = Position(3, 19)

# Color tuples
WHITE = 3 * (255,)
BLACK = 3 * (0,)
GREY = 3 * (127,)

# Colors of the tetrominoes
COLORS = tuple(
    pygame.Color(color)
    for color in ("cyan", "yellow", "purple", "green", "red", "blue", "orange")
)


class BlockType(Enum):
    """
    Enumeration of the block types
    """

    IBlock = 0
    JBlock = 1
    LBlock = 2
    OBlock = 3
    SBlock = 4
    TBlock = 5
    ZBlock = 6


# Wall kick definitions
JLSTZ_WALL_KICKS = {
    0: {
        1: [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
        3: [(1, 0), (1, 1), (0, -2), (1, -2)],
    },
    1: {  # fmt: off
        0: [(1, 0), (1, -1), (0, 2), (1, 2)],
        2: [(1, 0), (1, -1), (0, 2), (1, 2)],
    },  # fmt: on
    2: {
        1: [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
        3: [(1, 0), (1, 1), (0, -2), (1, -2)],
    },
    3: {
        2: [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
        0: [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
    },
}


I_WALL_KICKS = {
    0: {  # fmt: off
        1: [(-2, 0), (1, 0), (-2, 1), (1, 2)],
        3: [(-1, 0), (2, 0), (-1, 2), (2, -1)],
    },  # fmt: on
    1: {
        0: [(2, 0), (-1, 0), (2, 1), (-1, -2)],
        2: [(-1, 0), (2, 0), (-1, 2), (2, -1)],
    },
    2: {
        1: [(1, 0), (-2, 0), (1, -2), (-2, 1)],
        3: [(2, 0), (-1, 0), (2, 1), (-1, -2)],
    },
    3: {  # fmt: off
        2: [(1, 0), (1, 0), (-2, -1), (1, 2)],
        0: [(1, 0), (-2, 0), (1, -2), (-2, 1)],
    },  # fmt: on
}


WALL_KICKS = {
    BlockType.JBlock: JLSTZ_WALL_KICKS,
    BlockType.LBlock: JLSTZ_WALL_KICKS,
    BlockType.JBlock: JLSTZ_WALL_KICKS,
    BlockType.TBlock: JLSTZ_WALL_KICKS,
    BlockType.ZBlock: JLSTZ_WALL_KICKS,
    BlockType.IBlock: I_WALL_KICKS,
}

# Tetromino definitions
# fmt: off
BLOCKS = {
    BlockType.IBlock: ["    ",
                       "....",
                       "    ",
                       "    "],
    BlockType.JBlock: [".  ",
                       "...",
                       "   "],
    BlockType.LBlock: ["  .",
                       "...",
                       "   "],
    BlockType.OBlock: [" .. ",
                       " .. ",
                       "    "],
    BlockType.SBlock: [" ..",
                       ".. ",
                       "   "],
    BlockType.TBlock: [" . ",
                       "...",
                       "   "],
    BlockType.ZBlock: [".. ",
                       " ..",
                       "   "],
}
# fmt: on


class Tetromino:
    """
    Represents a Tetris tetromino
    """

    def __init__(self, x: int, y: int, block_type: BlockType, grid: List[List[int]]):
        self.x = x
        self.y = y
        self.block_type = block_type
        self.block = BLOCKS[block_type][:]
        self.grid = grid
        self.rotation = 0
        self.placed = False

    def _can_place(self) -> bool:
        return self.can_move(dx=0, dy=0)

    def place(self, *, test_place: bool = True) -> Optional[bool]:
        """
        Places the tetromino on the playing field

        :param test_place: Whether to test the placement, defaults to True
        :type test_place: bool
        :return: Whether the placement was successful, if test_place is True
        :rtype: Optional[bool]
        """
        if self.placed:
            return True
        if test_place and not self._can_place():
            return False
        for y, row in enumerate(self.block):
            for x, square in enumerate(row):
                if (
                    square == "."
                    and 0 <= self.x + x < COLUMNS
                    and 0 <= self.y + y < ROWS
                ):
                    self.grid[self.y + y][self.x + x] = self.block_type.value + 1

        self.placed = True
        return True if test_place else None

    def remove(self):
        # Removes this shape from the grid
        if not self.placed:
            return
        for y, row in enumerate(self.block):
            for x, square in enumerate(row):
                if (
                    square == "."
                    and 0 <= self.x + x < COLUMNS
                    and 0 <= self.y + y < ROWS
                ):
                    self.grid[self.y + y][self.x + x] = 0
        self.placed = False

    def can_move(self, dx: int, dy: int) -> bool:
        # Determines whether this shape can move in a given direction
        can_move = False
        was_placed = self.placed
        self.remove()
        for y, row in enumerate(self.block):
            for x, square in enumerate(row):
                if not square == ".":
                    continue
                new_x = self.x + x + dx
                new_y = self.y + y + dy
                if (
                    not 0 <= new_x < COLUMNS
                    or not 0 <= new_y < ROWS
                    or self.grid[new_y][new_x] != 0
                ):
                    break
            else:
                continue
            break
        else:
            can_move = True
        if was_placed:
            self.place(test_place=False)
        return can_move

    def _move(self, dx: int = 0, dy: int = 0, test_move: bool = True) -> Optional[bool]:
        # Moves the block to the specified location
        # Returns if the operation succeeded, if test_move is True, otherwise None
        if test_move:
            can_move = self.can_move(dx=dx, dy=dy)
        self.remove()
        if not test_move or can_move:
            self.x += dx
            self.y += dy
        self.place()

        return can_move if test_move else None

    def _rotate(self, amount: int) -> bool:
        # Rotates a shape by a certain amount
        # Rotations as multiples of 90 degrees clockwise, so a rotation of 1
        # is 90 degrees clockwise, -1 is 90 degrees anticlockwise
        if self.block_type == BlockType.OBlock:
            return True
        self.remove()
        amount %= 4
        old_rotation = self.rotation
        self.rotation = (self.rotation + amount) % 4
        for _ in range(amount):
            self.block = [
                "".join(self.block[y][x] for y in range(len(self.block) - 1, -1, -1))
                for x in range(len(self.block[0]))
            ]

        if not self._can_place():  # Normal rotation cannot be performed
            try:
                wall_kicks = WALL_KICKS[self.block_type][old_rotation][self.rotation]
            except KeyError:
                pass
            else:
                for dx, dy in wall_kicks:
                    if self.can_move(dx=dx, dy=dy):
                        self._move(dx=dx, dy=dy, test_move=False)
                        return True

            self._rotate(-amount)  # Undoes the rotation
            self.place()
            return False
        self.place()
        return True

    def move_down(self, *, test_move: bool = True) -> bool:
        """
        Moves the tetromino down one block

        :param test_move: Whether to test the move, defaults to True
        :type test_move: bool
        :return: Whether the move was successful
        :rtype: bool
        """
        return self._move(dy=1, test_move=test_move)

    def move_left(self) -> bool:
        """
        Moves the tetromino left one block

        :return: Whether the move was successful
        :rtype: bool
        """
        return self._move(dx=-1)

    def move_right(self) -> bool:
        """
        Moves the tetromino right one block

        :return: Whether the move was successful
        :rtype: bool
        """
        return self._move(dx=1)

    def rotate_clockwise(self) -> bool:
        """
        Rotates the tetromino clockwise

        :return: Whether the rotation was successful
        :rtype: bool
        """
        return self._rotate(1)

    def rotate_anticlockwise(self) -> bool:
        """
        Rotates the tetromino anticlockwise

        :return: Whether the rotation was successful
        :rtype: bool
        """
        return self._rotate(-1)


class Tetris:
    """
    Represents a game of Tetris
    """

    def __init__(self):
        self.grid = [[0 for x in range(COLUMNS)] for y in range(ROWS)]

    def _clear_lines(self) -> int:
        count = 0
        for y, row in enumerate(self.grid):
            if all(square != 0 for square in row):
                self.grid = (
                    [[0 for _ in range(COLUMNS)]] + self.grid[:y] + self.grid[y + 1 :]
                )
                count += 1
        return count

    def _hard_drop(self):
        while self.block.move_down():
            pass

    @staticmethod
    def _generate_tetrominoes():  # Implements the Random Generator
        tetrominoes = list(BlockType)
        random.shuffle(tetrominoes)
        return tetrominoes

    def _draw_grid(self):
        # Draws the grid and the squares on the board
        grid_surface = pygame.Surface(VISIBLE_PLAYFIELD_SIZE)
        for y, row in enumerate(self.grid[-VISIBLE_ROWS:]):
            for x, square in enumerate(row):
                if square:
                    pygame.draw.rect(
                        grid_surface,
                        COLORS[square - 1],
                        (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE,),
                    )
                pygame.draw.rect(
                    grid_surface,
                    GREY,
                    (x * SQUARE_SIZE, y * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE,),
                    LINE_WIDTH,
                )

        self.display.blit(grid_surface, GRID_POS)

    def _new_block(self, block_type: Optional[BlockType] = None) -> bool:
        if block_type is None:
            if not self.next_tetrominoes:
                self.next_tetrominoes = self._generate_tetrominoes()
            block_type = self.next_tetrominoes.pop()
        self.block = Tetromino(*SPAWN_POS, block_type, self.grid)
        if not self.block.place():
            self.block = None
        else:
            self.block.move_down()
        self.fall_timer = 0
        self.block_fall = False

    def _hold_block(self):
        if self.block_held:
            return
        self.block.remove()
        if self.hold_block_type is None:
            self.hold_block_type = self.block.block_type
            self._new_block()
        else:
            old_block_type = self.block.block_type
            self._new_block(self.hold_block_type)
            self.hold_block_type = old_block_type
        self.block_held = True

    def _run_game(self):
        if self.new_block:
            self._clear_lines()
            self._new_block()
            self.new_block = False
            self.block_held = False

        if not self.block:
            return

        millis = self.clock.tick()
        if not self.block_fall:
            self.fall_timer += millis
        if self.lock_started:
            self.lock_delay += millis
        if self.fall_timer >= self.fall_interval:
            self.block_fall = True
            self.fall_timer %= self.fall_interval
        if self.block.can_move(dx=0, dy=1):
            self.lock_started = False
            self.lock_delay = 0
            if self.block_fall:
                self.block.move_down(test_move=False)
            self.block_fall = False
        else:
            self.lock_started = True
        if self.lock_delay >= LOCK_DELAY:
            moved = self.block.move_down()
            self.new_block = not moved
            self.lock_delay = 0

    def render(self):
        self.display.fill(WHITE)
        self._draw_grid()

    def run(self):
        pygame.init()
        self.display = pygame.display.set_mode(DISPLAY_SIZE)

        pygame.key.set_repeat(170, 50)

        running = True

        self.fall_interval = 1000
        self.clock = pygame.time.Clock()
        self.fall_timer = 0
        self.lock_delay = 0
        self.lock_started = False
        self.block_fall = False
        self.new_block = True
        self.hold_block_type = None
        self.block_held = False  # Indicates whether a block has been held this turn
        self.block = None
        self.game_over = False

        self.next_tetrominoes = []
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                elif self.block is None:
                    continue
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        self.block_fall = True
                    elif event.key == pygame.K_SPACE:
                        self._hard_drop()
                    elif event.key == pygame.K_c:
                        self._hold_block()
                    else:
                        moves = {
                            pygame.K_LEFT: self.block.move_left,
                            pygame.K_RIGHT: self.block.move_right,
                            pygame.K_z: self.block.rotate_clockwise,
                            pygame.K_UP: self.block.rotate_anticlockwise,
                        }
                        if event.key in moves:
                            result = moves[event.key]()
                            if result:
                                self.lock_delay = 0
            if running:
                if not self.game_over:
                    self._run_game()

                self.render()
                pygame.display.update()

        pygame.quit()


def main():
    game = Tetris()
    game.run()


if __name__ == "__main__":
    main()
