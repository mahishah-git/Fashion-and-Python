"""Colour matching rules (no Streamlit code in here, so it is easy to test).

The rules are deliberately simple and explainable:
  * Neutrals go with everything.
  * Analogous colours sit close together on the colour wheel (within 45 degrees).
  * Complementary colours sit roughly opposite (at least 125 degrees apart).
  * Anything in between is treated as a clash.
"""
import colorsys

from sample_data import PALETTE

NEUTRALS = {"Ivory", "White", "Taupe", "Camel", "Charcoal", "Ink Black", "Navy"}
ACCENTS = ["Burgundy", "Cobalt", "Butter Yellow", "Blush"]  # suggested with a neutral base
ANALOGOUS_RANGE = 45
COMPLEMENT_MIN = 125
DEFAULT_HEX = "#B9AEA2"


def hex_for(name):
    """Hex value for a colour name; unknown names get a safe taupe."""
    return PALETTE.get(name, DEFAULT_HEX)


def hex_to_rgb(hex_value):
    """'#6F1D32' -> (111, 29, 50). Bad input falls back to the default taupe."""
    try:
        digits = hex_value.lstrip("#")
        return tuple(int(digits[i:i + 2], 16) for i in (0, 2, 4))
    except (ValueError, AttributeError):
        return hex_to_rgb(DEFAULT_HEX)


def hue_of(name):
    """Position on the colour wheel in degrees (0-360)."""
    r, g, b = hex_to_rgb(hex_for(name))
    hue, _sat, _val = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return hue * 360


def hue_gap(name_a, name_b):
    """Shortest distance between two colours on the wheel (0-180)."""
    gap = abs(hue_of(name_a) - hue_of(name_b))
    return min(gap, 360 - gap)


def is_neutral(name):
    # Unknown colour names are treated as neutral so they never cause a clash.
    return name in NEUTRALS or name not in PALETTE


def colours_compatible(name_a, name_b):
    """True when two colours may be worn together under the rules above."""
    if name_a == name_b or is_neutral(name_a) or is_neutral(name_b):
        return True
    gap = hue_gap(name_a, name_b)
    return gap <= ANALOGOUS_RANGE or gap >= COMPLEMENT_MIN


def analogous_colours(base, limit=3):
    """Non-neutral colours close to the base, nearest first."""
    if is_neutral(base):
        return []
    close = [c for c in PALETTE if c != base and not is_neutral(c)
             and hue_gap(base, c) <= ANALOGOUS_RANGE]
    return sorted(close, key=lambda c: hue_gap(base, c))[:limit]


def complementary_colours(base, limit=3):
    """Non-neutral colours roughly opposite the base, closest to 180 first."""
    if is_neutral(base):
        return []
    opposite = [c for c in PALETTE if c != base and not is_neutral(c)
                and hue_gap(base, c) >= COMPLEMENT_MIN]
    return sorted(opposite, key=lambda c: 180 - hue_gap(base, c))[:limit]


def build_palette(base):
    """Everything the Colour Edit page needs for one base colour."""
    if base not in PALETTE:
        base = "Burgundy"
    neutral = is_neutral(base)
    return {
        "base": base,
        "neutral": neutral,
        "analogous": analogous_colours(base),
        "complementary": complementary_colours(base),
        "accents": [c for c in ACCENTS if c != base] if neutral else [],
    }


def palette_colours(palette):
    """Flat list of colour names in a palette, base first, no duplicates."""
    names = [palette["base"]]
    for group in ("analogous", "complementary", "accents"):
        for name in palette[group]:
            if name not in names:
                names.append(name)
    return names


def items_matching(items, colour_names, include_neutrals=False):
    """Wardrobe items whose colour is in colour_names (a set makes lookup fast)."""
    wanted = set(colour_names)
    if include_neutrals:
        wanted |= NEUTRALS
    return [item for item in items if item.get("color") in wanted]


def describe_palette(palette):
    """A short editorial paragraph that changes with the selection."""
    base = palette["base"]
    if palette["neutral"]:
        return (f"{base} is a neutral. It anchors a look without competing for attention, "
                f"so almost anything can sit beside it. Bring in one of the accent colours "
                f"below when the outfit needs a point of focus.")
    parts = [f"{base} leads this edit."]
    if palette["analogous"]:
        parts.append(f"Its neighbours on the wheel, {_join(palette['analogous'])}, "
                     f"give a tonal, quiet look.")
    if palette["complementary"]:
        parts.append(f"{_join(palette['complementary'])} sit opposite and create deliberate contrast.")
    parts.append("Keep one colour dominant and let the rest appear in small doses.")
    return " ".join(parts)


def _join(names):
    if len(names) <= 2:
        return " and ".join(names)
    return ", ".join(names[:-1]) + " and " + names[-1]
