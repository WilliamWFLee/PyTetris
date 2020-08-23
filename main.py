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
from collections import namedtuple, defaultdict
from enum import Enum
from typing import List, Optional, Tuple

import pygame

pygame.init()

# Various game dimensions
VISIBLE_ROWS = 20
ROWS = 40
COLUMNS = 10
SQUARE_WIDTH = 25
LINE_WIDTH = 1

# The length of time before a shape locks
LOCK_DELAY = 500
NEW_BLOCK_DELAY = 200


# Named tuples to make things easier to read
class Dimensions(namedtuple("Dimensions", "width height pwidth pheight")):  # noqa
    """
    Class for representing on-screen dimensions in units of grid square width

    .. attribute:: width

        The width in terms of grid squares

        :type: int

    .. attribute:: height

        The height in terms of grid squares

        :type: int

    .. attribute:: pwidth

        The width in terms of pixels

        :type: int

    .. attribute:: pheight

        The height in terms of pixels

        :type: int
    """

    def __new__(cls, *args, **kwargs):
        """
        Creates a new dimension specification

        You should specify the width and height in units of grid square width.
        These are automatically multiplied to give the width and height
        in terms of pixels.

        For example, where `SQUARE_WIDTH` equals 25,
        >>> Dimensions(2, 4)
        Dimensions(width=2, height=4, pwidth=50, pheight=100)
        """
        args = list(args) + [arg * SQUARE_WIDTH for arg in args]
        kwargs.update({f"p{k}": v * SQUARE_WIDTH for k, v in kwargs.items()})
        return super().__new__(cls, *args, **kwargs)

    @property
    def in_pixels(self):
        return self.pwidth, self.pheight

    @property
    def in_squares(self):
        return self.width, self.height


Position = namedtuple("Position", "x y")

# Padding around the grid, as the number of squares,
# left and right, and up and down respectively
PADDING = Dimensions(12, 4)

# Size of grid boxes - hold box and next piece preview
GRID_BOX_SIZE = Dimensions(6, 6)

# The size of the display surface
DISPLAY_SIZE = Dimensions(
    COLUMNS + 2 * PADDING.width, VISIBLE_ROWS + 2 * PADDING.height
)
# The size of the playfield
PLAYFIELD_SIZE = Dimensions(COLUMNS, ROWS)
# The visible size of the playfield
VISIBLE_PLAYFIELD_SIZE = Dimensions(COLUMNS, VISIBLE_ROWS)
# Size of text area at the bottom
TEXT_AREA = Dimensions(COLUMNS, PADDING.height)
# The position of the playfield relative to the display surface
GRID_POS = Position(*PADDING.in_pixels)
# The position that new tetrominoes appear
SPAWN_POS = Position(3, 19)

# Color tuples
WHITE = 3 * (255,)
BLACK = 3 * (0,)
GREY = 3 * (127,)

# The number of lines to clear per level
LINE_GOAL_MULTIPILER = 5

ADJUSTED_LINE_SCORE = defaultdict(lambda: 0, {1: 1, 2: 3, 3: 5, 4: 8})

# Number of preview pieces
PREVIEW_NUM = 3

# Text font
FONT = pygame.font.SysFont("Arial", 20)

# Key repeat values
KEY_REPEATS = {
    pygame.K_LEFT: (170, 50),
    pygame.K_RIGHT: (170, 50),
    pygame.K_DOWN: (0, 50),
}


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


COLORS = {
    BlockType.IBlock: (0, 255, 255),
    BlockType.JBlock: (0, 0, 255),
    BlockType.LBlock: (255, 165, 0),
    BlockType.OBlock: (255, 255, 0),
    BlockType.SBlock: (0, 255, 0),
    BlockType.TBlock: (160, 32, 240),
    BlockType.ZBlock: (255, 0, 0),
}


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
Color = Tuple[int, int, int]


class Movement(Enum):
    GRAVITY = 0
    SOFT_DROP = 1
    HARD_DROP = 2
    LEFT = 3
    RIGHT = 4
    ROT_C = 5
    ROT_AC = 6


class TetrominoBase:
    """
    Base class for tetrominoes
    """

    def __init__(
        self,
        x: int,
        y: int,
        block_type: BlockType,
        color: Color,
        grid: List[List[Color]],
    ):
        self.x = x
        self.y = y
        self.block_type = block_type
        self.block = BLOCKS[block_type][:]
        self.grid = grid
        self.rotation = 0
        self.color = color
        self.placed = False

    def _can_place(self) -> bool:
        return self.can_move(dx=0, dy=0)

    def place(
        self, *, test_place: bool = True, skip_non_empty: bool = False
    ) -> Optional[bool]:
        """
        Places the tetromino on the playing field

        :param test_place: Whether to test the placement, defaults to True
        :type test_place: bool
        :param skip_non_empty: Whether non-empty squares are skipped, defaults to False. Implies test_place is False.
        :type skip_non_empty: bool
        :return: Whether the placement was successful, if test_place is True
        :rtype: Optional[bool]
        """
        if self.placed:
            return True
        if skip_non_empty:
            test_place = False
        if test_place and not self._can_place():
            return False
        for y, row in enumerate(self.block):
            for x, square in enumerate(row):
                bx = self.x + x
                by = self.y + y
                if square == "." and 0 <= bx < COLUMNS and 0 <= by < ROWS:
                    if self.grid[by][bx] is None or (
                        self.grid[by][bx] is not None and not skip_non_empty
                    ):
                        self.grid[by][bx] = self.color

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
                    and self.grid[self.y + y][self.x + x] == self.color
                ):
                    self.grid[self.y + y][self.x + x] = None
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
                    or (
                        self.grid[new_y][new_x] is not None
                        and all(v >= 0 for v in self.grid[new_y][new_x])
                    )
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
        was_placed = self.placed
        self.remove()
        if not test_move or can_move:
            self.x += dx
            self.y += dy
        if was_placed:
            self.place()

        return can_move if test_move else None

    def _rotate(self, amount: int, *, test_rotation: bool = True) -> bool:
        # Rotates a shape by a certain amount
        # Rotations as multiples of 90 degrees clockwise, so a rotation of 1
        # is 90 degrees clockwise, -1 is 90 degrees anticlockwise
        if self.block_type == BlockType.OBlock:
            return True
        was_placed = self.placed
        if was_placed:
            self.remove()
        amount %= 4
        old_rotation = self.rotation
        self.rotation = (self.rotation + amount) % 4
        for _ in range(amount):
            self.block = [
                "".join(self.block[y][x] for y in range(len(self.block) - 1, -1, -1))
                for x in range(len(self.block[0]))
            ]

        if test_rotation and not self._can_place():
            # Normal rotation cannot be performed
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
            if was_placed:
                self.place()
            return False
        if was_placed:
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

    def hard_drop(self) -> int:
        lines = 0
        while True:
            if not self._move(dy=1):
                break
            lines += 1
        return lines


class GhostPiece(TetrominoBase):
    """
    Represents the Ghost Piece of a tetromino
    """

    def __init__(
        self,
        x: int,
        y: int,
        block_type: BlockType,
        color: Color,
        grid: List[List[Color]],
        rotation: int = 0,
    ):
        color = tuple(-v for v in color)
        super().__init__(x, y, block_type, color, grid)
        self._rotate(rotation, test_rotation=False)
        self.hard_drop()

    def place(self, *args, **kwargs):
        return super().place(test_place=False, skip_non_empty=True)


class Tetromino(TetrominoBase):
    """
    Represents a Tetris tetromino
    """

    def __init__(self, x, y, block_type, color, grid):
        super().__init__(x, y, block_type, color, grid)
        self.ghost_piece = GhostPiece(x, y, block_type, color, grid)
        self.ghost_piece.place()

    def renew_ghost_piece(method):  # noqa
        def inner(self, *args, **kwargs):
            ret = method(self, *args, **kwargs)
            self.remove()
            self.ghost_piece.remove()
            self.ghost_piece = GhostPiece(
                self.x, self.y, self.block_type, self.color, self.grid, self.rotation
            )
            self.ghost_piece.place()
            self.place()

            return ret

        return inner

    @renew_ghost_piece
    def move_left(self) -> bool:
        """
        Moves the tetromino left one block

        :return: Whether the move was successful
        :rtype: bool
        """
        return self._move(dx=-1)

    @renew_ghost_piece
    def move_right(self) -> bool:
        """
        Moves the tetromino right one block

        :return: Whether the move was successful
        :rtype: bool
        """
        return self._move(dx=1)

    @renew_ghost_piece
    def rotate_clockwise(self) -> bool:
        """
        Rotates the tetromino clockwise

        :return: Whether the rotation was successful
        :rtype: bool
        """
        return self._rotate(1)

    @renew_ghost_piece
    def rotate_anticlockwise(self) -> bool:
        """
        Rotates the tetromino anticlockwise

        :return: Whether the rotation was successful
        :rtype: bool
        """
        return self._rotate(-1)

    @renew_ghost_piece
    def move_down(self, *, test_move: bool = True):
        return super().move_down(test_move=test_move)

    def delete(self):
        self.remove()
        self.ghost_piece.remove()


class Tetris:
    """
    Represents a game of Tetris
    """

    def _clear_lines(self) -> int:
        count = 0
        for y, row in enumerate(self.grid):
            if all(square is not None for square in row):
                self.grid = (
                    [[None for _ in range(COLUMNS)]]
                    + self.grid[:y]
                    + self.grid[y + 1 :]
                )
                count += 1
        return count

    def _calculate_level(self, lines: int):
        if not lines:
            return
        self.current_line_count += ADJUSTED_LINE_SCORE[lines]
        while self.current_line_count >= self.level * LINE_GOAL_MULTIPILER:
            self.current_line_count -= self.level * LINE_GOAL_MULTIPILER
            self.level += 1
        self.fall_interval = 1000 * (0.8 - 0.007 * (self.level - 1)) ** (self.level - 1)

    def _increase_score(
        self, *, lines: int = 0, soft_drop_cells: int = 0, hard_drop_cells: int = 0,
    ):
        self.score += (
            (100 * ADJUSTED_LINE_SCORE[lines]) * self.level
            + soft_drop_cells
            + 2 * hard_drop_cells
            + 50 * (self.combo - 1) * self.level
        )

    def _hard_drop(self):
        lines = self.block.hard_drop()
        self._increase_score(hard_drop_cells=lines)
        self.new_block = True
        self._on_lock()

    def _soft_drop(self):
        if self.block.move_down():
            self._increase_score(soft_drop_cells=1)
            self.block_fall = False

    def _do_move(self, movement: Movement):
        moves = {
            Movement.SOFT_DROP: self._soft_drop,
            Movement.HARD_DROP: self._hard_drop,
            Movement.SOFT_DROP: self.block.move_down,
            Movement.GRAVITY: self.block.move_down,
            Movement.LEFT: self.block.move_left,
            Movement.RIGHT: self.block.move_right,
            Movement.ROT_C: self.block.rotate_clockwise,
            Movement.ROT_AC: self.block.rotate_anticlockwise,
        }
        result = moves[movement]()
        if result and movement in (
            Movement.LEFT,
            Movement.RIGHT,
            Movement.ROT_C,
            Movement.ROT_AC,
        ):
            self.lock_timer = 0

    @staticmethod
    def _generate_tetrominoes():  # Implements the Random Generator
        tetrominoes = list(BlockType)
        random.shuffle(tetrominoes)
        return tetrominoes

    @staticmethod
    def _draw_grid_square(
        surface: pygame.Surface, color: Optional[Color], x: int, y: int
    ):
        x *= SQUARE_WIDTH
        y *= SQUARE_WIDTH
        if color is not None:
            if all(v <= 0 for v in color):
                color = tuple(-v // 2 for v in color)
            pygame.draw.rect(
                surface, color, (x, y, SQUARE_WIDTH, SQUARE_WIDTH),
            )
            pygame.draw.rect(
                surface, color, (x, y, SQUARE_WIDTH, SQUARE_WIDTH),
            )
        pygame.draw.rect(
            surface, GREY, (x, y, SQUARE_WIDTH, SQUARE_WIDTH), LINE_WIDTH,
        )

    def _draw_grid(self):
        # Draws the grid and the squares on the board
        grid_surface = pygame.Surface(VISIBLE_PLAYFIELD_SIZE.in_pixels)
        for y, row in enumerate(self.grid[-VISIBLE_ROWS:]):
            for x, color in enumerate(row):
                self._draw_grid_square(grid_surface, color, x, y)

        self.display.blit(grid_surface, GRID_POS)

    @classmethod
    def _draw_grid_box(cls, block_type: Optional[BlockType] = None):
        surface = pygame.Surface(GRID_BOX_SIZE.in_pixels)
        for y in range(GRID_BOX_SIZE.height):
            for x in range(GRID_BOX_SIZE.width):
                color = None
                if block_type is not None:
                    block = BLOCKS[block_type]
                    if (
                        0 <= y - 1 < len(block)
                        and 0 <= x - 1 < len(block[y - 1])
                        and block[y - 1][x - 1] == "."
                    ):
                        color = COLORS[block_type]
                cls._draw_grid_square(surface, color, x, y)
        return surface

    @staticmethod
    def _draw_grid_box_label(text: str):
        label_surface = pygame.Surface(
            (GRID_BOX_SIZE.pwidth, PADDING.pheight), pygame.SRCALPHA,
        )
        label = FONT.render(text, True, BLACK)
        label_x = (label_surface.get_width() - label.get_width()) // 2
        label_y = (label_surface.get_height() - label.get_height()) // 2

        label_surface.blit(label, (label_x, label_y))
        return label_surface

    def _draw_hold(self):
        # Draw the hold grid
        hold_x = (PADDING.pwidth - GRID_BOX_SIZE.pwidth) // 2
        hold_y = PADDING.pheight
        hold_surface = self._draw_grid_box(self.hold_block_type)
        self.display.blit(hold_surface, (hold_x, hold_y))

        # Draw the hold label
        hold_label_surface = self._draw_grid_box_label("Hold Box")
        self.display.blit(hold_label_surface, (hold_x, 0))

    def _draw_next_pieces(self):
        # Draw the grids
        preview_x = (
            PLAYFIELD_SIZE.pwidth
            + PADDING.pwidth
            + (PADDING.pwidth - GRID_BOX_SIZE.pwidth) // 2
        )
        preview_y = PADDING.pheight
        preview_surface = pygame.Surface(
            (GRID_BOX_SIZE.pwidth, GRID_BOX_SIZE.pheight * PREVIEW_NUM)
        )
        for y in range(PREVIEW_NUM):
            box_surface = self._draw_grid_box(self.next_tetrominoes[y])
            preview_surface.blit(box_surface, (0, GRID_BOX_SIZE.pheight * y))
        self.display.blit(preview_surface, (preview_x, preview_y))

        # Draw label
        preview_label_surface = self._draw_grid_box_label("Next Pieces")
        self.display.blit(preview_label_surface, (preview_x, 0))

    def _draw_stats(self):
        # Creates a text surface to blit to
        text_surface = pygame.Surface(TEXT_AREA.in_pixels, pygame.SRCALPHA)

        # Label for the stats
        texts = (f"Level: {self.level}", f"Score: {self.score}")

        # Width of each "cell"
        width = text_surface.get_width() // len(texts)
        height = text_surface.get_height()

        for i, label_text in enumerate(texts):
            text = FONT.render(label_text, True, BLACK)
            x = i * width + (width - text.get_width()) // 2
            y = (height - text.get_height()) // 2
            text_surface.blit(text, (x, y))

        self.display.blit(
            text_surface, (GRID_POS.x, GRID_POS.y + VISIBLE_PLAYFIELD_SIZE.pheight)
        )

    def _new_block(self, block_type: Optional[BlockType] = None):
        if block_type is None:
            if len(self.next_tetrominoes) < 7:
                self.next_tetrominoes += self._generate_tetrominoes()
            block_type = self.next_tetrominoes.pop(0)
        self.block = Tetromino(*SPAWN_POS, block_type, COLORS[block_type], self.grid)
        if not self.block.place():
            self.block = None
        else:
            self.block.move_down()
        self.fall_timer = 0
        self.block_fall = False

    def _hold_block(self):
        if self.block_held:
            return
        self.block.delete()
        if self.hold_block_type is None:
            self.hold_block_type = self.block.block_type
            self._new_block()
        else:
            old_block_type = self.block.block_type
            self._new_block(self.hold_block_type)
            self.hold_block_type = old_block_type
        self.block_held = True

    def _on_lock(self):
        lines = self._clear_lines()
        if lines:
            self._calculate_level(lines)
            self._increase_score(lines=lines)
            self.combo += 1
        else:
            self.combo = 1
        self.lock_timer = 0
        self.lock_started = False
        self.block = None

    def _run_game(self):
        # Returns whether to the game is still to run

        self.grid = [[None for x in range(COLUMNS)] for y in range(ROWS)]
        self.fall_interval = 1000
        self.clock = pygame.time.Clock()
        self.fall_timer = 0
        self.lock_timer = 0
        self.new_block_timer = NEW_BLOCK_DELAY
        self.lock_started = False
        self.block_fall = False
        self.new_block = True
        self.hold_block_type = None
        self.block_held = False  # Indicates whether a block has been held this turn
        self.block = None
        self.game_over = False
        self.next_tetrominoes = []
        self.level = 1
        self.current_line_count = 0
        self.score = 0
        self.paused = False
        self.combo = 1

        self.repeating_keys = set()
        self.key_repeats_timers = {k: 0 for k in KEY_REPEATS}

        game_over = False
        while not game_over:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYUP:
                    if event.key in self.repeating_keys:
                        self.repeating_keys.remove(event.key)
                        self.key_repeats_timers[event.key] = 0
                elif self.block is None:
                    continue
                if event.type == pygame.KEYDOWN:
                    if event.key in KEY_REPEATS and not getattr(event, "repeat", False):
                        self.repeating_keys.add(event.key)
                    if event.key == pygame.K_ESCAPE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_c:
                        self._hold_block()
                    else:
                        moves = {
                            pygame.K_DOWN: Movement.SOFT_DROP,
                            pygame.K_SPACE: Movement.HARD_DROP,
                            pygame.K_LEFT: Movement.LEFT,
                            pygame.K_RIGHT: Movement.RIGHT,
                            pygame.K_z: Movement.ROT_C,
                            pygame.K_UP: Movement.ROT_AC,
                        }
                        if event.key in moves:
                            self._do_move(moves[event.key])

            if self.paused:
                continue

            if self.new_block and self.new_block_timer >= NEW_BLOCK_DELAY:
                self._new_block()
                self.new_block = False
                self.block_held = False
                self.new_block_timer = 0
                if self.block is None:
                    game_over = True

            if game_over:
                break

            millis = self.clock.tick()
            for key in self.repeating_keys:
                self.key_repeats_timers[key] += millis
                delay, interval = KEY_REPEATS[key]
                while self.key_repeats_timers[key] - delay > interval:
                    pygame.event.post(
                        pygame.event.Event(pygame.KEYDOWN, key=key, repeat=True)
                    )
                    self.key_repeats_timers[key] -= interval
            if self.new_block:
                self.new_block_timer += millis
            if self.block:
                if not self.block_fall:
                    self.fall_timer += millis
                if self.lock_started:
                    self.lock_timer += millis
                if self.fall_timer >= self.fall_interval:
                    self.block_fall = True
                    self.fall_timer %= self.fall_interval
                if self.block.can_move(dx=0, dy=1):
                    self.lock_started = False
                    self.lock_timer = 0
                    if self.block_fall:
                        self.block.move_down(test_move=False)
                    self.block_fall = False
                else:
                    self.lock_started = True
                if self.lock_timer >= LOCK_DELAY:
                    moved = self.block.move_down()
                    self.new_block = not moved
                    if not moved:
                        self._on_lock()
            self.render()
            pygame.display.update()
        return True

    def _game_over(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    return True
        return False

    def render(self):
        self.display.fill(WHITE)
        self._draw_grid()
        self._draw_stats()
        self._draw_hold()
        self._draw_next_pieces()

    def run(self):
        self.display = pygame.display.set_mode(DISPLAY_SIZE.in_pixels)
        pygame.display.set_caption("PyTetris")

        while True:
            run = self._run_game()
            if not run:
                break
            restart = self._game_over()
            if not restart:
                break

        pygame.quit()


def main():
    game = Tetris()
    game.run()


if __name__ == "__main__":
    main()
