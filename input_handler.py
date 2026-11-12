from __future__ import annotations

import math

import glfw


class InputController:
    def __init__(self, window: object, app) -> None:
        self.window = window
        self.app = app
        self.drag_index: int | None = None
        glfw.set_key_callback(window, self._on_key)
        glfw.set_mouse_button_callback(window, self._on_mouse_button)
        glfw.set_cursor_pos_callback(window, self._on_cursor)

    def _on_key(self, window, key, _scancode, action, _mods) -> None:
        if action != glfw.PRESS:
            return
        actions = {
            glfw.KEY_SPACE: self.app.toggle_pause,
            glfw.KEY_R: self.app.reset,
            glfw.KEY_C: self.app.toggle_chaos,
            glfw.KEY_UP: lambda: self.app.change_links(1),
            glfw.KEY_DOWN: lambda: self.app.change_links(-1),
            glfw.KEY_T: self.app.toggle_trails,
        }
        callback = actions.get(key)
        if callback:
            callback()

    def _on_mouse_button(self, window, button, action, _mods) -> None:
        if button != glfw.MOUSE_BUTTON_LEFT:
            return
        if action == glfw.RELEASE:
            self.drag_index = None
            return
        if action != glfw.PRESS or not self.app.paused:
            return
        cursor = glfw.get_cursor_pos(window)
        pointer = self.app.screen_to_world(*cursor)
        points = self.app.positions()[0]
        distances = [math.hypot(point[0] - pointer[0], point[1] - pointer[1]) for point in points]
        if distances and min(distances) < 0.18:
            self.drag_index = distances.index(min(distances))

    def _on_cursor(self, _window, x: float, y: float) -> None:
        if self.drag_index is None or not self.app.paused:
            return
        pointer = self.app.screen_to_world(x, y)
        points = self.app.positions()[0]
        parent = (0.0, 0.0) if self.drag_index == 0 else tuple(points[self.drag_index - 1])
        angle = math.atan2(pointer[0] - parent[0], -(pointer[1] - parent[1]))
        self.app.set_angle(self.drag_index, angle)
