#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pytetris.game

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

from typing import Optional

import pygame

from .locals.color import BLACK, COLORS, GREY, WHITE
from .locals.game import (
    BLOCKS,
    FONT,
    KEY_REPEATS,
    KEY_TO_MOVE,
    PREVIEW_NUM,
    BlockType,
)
from .locals.size import (
    DISPLAY_SIZE,
    GRID_BOX_SIZE,
    GRID_POS,
    LINE_WIDTH,
    PADDING,
    PLAYFIELD_SIZE,
    SQUARE_WIDTH,
    TEXT_AREA,
    VISIBLE_PLAYFIELD_SIZE,
    VISIBLE_ROWS,
)
from .locals.types import Color
from .state import TetrisState

pygame.init()


class Tetris:
    """
    Represents a game of Tetris
    """

    def __init__(self):
        self.state = TetrisState()

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
        for y, row in enumerate(self.state.grid[-VISIBLE_ROWS:]):
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
        hold_surface = self._draw_grid_box(self.state.hold_block_type)
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
            box_surface = self._draw_grid_box(self.state.next_tetrominoes[y])
            preview_surface.blit(box_surface, (0, GRID_BOX_SIZE.pheight * y))
        self.display.blit(preview_surface, (preview_x, preview_y))

        # Draw label
        preview_label_surface = self._draw_grid_box_label("Next Pieces")
        self.display.blit(preview_label_surface, (preview_x, 0))

    def _draw_stats(self):
        # Creates a text surface to blit to
        text_surface = pygame.Surface(TEXT_AREA.in_pixels, pygame.SRCALPHA)

        # Label for the stats
        texts = (f"Level: {self.state.level}", f"Score: {self.state.score}")

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

    def _run_game(self):
        # Returns whether to the game is still to run

        self.clock = pygame.time.Clock()

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
                elif self.state.block is None:
                    continue
                if event.type == pygame.KEYDOWN:
                    if event.key in KEY_REPEATS and not getattr(event, "repeat", False):
                        self.repeating_keys.add(event.key)
                    if event.key == pygame.K_ESCAPE:
                        self.state.paused = not self.state.paused
                    elif event.key == pygame.K_c:
                        self.state._hold_block()
                    else:
                        if event.key in KEY_TO_MOVE:
                            self.state._do_move(KEY_TO_MOVE[event.key])

            if self.state.paused:
                continue

            if game_over:
                break

            millis = self.clock.tick()
            self.state._update_time(millis)

            for key in self.repeating_keys:
                self.key_repeats_timers[key] += millis
                delay, interval = KEY_REPEATS[key]
                while self.key_repeats_timers[key] - delay > interval:
                    pygame.event.post(
                        pygame.event.Event(pygame.KEYDOWN, key=key, repeat=True)
                    )
                    self.key_repeats_timers[key] -= interval

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
