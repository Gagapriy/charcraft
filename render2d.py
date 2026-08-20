"""Draws a character in 2D from its parameters, using matplotlib primitives.

Every shape is tagged with the part it belongs to, so the editor can outline
whichever part the designer has selected. Each character type is one small
function; adding a fourth type means adding one more.
"""
from matplotlib.patches import Circle, Ellipse, FancyBboxPatch, Polygon

SELECTED_EDGE = "#F5C542"
CANVAS_BG = "#FBF7F0"


def _add(ax, patch, part, selected):
    patch.set_zorder(2 if part == "accent" else 3)
    if part == selected:
        patch.set_edgecolor(SELECTED_EDGE)
        patch.set_linewidth(3.0)
    else:
        patch.set_edgecolor("#2E2440")
        patch.set_linewidth(1.2)
    ax.add_patch(patch)


def _animal(ax, c, s, p, selected):
    col = c["colors"]
    body_w, body_h = 2.6 * s * p["body"], 1.7 * s * p["body"]
    head_r = 0.95 * s * p["head"]
    leg_h = 1.0 * s * p["limbs"]
    leg_w = 0.34 * s

    for i, dx in enumerate((-0.85, -0.3, 0.35, 0.9)):
        _add(ax, FancyBboxPatch(
            (dx * s - leg_w / 2, -body_h / 2 - leg_h), leg_w, leg_h,
            boxstyle="round,pad=0,rounding_size=0.12",
            facecolor=col["limbs"]), "limbs", selected)

    _add(ax, Ellipse((0, 0), body_w, body_h, facecolor=col["body"]),
         "body", selected)

    hx, hy = body_w / 2 + head_r * 0.45, body_h * 0.45
    for sign in (-1, 1):
        _add(ax, Ellipse((hx + sign * head_r * 0.45, hy + head_r * 0.85),
                         head_r * 0.55, head_r * 0.85,
                         facecolor=col["accent"]), "accent", selected)
    _add(ax, Polygon([(-body_w / 2, body_h * 0.25),
                      (-body_w / 2 - 0.9 * s, body_h * 0.8),
                      (-body_w / 2 - 0.55 * s, body_h * 0.15)],
                     closed=True, facecolor=col["accent"]), "accent", selected)
    _add(ax, Circle((hx, hy), head_r, facecolor=col["head"]), "head", selected)

    eye = head_r * 0.16
    for dx in (-0.28, 0.28):
        ax.add_patch(Circle((hx + dx * head_r, hy + 0.15 * head_r), eye,
                            facecolor="#2E2440", zorder=4))


def _plant(ax, c, s, p, selected):
    col = c["colors"]
    stem_h = 3.0 * s * p["body"]
    bloom_r = 0.85 * s * p["head"]
    leaf = 1.15 * s * p["limbs"]

    _add(ax, FancyBboxPatch((-0.16 * s, -1.6 * s), 0.32 * s, stem_h,
                            boxstyle="round,pad=0,rounding_size=0.14",
                            facecolor=col["body"]), "body", selected)
    for sign in (-1, 1):
        _add(ax, Ellipse((sign * leaf * 0.55, -0.3 * s), leaf, leaf * 0.5,
                         angle=sign * 22, facecolor=col["limbs"]),
             "limbs", selected)

    top = -1.6 * s + stem_h
    for k in range(6):
        angle = k * 60
        from math import cos, radians, sin
        px = bloom_r * 1.05 * cos(radians(angle))
        py = bloom_r * 1.05 * sin(radians(angle))
        _add(ax, Circle((px, top + py), bloom_r * 0.62,
                        facecolor=col["head"]), "head", selected)
    _add(ax, Circle((0, top), bloom_r * 0.55, facecolor=col["accent"]),
         "accent", selected)


def _human(ax, c, s, p, selected):
    col = c["colors"]
    torso_w, torso_h = 1.3 * s * p["body"], 2.0 * s * p["body"]
    head_r = 0.72 * s * p["head"]
    limb = 1.5 * s * p["limbs"]
    limb_w = 0.3 * s

    for sign in (-1, 1):
        _add(ax, FancyBboxPatch(
            (sign * (torso_w / 2) - limb_w / 2, torso_h / 2 - limb),
            limb_w, limb, boxstyle="round,pad=0,rounding_size=0.13",
            facecolor=col["limbs"]), "limbs", selected)
    for sign in (-1, 1):
        _add(ax, FancyBboxPatch(
            (sign * 0.32 * s - limb_w / 2, -torso_h / 2 - limb),
            limb_w, limb, boxstyle="round,pad=0,rounding_size=0.13",
            facecolor=col["limbs"]), "limbs", selected)

    _add(ax, FancyBboxPatch((-torso_w / 2, -torso_h / 2), torso_w, torso_h,
                            boxstyle="round,pad=0,rounding_size=0.3",
                            facecolor=col["body"]), "body", selected)

    hy = torso_h / 2 + head_r * 0.95
    _add(ax, Ellipse((0, hy + head_r * 0.42), head_r * 2.05, head_r * 1.2,
                     facecolor=col["accent"]), "accent", selected)
    _add(ax, Circle((0, hy), head_r, facecolor=col["head"]), "head", selected)

    for dx in (-0.3, 0.3):
        ax.add_patch(Circle((dx * head_r, hy + 0.1 * head_r), head_r * 0.11,
                            facecolor="#2E2440", zorder=4))


DRAWERS = {"animal": _animal, "plant": _plant, "human": _human}


def draw(ax, char, selected_part=None):
    """Render `char` onto a matplotlib axes. Call this on every change."""
    ax.clear()
    ax.set_facecolor(CANVAS_BG)
    ax.set_aspect("equal")
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.axis("off")

    s = char["scale"]
    DRAWERS[char["type"]](ax, char, s, char["parts"], selected_part)
    return ax
