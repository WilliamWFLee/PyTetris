#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
pytetris.locals.size

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

# Some game dimensions
VISIBLE_ROWS = 20
ROWS = 40
COLUMNS = 10
SQUARE_WIDTH = 25
LINE_WIDTH = 1


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
