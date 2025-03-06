import arcadia_pycolor as apc
import matplotlib.colors as mcolors
import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def darken(color, factor: float = 0.6) -> str:
    rgb = mcolors.to_rgb(color)
    rgb_darker = tuple(c * factor for c in rgb)
    return mcolors.to_hex(rgb_darker)


def get_custom_colorpalette() -> dict[str | tuple[str, str], str]:
    # color palette for each (instrument, wavelength) combination
    greens = apc.palettes.green_shades.colors
    reds = apc.palettes.red_shades.colors
    instrument_color_palette = {
        ("openraman", 532): greens[1].hex_code,
        ("wasatch", 532): greens[2].hex_code,
        ("horiba", 785): reds[0].hex_code,
        ("renishaw", 785): reds[1].hex_code,
        ("wasatch", 785): reds[2].hex_code,
    }

    # color palette for each (strain, medium) combination
    chlamy_color_palette = {
        ("CC-124", "TAP"): apc.denim.hex_code,
        ("CC-125", "TAP"): apc.aegean.hex_code,
        ("CC-1373", "TAP"): apc.dusk.hex_code,
        ("CC-124", "M-N"): apc.tangerine.hex_code,
        ("CC-125", "M-N"): apc.dragon.hex_code,
        ("CC-1373", "M-N"): apc.redwood.hex_code,
    }

    # merge palettes
    color_palette = {**instrument_color_palette, **chlamy_color_palette}
    return color_palette


def get_default_plotly_layout() -> dict:
    layout = {
        "paper_bgcolor": apc.parchment.hex_code,
        "plot_bgcolor": apc.parchment.hex_code,
        "template": "simple_white",
        "margin": {"l": 50, "r": 50, "t": 50, "b": 75},
    }
    return layout
