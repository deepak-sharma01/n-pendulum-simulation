# N-Pendulum Chaos

An interactive rigid-link N-pendulum simulation using NumPy, GLFW, and PyOpenGL.

## Project tree

```text
config.py          simulation constants
physics.py         vectorized dynamics and chaos ensemble
renderer.py        2D orthographic OpenGL renderer
input_handler.py   GLFW keyboard and mouse controls
main.py            CLI and fixed-timestep application loop
requirements.txt   Python dependencies
```

## Setup

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

Run with a chosen link count or ensemble:

```bash
python main.py --links 6
python main.py --links 5 --chaos
```

## Math

Each link has angle `theta_i`, length `L_i`, mass `m_i`, and angular velocity
`omega_i`. The vectorized Lagrangian equations form `M(theta) * theta_ddot = F`.
The mass matrix and velocity/gravity forces include every downstream mass.
Acceleration is solved with `numpy.linalg.solve`; RK4 integration uses 12
substeps per 1/60-second simulation tick. Chaos mode runs six systems whose
first angle differs by `k * 1e-5` radians.

## Controls

| Key/action | Effect |
|---|---|
| Space | Pause/resume |
| R | Reset |
| C | Toggle chaos ensemble |
| Up / Down | Add/remove a link (1-10) |
| T | Toggle tip trails |
| Left-drag while paused | Move the nearest bob |

## OpenGL note

PyOpenGL requires a working desktop OpenGL context. On Windows, install a
current graphics driver; on Linux, install the distribution's OpenGL/GLFW
runtime packages. Headless environments generally cannot create the window.
