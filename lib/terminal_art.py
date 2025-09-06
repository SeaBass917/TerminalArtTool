"""Utility functions for use in ascii/unicode terminal art."""

import numpy as np
from .constants import dots4


def generate_braille_binary_list():
    """Utility I needed at the time."""
    print("")
    for i in [0, 128, 64, 192, 32, 160, 96, 224]:
        for j in [1, 9, 5, 13, 3, 11, 7, 15]:
            print(i + j)
    for i in [16, 144, 80, 208, 48, 176, 112, 240]:
        for j in [0, 8, 4, 12, 2, 10, 6, 14]:
            print(i + j)
    for i in [16, 144, 80, 208, 48, 176, 112, 240]:
        for j in [1, 9, 5, 13, 3, 11, 7, 15]:
            print(i + j)


def get_dot(edge_window: np.ndarray, invert=False) -> str:
    """For a given window of edges (0|1's or 0|255's whatever),
    return the corresponding braille dots.

    Args:
        edge_window: Must be shape (4,2) or (3,2).
    """

    def value(v: int, w: int) -> int:
        if invert:
            return w if 0 == v else 0

        return w if 0 < v else 0

    if edge_window.shape == (4, 2):
        dots = dots4

        weights = [128, 64, 32, 16, 8, 4, 2, 1]
        flat = edge_window.flatten()
        x = sum(value(v, w) for w, v in zip(weights, flat))

    elif edge_window.shape == (3, 2):
        # dots = dots3
        raise NotImplementedError("No 3x2 yet.")
    else:
        raise RuntimeError(
            f"Invalid shape {edge_window.shape}. Cannot proceed.")

    if x not in dots:
        x += 1

        if x not in dots:
            raise NotImplementedError(
                f"I didn't think this would happen. Do more testing. {x} did not exist.")

    return dots[x]
