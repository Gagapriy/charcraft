"""The character model.

A character is not a drawing. It is a small dictionary of numbers and
colours, and both the 2D and the 3D view are functions of that dictionary.
That is the whole architectural idea of this app: one model, two renderers.
Adding the 3D view later costs you a new render function and nothing else.

    {
      "type": "animal",
      "scale": 1.0,                     # overall size multiplier
      "parts": {"head": 1.0, "body": 1.0, "limbs": 1.0},   # proportions
      "colors": {"head": "#...", "body": "#...",
                 "limbs": "#...", "accent": "#..."}
    }
"""
import copy

TYPES = ["animal", "plant", "human"]

# Parts a designer can select and recolour independently.
PART_KEYS = ["head", "body", "limbs", "accent"]

PART_LABELS = {
    "animal": {"head": "Head", "body": "Body", "limbs": "Legs", "accent": "Ears & tail"},
    "plant":  {"head": "Bloom", "body": "Stem", "limbs": "Leaves", "accent": "Centre"},
    "human":  {"head": "Head", "body": "Torso", "limbs": "Arms & legs", "accent": "Hair"},
}

SCALE_RANGE = (0.5, 2.0)
PROPORTION_RANGE = (0.6, 1.6)

DEFAULTS = {
    "animal": {
        "type": "animal",
        "scale": 1.0,
        "parts": {"head": 1.0, "body": 1.0, "limbs": 1.0},
        "colors": {"head": "#E8A33D", "body": "#E8A33D",
                   "limbs": "#C98429", "accent": "#8C5A1F"},
    },
    "plant": {
        "type": "plant",
        "scale": 1.0,
        "parts": {"head": 1.0, "body": 1.0, "limbs": 1.0},
        "colors": {"head": "#E5658A", "body": "#4E8C5A",
                   "limbs": "#6FB07C", "accent": "#F5C542"},
    },
    "human": {
        "type": "human",
        "scale": 1.0,
        "parts": {"head": 1.0, "body": 1.0, "limbs": 1.0},
        "colors": {"head": "#F0C9A6", "body": "#4C7BE0",
                   "limbs": "#F0C9A6", "accent": "#3E2A20"},
    },
}


def new_character(char_type="animal"):
    """A fresh character of the given type, at default proportions."""
    if char_type not in TYPES:
        raise ValueError(f"Unknown character type: {char_type}")
    return copy.deepcopy(DEFAULTS[char_type])


def switch_type(data, char_type):
    """Change type but keep the designer's scale and proportions."""
    fresh = new_character(char_type)
    fresh["scale"] = data.get("scale", 1.0)
    fresh["parts"] = dict(data.get("parts", fresh["parts"]))
    return fresh


def set_colour(data, part, hex_colour, whole_character=False):
    """Recolour one part, or every part at once."""
    if whole_character:
        for key in PART_KEYS:
            data["colors"][key] = hex_colour
    else:
        data["colors"][part] = hex_colour
    return data


def clamp(value, low, high):
    return max(low, min(high, value))


def validate(data):
    """Coerce anything loaded from the database into a usable shape."""
    safe = new_character(data.get("type", "animal"))
    safe["scale"] = clamp(float(data.get("scale", 1.0)), *SCALE_RANGE)
    for key in ("head", "body", "limbs"):
        safe["parts"][key] = clamp(
            float(data.get("parts", {}).get(key, 1.0)), *PROPORTION_RANGE
        )
    for key in PART_KEYS:
        colour = data.get("colors", {}).get(key)
        if isinstance(colour, str) and colour.startswith("#") and len(colour) == 7:
            safe["colors"][key] = colour
    return safe
