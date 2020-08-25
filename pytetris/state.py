#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pytetris.state

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
from typing import List, Optional, Tuple

from .locals.color import COLORS
from .locals.game import (
    ADJUSTED_LINE_SCORE,
    BLOCKS,
    LINE_GOAL_MULTIPLIER,
    LOCK_DELAY,
    NEW_BLOCK_DELAY,
    ROTATION_MOVEMENTS,
    T_BLOCK_BEHIND_BLOCK,
    T_BLOCK_POINTING_CORNERS,
    TST_ROTATIONS,
    TST_WALL_KICKS,
    WALL_KICKS,
    BlockType,
    Movement,
)
from .locals.size import COLUMNS, ROWS, SPAWN_POS
from .locals.types import Color


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

    def _rotate(
        self, amount: int, *, test_rotation: bool = True
    ) -> Tuple[bool, Optional[int], Optional[int], Optional[int]]:
        # Rotates a shape by a certain amount
        # Rotations as multiples of 90 degrees clockwise, so a rotation of 1
        # is 90 degrees clockwise, -1 is 90 degrees anticlockwise
        if self.block_type == BlockType.OBlock:
            return True, 0, 0, None
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
                for i, (dx, dy) in enumerate(wall_kicks):
                    if self.can_move(dx=dx, dy=dy):
                        self._move(dx=dx, dy=dy, test_move=False)
                        return True, old_rotation, self.rotation, i

            self._rotate(-amount)  # Undoes the rotation
            if was_placed:
                self.place()
            return False, None, None, None
        if was_placed:
            self.place()
        return True, old_rotation, self.rotation, None

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


class MovementEntry:
    """
    Represents a movement made
    """

    def __init__(self, movement: Movement, **attrs):
        self.movement = movement
        self.__dict__.update(attrs)

    def __repr__(self):
        return "{0.__name__}({1})".format(
            type(self),
            ", ".join(
                f"{k}={v!r}" if isinstance(v, str) else f"{k}={v}"
                for k, v in self.__dict__.items()
            ),
        )


class TetrisState:
    """
    Represents the state of the game
    """

    def __init__(self):
        self.grid = [[None for x in range(COLUMNS)] for y in range(ROWS)]
        self.fall_interval = 1000
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
        self.move_log = []

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
        while self.current_line_count >= self.level * LINE_GOAL_MULTIPLIER:
            self.current_line_count -= self.level * LINE_GOAL_MULTIPLIER
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

        return True if lines else False

    def _soft_drop(self):
        if self.block.move_down():
            self._increase_score(soft_drop_cells=1)
            self.block_fall = False
            return True
        return False

    def _do_move(self, movement: Movement):
        moves = {
            Movement.SOFT_DROP: self._soft_drop,
            Movement.HARD_DROP: self._hard_drop,
            Movement.GRAVITY: self.block.move_down,
            Movement.LEFT: self.block.move_left,
            Movement.RIGHT: self.block.move_right,
            Movement.ROT_C: self.block.rotate_clockwise,
            Movement.ROT_AC: self.block.rotate_anticlockwise,
        }
        success = moves[movement]()
        if movement in (Movement.ROT_C, Movement.ROT_AC):
            success, old_rotation, new_rotation, wall_kick = success
        if success:
            log_entry = MovementEntry(movement)
            if movement in (
                Movement.LEFT,
                Movement.RIGHT,
                Movement.ROT_AC,
                Movement.ROT_C,
            ):
                self.lock_timer = 0
                if movement in (Movement.ROT_AC, Movement.ROT_C):
                    log_entry.old_rotation = old_rotation
                    log_entry.new_rotation = new_rotation
                    log_entry.wall_kick = wall_kick
            self.move_log.append(log_entry)
            if movement == Movement.HARD_DROP:
                self._on_lock()

    @staticmethod
    def _generate_tetrominoes():  # Implements the Random Generator
        tetrominoes = list(BlockType)
        random.shuffle(tetrominoes)
        return tetrominoes

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

    def _determine_t_spin(self) -> Optional[bool]:
        # Returns None if no T-Spin, True for a full T-spin, False for a Mini
        if (
            self.block.block_type == BlockType.TBlock
            and self.move_log[-1].movement in ROTATION_MOVEMENTS
        ):
            corners = []
            for x, y in ((0, 0), (0, 2), (2, 0), (2, 2)):
                grid_x = x + self.block.x
                grid_y = y + self.block.y
                if (
                    grid_x < COLUMNS
                    and grid_y < ROWS
                    and self.grid[grid_y][grid_x] is not None
                ):
                    corners.append((x, y))
            if len(corners) >= 3:  # 4 is possible with the TST twist
                # If one of the corners next to the pointing side
                # is not occupied, then the T-Spin is a Mini
                full_spin = True
                if any(
                    pos not in corners
                    for pos in T_BLOCK_POINTING_CORNERS[self.block.rotation]
                ):
                    full_spin = False
                else:
                    # If the block behind the centerpiece of the T-Block is empty,
                    # and the two blocks either side of the empty block are filled,
                    # (forming a hole) it is also a T-Spin Mini.
                    x, y = (
                        x1 + x2
                        for x1, x2 in zip(
                            (self.block.x, self.block.y),
                            T_BLOCK_BEHIND_BLOCK[self.block.rotation],
                        )
                    )
                    if (
                        not full_spin
                        and len(corners) == 3
                        and self.grid[y][x] is None
                        and all(
                            pos in T_BLOCK_POINTING_CORNERS[self.block.rotation]
                            for pos in corners
                        )
                    ):
                        full_spin = False
                if not full_spin:
                    # T-Spin mini is upgraded to a standard T-Spin
                    # if a TST twist is executed
                    rotation = None
                    for i, entry in enumerate(self.move_log[-2:]):
                        if entry.movement not in (Movement.ROT_AC, Movement.ROT_C) or (
                            rotation is not None and entry.movement != rotation
                        ):
                            break
                        rotation = entry.movement
                        expected_transition = (
                            TST_ROTATIONS
                            if entry.movement == Movement.ROT_C
                            else tuple(reversed(TST_ROTATIONS))
                        )[i : i + 2]
                        actual_transition = (entry.old_rotation, entry.new_rotation)
                        if not (
                            entry.wall_kick == TST_WALL_KICKS[i]
                            and actual_transition == expected_transition
                        ):
                            break
                    else:
                        full_spin = True
                return full_spin
        return None

    def _on_lock(self):
        self._determine_t_spin()
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

    def _update_time(self, millis: int):
        if self.new_block and self.new_block_timer >= NEW_BLOCK_DELAY:
            self._new_block()
            self.new_block = False
            self.block_held = False
            self.new_block_timer = 0
            if self.block is None:
                self.game_over = True

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
