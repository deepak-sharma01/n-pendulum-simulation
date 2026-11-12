from __future__ import annotations

import colorsys
import math
from collections import deque
from typing import Iterable

import glfw
from OpenGL.GL import (
    GL_BLEND,
    GL_COLOR_BUFFER_BIT,
    GL_LINE_SMOOTH,
    GL_LINE_SMOOTH_HINT,
    GL_NICEST,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_SRC_ALPHA,
    GL_TRIANGLE_FAN,
    GL_LINES,
    GL_LINE_STRIP,
    glBegin,
    glClear,
    glColor4f,
    glEnd,
    glHint,
    glLineWidth,
    glLoadIdentity,
    glMatrixMode,
    glOrtho,
    glPointSize,
    glVertex2f,
    glViewport,
    glEnable,
    glBlendFunc,
    GL_MODELVIEW,
    GL_PROJECTION,
)

from config import TRAIL_LENGTH


class OpenGLRenderer:
    def __init__(self, window: object, lengths: Iterable[float]) -> None:
        self.window = window
        self.lengths = list(lengths)
        self.trails_enabled = True
        self.trails: list[deque[tuple[float, float]]] = []
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)
        glHint(GL_LINE_SMOOTH_HINT, GL_NICEST)

    def set_lengths(self, lengths: Iterable[float]) -> None:
        self.lengths = list(lengths)
        self.trails.clear()

    def toggle_trails(self) -> None:
        self.trails_enabled = not self.trails_enabled
        if not self.trails_enabled:
            self.trails.clear()

    def world_scale(self) -> float:
        width, height = glfw.get_framebuffer_size(self.window)
        aspect = width / max(height, 1)
        radius = max(sum(self.lengths) * 1.15, 1.0)
        return radius if aspect >= 1.0 else radius / aspect

    def screen_to_world(self, x: float, y: float) -> tuple[float, float]:
        width, height = glfw.get_framebuffer_size(self.window)
        scale = self.world_scale()
        aspect = width / max(height, 1)
        return ((x / width - 0.5) * 2.0 * scale * aspect, (0.5 - y / height) * 2.0 * scale)

    def draw(self, positions: list) -> None:
        width, height = glfw.get_framebuffer_size(self.window)
        scale = self.world_scale()
        aspect = width / max(height, 1)
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-scale * aspect, scale * aspect, -scale, scale, -1.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClear(GL_COLOR_BUFFER_BIT)

        while len(self.trails) < len(positions):
            self.trails.append(deque(maxlen=TRAIL_LENGTH))
        for index, points in enumerate(positions):
            color = colorsys.hsv_to_rgb(index / max(len(positions), 1), 0.8, 0.95)
            self._draw_system(points, color, index)
        glfw.swap_buffers(self.window)

    def _draw_system(self, points, color: tuple[float, float, float], index: int) -> None:
        if self.trails_enabled and len(points):
            self.trails[index].append(tuple(points[-1]))
            trail = self.trails[index]
            glBegin(GL_LINE_STRIP)
            for step, point in enumerate(trail):
                alpha = 0.05 + 0.45 * (step + 1) / len(trail)
                glColor4f(*color, alpha)
                glVertex2f(*point)
            glEnd()

        glLineWidth(2.0)
        glColor4f(*color, 0.9)
        glBegin(GL_LINES)
        previous = (0.0, 0.0)
        for point in points:
            glVertex2f(*previous)
            glVertex2f(*point)
            previous = tuple(point)
        glEnd()

        for point in points:
            self._draw_circle(tuple(point), 0.045, (*color, 0.95))
        self._draw_circle((0.0, 0.0), 0.065, (1.0, 1.0, 1.0, 1.0))

    def _draw_circle(self, center: tuple[float, float], radius: float, color: tuple[float, float, float, float]) -> None:
        glBegin(GL_TRIANGLE_FAN)
        glColor4f(*color)
        glVertex2f(*center)
        for angle in range(17):
            radians = angle * 2.0 * math.pi / 16.0
            glVertex2f(center[0] + radius * math.cos(radians), center[1] + radius * math.sin(radians))
        glEnd()
