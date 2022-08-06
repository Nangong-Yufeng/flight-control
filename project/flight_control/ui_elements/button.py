#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Python pygame module for creating simple buttons. This module requires at least `pygame 2.0.0`. Newer version is recommended!
To install the latest version of pygame, find the corresponding command for your OS below and run the command in your terminal:

  PYGAME INSTALLATION:

  - Windows                   py -m pip install -U pygame --user
  - Mac OS                    python3 -m pip install -U pygame --user
  - Linux Debian/Ubuntu/Mint  sudo apt-get install python3-pygame
  - Linux Fedora/Red hat      sudo yum install python3-pygame
  - OpenSUSE                  sudo zypper install python3-pygame
  - Linux Arch/Manjaro        sudo pamac install python-pygame
"""

from pygame.draw import rect
from pygame import font
from pygame.mouse import get_pos, get_pressed

font.init()


def mouse_over(element):
    if element.collidepoint(get_pos()):
        return True


class button:
    """
    Creates a button element, which is made with pygame.Rect(). This program allows you to click it and make something happen
    when clicked.

        Usage: button(surface, (r, g, b), "text", (x, y, width, height), lambda: command, [optional argument(s)])

        Optional arguments (instance):
            [Borders]
            (int) border_radius, (int) border_top_left_radius, (int) border_top_right_radius,
            (int) border_bottom_left_radius, (int) border_bottom_right_radius

            [Font]
            (pygame Font/SysFont) font, (str) font_family, (int) font_size

            [Styling]
            (list) text_color, (list) hover_color, (bool) bold, (bool) italic
    """

    # NOTE: Functions with single underscore (_) before its name, should not be called from outside this class,
    #       for example: self._foo()

    def __init__(self, surface, color, text, rect, command,
                 border_radius=-1, border_top_left_radius=-1, border_top_right_radius=-1,
                 border_bottom_left_radius=-1, border_bottom_right_radius=-1,
                 font=None, font_family=None, font_size=None, bold=False, italic=False,
                 hover_color=None, text_color=(0, 0, 0)):

        self.x, self.y, self.width, self.height = rect
        self.surface = surface
        self.command = command
        self.is_clicked = False

        self.color = color
        self.hover_color = hover_color
        self.active_color = self.color

        self.text = text
        self.font = font
        self.highlight_font = None
        self.current_font = self.font
        self.font_family = font_family
        self.font_size = font_size
        self.text_color = text_color

        self.bold = bold
        self.italic = italic

        self.border_radius = border_radius
        self.border_top_left_radius = border_top_left_radius
        self.border_top_right_radius = border_top_right_radius
        self.border_bottom_left_radius = border_bottom_left_radius
        self.border_bottom_right_radius = border_bottom_right_radius

    def show(self):
        global btn
        btn = rect(self.surface, self.active_color, (
            self.x if not self.is_clicked else self.x + 2,
            self.y if not self.is_clicked else self.y + 2,
            self.width if not self.is_clicked else self.width - 4,
            self.height if not self.is_clicked else self.height - 4
        ),
                   border_radius=self.border_radius,
                   border_top_left_radius=self.border_top_left_radius,
                   border_top_right_radius=self.border_top_right_radius,
                   border_bottom_left_radius=self.border_bottom_left_radius,
                   border_bottom_right_radius=self.border_bottom_right_radius
                   )

        self._update()

        btn_text = self.current_font.render(self.text, True, self.text_color)
        btn_text_rect = btn_text.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        self.surface.blit(btn_text, btn_text_rect)

    def _update(self):
        if self.font_size is None:
            self.font_size = 25

        if self.font is None and self.font_family is None:
            self.font = font.SysFont("freesansbold.ttf", self.font_size, self.bold, self.italic)
            self.highlight_font = font.SysFont("freesansbold.ttf", self.font_size - 2, self.bold, self.italic)
        elif self.font is None and self.font_family is not None:
            self.font = font.SysFont(self.font_family, self.font_size, self.bold, self.italic)
            self.highlight_font = font.SysFont(self.font_family, self.font_size - 2, self.bold, self.italic)

        if self.hover_color is None:
            r, g, b = [val - 30 if val > 30 else val + 30 for val in list(self.color)[:3]]
            self.hover_color = (r, g, b)

        if mouse_over(btn):
            self.active_color = self.hover_color

            if get_pressed()[0]:
                if not self.is_clicked:
                    self.command()
                self.is_clicked = True
            else:
                self.is_clicked = False
        else:
            self.active_color = self.color

        if self.is_clicked:
            self.current_font = self.highlight_font
        else:
            self.current_font = self.font
