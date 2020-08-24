#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pytetris.locals.game

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

from enum import Enum
from collections import defaultdict

import pygame


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


class Movement(Enum):
    GRAVITY = 0
    SOFT_DROP = 1
    HARD_DROP = 2
    LEFT = 3
    RIGHT = 4
    ROT_C = 5
    ROT_AC = 6


# The length of time before a shape locks
LOCK_DELAY = 500
NEW_BLOCK_DELAY = 200

# The number of lines to clear per level
LINE_GOAL_MULTIPLIER = 5

ADJUSTED_LINE_SCORE = defaultdict(lambda: 0, {1: 1, 2: 3, 3: 5, 4: 8})

# Number of preview pieces
PREVIEW_NUM = 3

# Text font
pygame.font.init()
FONT = pygame.font.SysFont("Arial", 20)

# Key repeat values
KEY_REPEATS = {
    pygame.K_LEFT: (170, 50),
    pygame.K_RIGHT: (170, 50),
    pygame.K_DOWN: (0, 50),
}

# Wall kick definitions
# fmt: off
JLSTZ_WALL_KICKS = {
    0: {
        1: [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
        3: [(1, 0), (1, -1), (0, 2), (1, 2)],
    },
    1: {
        0: [(1, 0), (1, 1), (0, -2), (1, -2)],
        2: [(1, 0), (1, 1), (0, -2), (1, -2)],
    },
    2: {
        1: [(-1, 0), (-1, -1), (0, 2), (-1, 2)],
        3: [(1, 0), (1, -1), (0, 2), (1, 2)],
    },
    3: {
        2: [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
        0: [(-1, 0), (-1, 1), (0, -2), (-1, -2)],
    },
}


I_WALL_KICKS = {
    0: {
        1: [(-2, 0), (1, 0), (-2, -1), (1, -2)],
        3: [(-1, 0), (2, 0), (-1, -2), (2, 1)],
    },
    1: {
        0: [(2, 0), (-1, 0), (2, -1), (-1, 2)],
        2: [(-1, 0), (2, 0), (-1, -2), (2, 1)],
    },
    2: {
        1: [(1, 0), (-2, 0), (1, 2), (-2, -1)],
        3: [(2, 0), (-1, 0), (2, -1), (-1, 2)],
    },
    3: {
        2: [(1, 0), (1, 0), (-2, 1), (1, -2)],
        0: [(1, 0), (-2, 0), (1, 2), (-2, -1)],
    },
}

# fmt: on
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

# T-Block pointing side corner blocks for T-Spins
T_BLOCK_POINTING_CORNERS = {
    0: [(0, 0), (2, 0)],
    1: [(2, 0), (2, 2)],
    2: [(2, 2), (0, 2)],
    3: [(0, 2), (0, 0)],
}

# Block behind the center piece on T-Block
T_BLOCK_BEHIND_BLOCK = {
    0: (1, 2),
    1: (0, 1),
    2: (1, 0),
    3: (2, 1),
}

TST_WALL_KICKS = (1, 3)  # Wall kicks that determine if a TST has occurred
TST_ROTATIONS = (3, 0, 1)  # For clockwise direction, reverse for anticlockwise

ROTATION_MOVEMENTS = (Movement.ROT_AC, Movement.ROT_C)

KEY_TO_MOVE = {
    pygame.K_DOWN: Movement.SOFT_DROP,
    pygame.K_SPACE: Movement.HARD_DROP,
    pygame.K_LEFT: Movement.LEFT,
    pygame.K_RIGHT: Movement.RIGHT,
    pygame.K_z: Movement.ROT_C,
    pygame.K_UP: Movement.ROT_AC,
}
