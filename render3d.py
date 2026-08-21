"""Draws the same character in 3D.

This is a second function of the same parameter dictionary that render2d.py
uses. Nothing about the character model changes to support 3D — that is the
point of storing a character as numbers rather than as a drawing.

Shapes are built from two primitives, an ellipsoid and a cylinder, both
generated as parametric surfaces and passed to matplotlib's plot_surface.
"""
import numpy as np

CANVAS_BG = "#FBF7F0"
EYE_COLOUR = "#2E2440"


def _ellipsoid(ax, centre, radii, colour, n=18):
    u = np.linspace(0, 2 * np.pi, n * 2)
    v = np.linspace(0, np.pi, n)
    x = radii[0] * np.outer(np.cos(u), np.sin(v)) + centre[0]
    y = radii[1] * np.outer(np.sin(u), np.sin(v)) + centre[1]
    z = radii[2] * np.outer(np.ones_like(u), np.cos(v)) + centre[2]
    ax.plot_surface(x, y, z, color=colour, linewidth=0,
                    antialiased=True, shade=True)


def _cylinder(ax, centre, radius, height, colour, axis="z", n=16):
    theta = np.linspace(0, 2 * np.pi, n)
    h = np.linspace(-height / 2, height / 2, 2)
    t, hh = np.meshgrid(theta, h)
    a = radius * np.cos(t)
    b = radius * np.sin(t)

    if axis == "z":
        x, y, z = a + centre[0], b + centre[1], hh + centre[2]
    elif axis == "x":
        x, y, z = hh + centre[0], a + centre[1], b + centre[2]
    else:
        x, y, z = a + centre[0], hh + centre[1], b + centre[2]

    ax.plot_surface(x, y, z, color=colour, linewidth=0,
                    antialiased=True, shade=True)


def _animal(ax, c, s, p):
    col = c["colors"]
    body = 1.3 * s * p["body"]
    head_r = 0.72 * s * p["head"]
    leg_h = 1.0 * s * p["limbs"]
    leg_r = 0.16 * s

    _ellipsoid(ax, (0, 0, 0), (body, body * 0.6, body * 0.62), col["body"])
    for dx in (-0.7, 0.6):
        for dy in (-0.42, 0.42):
            _cylinder(ax, (dx * s, dy * body, -body * 0.55 - leg_h / 2),
                      leg_r, leg_h, col["limbs"])

    hx, hz = body + head_r * 0.4, body * 0.45
    _ellipsoid(ax, (hx, 0, hz), (head_r, head_r, head_r), col["head"])
    for dy in (-1, 1):
        _ellipsoid(ax, (hx, dy * head_r * 0.55, hz + head_r * 0.8),
                   (head_r * 0.22, head_r * 0.3, head_r * 0.42), col["accent"])
    _cylinder(ax, (-body - 0.35 * s, 0, body * 0.3), 0.1 * s, 0.8 * s,
              col["accent"], axis="x")

    # Eyes, so the 3D view matches the 2D one (round 2 evaluation finding).
    for dy in (-1, 1):
        _ellipsoid(ax, (hx + head_r * 0.80, dy * head_r * 0.42,
                        hz + head_r * 0.22),
                   (head_r * 0.20,) * 3, EYE_COLOUR, n=10)


def _plant(ax, c, s, p):
    col = c["colors"]
    stem_h = 2.6 * s * p["body"]
    bloom_r = 0.55 * s * p["head"]
    leaf = 0.8 * s * p["limbs"]

    _cylinder(ax, (0, 0, stem_h / 2 - 1.4 * s), 0.13 * s, stem_h, col["body"])
    for dy in (-1, 1):
        _ellipsoid(ax, (0, dy * leaf * 0.55, -0.3 * s),
                   (leaf * 0.3, leaf * 0.6, leaf * 0.16), col["limbs"])

    top = stem_h - 1.4 * s
    for k in range(6):
        angle = k * np.pi / 3
        _ellipsoid(ax, (bloom_r * 1.05 * np.cos(angle),
                        bloom_r * 1.05 * np.sin(angle), top),
                   (bloom_r * 0.55, bloom_r * 0.55, bloom_r * 0.3), col["head"])
    _ellipsoid(ax, (0, 0, top), (bloom_r * 0.5,) * 3, col["accent"])


def _human(ax, c, s, p):
    col = c["colors"]
    torso_h = 1.5 * s * p["body"]
    torso_w = 0.5 * s * p["body"]
    head_r = 0.42 * s * p["head"]
    limb = 1.2 * s * p["limbs"]
    limb_r = 0.14 * s

    _ellipsoid(ax, (0, 0, 0), (torso_w * 0.6, torso_w, torso_h / 2), col["body"])
    for dy in (-1, 1):
        _cylinder(ax, (0, dy * torso_w * 1.05, torso_h / 2 - limb / 2),
                  limb_r, limb, col["limbs"])
        _cylinder(ax, (0, dy * torso_w * 0.45, -torso_h / 2 - limb / 2),
                  limb_r, limb, col["limbs"])

    hz = torso_h / 2 + head_r * 1.05
    _ellipsoid(ax, (0, 0, hz), (head_r,) * 3, col["head"])
    _ellipsoid(ax, (0, 0, hz + head_r * 0.45),
               (head_r * 1.02, head_r * 1.02, head_r * 0.55), col["accent"])

    for dy in (-1, 1):
        _ellipsoid(ax, (head_r * 0.88, dy * head_r * 0.34, hz + head_r * 0.1),
                   (head_r * 0.19,) * 3, EYE_COLOUR, n=10)


DRAWERS = {"animal": _animal, "plant": _plant, "human": _human}


def draw(ax, char):
    """Render `char` onto a 3D axes. The designer can drag to rotate it."""
    ax.clear()
    ax.set_facecolor(CANVAS_BG)
    DRAWERS[char["type"]](ax, char, char["scale"], char["parts"])

    bound = 2.6 * max(char["scale"], 0.8)
    ax.set_xlim(-bound, bound)
    ax.set_ylim(-bound, bound)
    ax.set_zlim(-bound, bound)
    ax.set_box_aspect((1, 1, 1))
    ax.view_init(elev=16, azim=-58)
    ax.set_axis_off()
    return ax
