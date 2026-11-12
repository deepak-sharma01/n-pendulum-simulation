from __future__ import annotations

import argparse
import time

import glfw

from config import DEFAULT_N, ENSEMBLE_SIZE, MAX_N, TARGET_FPS, WINDOW_HEIGHT, WINDOW_WIDTH
from input_handler import InputController
from physics import ChaosEnsemble, NPendulumSystem
from renderer import OpenGLRenderer


class Simulation:
    def __init__(self, window: object, links: int, chaos: bool) -> None:
        self.window = window
        self.n = links
        self.paused = False
        self.chaos = chaos
        self.system = NPendulumSystem(links)
        self.ensemble = ChaosEnsemble(links, ENSEMBLE_SIZE)
        self.renderer = OpenGLRenderer(window, self.system.lengths)
        self.input = InputController(window, self)

    def active_systems(self):
        return self.ensemble.systems if self.chaos else [self.system]

    def positions(self):
        return [system.get_cartesian_positions() for system in self.active_systems()]

    def screen_to_world(self, x, y):
        return self.renderer.screen_to_world(x, y)

    def set_angle(self, index: int, angle: float) -> None:
        self.system.state[index] = angle
        self.ensemble.primary.state[index] = angle
        if self.chaos:
            base = self.ensemble.primary.state[: self.n].copy()
            self.ensemble.reset(base)

    def toggle_pause(self) -> None:
        self.paused = not self.paused

    def reset(self) -> None:
        self.system.reset()
        self.ensemble.reset()

    def toggle_chaos(self) -> None:
        self.chaos = not self.chaos

    def change_links(self, amount: int) -> None:
        self.n = max(1, min(MAX_N, self.n + amount))
        self.system = NPendulumSystem(self.n)
        self.ensemble.set_n(self.n)
        self.renderer.set_lengths(self.system.lengths)

    def toggle_trails(self) -> None:
        self.renderer.toggle_trails()

    def update_title(self) -> None:
        mode = "CHAOS" if self.chaos else "SINGLE"
        energy = self.ensemble.get_total_energy() if self.chaos else self.system.get_total_energy()
        glfw.set_window_title(self.window, f"N-Pendulum | N={self.n} | {mode} | E={energy:.4f} J")

    def run(self) -> None:
        fixed_dt = 1.0 / TARGET_FPS
        accumulator = 0.0
        previous = time.perf_counter()
        while not glfw.window_should_close(self.window):
            now = time.perf_counter()
            accumulator += min(now - previous, 0.25)
            previous = now
            glfw.poll_events()
            if not self.paused:
                while accumulator >= fixed_dt:
                    if self.chaos:
                        self.ensemble.step(fixed_dt)
                    else:
                        self.system.step(fixed_dt)
                    accumulator -= fixed_dt
            self.renderer.draw(self.positions())
            self.update_title()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Interactive N-pendulum chaos simulation")
    parser.add_argument("--links", type=int, default=DEFAULT_N, choices=range(1, MAX_N + 1))
    parser.add_argument("--chaos", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not glfw.init():
        raise RuntimeError("Unable to initialize GLFW")
    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "N-Pendulum", None, None)
    if not window:
        glfw.terminate()
        raise RuntimeError("Unable to create OpenGL window")
    glfw.make_context_current(window)
    try:
        Simulation(window, args.links, args.chaos).run()
    finally:
        glfw.destroy_window(window)
        glfw.terminate()


if __name__ == "__main__":
    main()
