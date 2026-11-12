from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from config import GRAVITY, PERTURBATION, SUBSTEPS


@dataclass
class NPendulumSystem:
    n: int
    lengths: np.ndarray | None = None
    masses: np.ndarray | None = None
    gravity: float = GRAVITY

    def __post_init__(self) -> None:
        if not 1 <= self.n:
            raise ValueError("n must be positive")
        self.lengths = np.ones(self.n, dtype=float) if self.lengths is None else np.asarray(self.lengths, dtype=float)
        self.masses = np.ones(self.n, dtype=float) if self.masses is None else np.asarray(self.masses, dtype=float)
        if self.lengths.shape != (self.n,) or self.masses.shape != (self.n,):
            raise ValueError("lengths and masses must contain one value per link")
        self.state = np.zeros(2 * self.n, dtype=float)
        self.reset()

    def reset(self, theta: np.ndarray | None = None) -> None:
        self.state.fill(0.0)
        self.state[: self.n] = (
            np.linspace(0.8, 0.2, self.n) if theta is None else np.asarray(theta, dtype=float)
        )

    def derivative(self, state: np.ndarray) -> np.ndarray:
        theta, omega = state[: self.n], state[self.n :]
        difference = theta[:, None] - theta[None, :]
        suffix_mass = np.cumsum(self.masses[::-1])[::-1]
        coefficients = suffix_mass[np.maximum.outer(np.arange(self.n), np.arange(self.n))]
        mass_matrix = coefficients * self.lengths[:, None] * self.lengths[None, :] * np.cos(difference)
        force = -np.sum(
            coefficients
            * self.lengths[:, None]
            * self.lengths[None, :]
            * omega[None, :] ** 2
            * np.sin(difference),
            axis=1,
        )
        force -= suffix_mass * self.gravity * self.lengths * np.sin(theta)
        acceleration = np.linalg.solve(mass_matrix + 1e-9 * np.eye(self.n), force)
        return np.concatenate((omega, acceleration))

    def step(self, dt: float, substeps: int = SUBSTEPS) -> None:
        h = dt / substeps
        for _ in range(substeps):
            state = self.state
            k1 = self.derivative(state)
            k2 = self.derivative(state + 0.5 * h * k1)
            k3 = self.derivative(state + 0.5 * h * k2)
            k4 = self.derivative(state + h * k3)
            self.state = state + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6.0

    def get_cartesian_positions(self) -> np.ndarray:
        theta = self.state[: self.n]
        x = np.cumsum(self.lengths * np.sin(theta))
        y = np.cumsum(-self.lengths * np.cos(theta))
        return np.column_stack((x, y))

    def get_total_energy(self) -> float:
        theta, omega = self.state[: self.n], self.state[self.n :]
        difference = theta[:, None] - theta[None, :]
        suffix_mass = np.cumsum(self.masses[::-1])[::-1]
        coefficients = suffix_mass[np.maximum.outer(np.arange(self.n), np.arange(self.n))]
        kinetic = 0.5 * np.sum(
            coefficients
            * self.lengths[:, None]
            * self.lengths[None, :]
            * omega[:, None]
            * omega[None, :]
            * np.cos(difference)
        )
        potential = np.sum(suffix_mass * self.gravity * self.lengths * (1.0 - np.cos(theta)))
        return float(kinetic + potential)


class ChaosEnsemble:
    def __init__(self, n: int, size: int = 6, perturbation: float = PERTURBATION) -> None:
        self.size = size
        self.perturbation = perturbation
        self.n = n
        self.systems: list[NPendulumSystem] = []
        self.reset()

    @property
    def primary(self) -> NPendulumSystem:
        return self.systems[0]

    def reset(self, theta: np.ndarray | None = None) -> None:
        base = np.linspace(0.8, 0.2, self.n) if theta is None else np.asarray(theta, dtype=float)
        self.systems = []
        for index in range(self.size):
            initial = base.copy()
            initial[0] += index * self.perturbation
            self.systems.append(NPendulumSystem(self.n))
            self.systems[-1].reset(initial)

    def set_n(self, n: int) -> None:
        self.n = n
        self.reset()

    def step(self, dt: float) -> None:
        for system in self.systems:
            system.step(dt)

    def get_total_energy(self) -> float:
        return float(sum(system.get_total_energy() for system in self.systems))
