"""
Unicode character database with optical weights
"""
from typing import List, Tuple

import numpy as np


class UnicodeChar:
    """Unicode character with optical properties"""

    def __init__(self, char: str, weight: float, density: float):
        """
        Args:
            char: Unicode character
            weight: Optical weight (0.0 - 1.0, where 0 is white, 1 is black)
            density: Character density (0.0 - 1.0)
        """
        self.char = char
        self.weight = weight
        self.density = density

    def __repr__(self):
        return f"UnicodeChar('{self.char}', weight={self.weight:.3f})"


# Unicode characters sorted by optical weight (light to dark)
# These characters are selected based on their visual density and rendering
UNICODE_CHARS: List[UnicodeChar] = [
    # Light characters (spaces, dots)
    UnicodeChar(' ', 0.0, 0.0),      # Space - white
    UnicodeChar('·', 0.05, 0.1),     # Middle dot
    UnicodeChar('░', 0.15, 0.2),     # Light shade
    UnicodeChar('▒', 0.25, 0.3),     # Medium shade
    UnicodeChar('▓', 0.35, 0.4),     # Dark shade
    UnicodeChar('▄', 0.3, 0.35),     # Lower half block
    UnicodeChar('▀', 0.3, 0.35),     # Upper half block
    UnicodeChar('▌', 0.3, 0.35),     # Left half block
    UnicodeChar('▐', 0.3, 0.35),     # Right half block

    # Medium-light characters
    UnicodeChar('▖', 0.4, 0.45),     # Quadrant lower left
    UnicodeChar('▗', 0.4, 0.45),     # Quadrant lower right
    UnicodeChar('▘', 0.4, 0.45),     # Quadrant upper left
    UnicodeChar('▙', 0.5, 0.55),     # Quadrant upper left and lower left and lower right
    UnicodeChar('▚', 0.5, 0.55),     # Quadrant upper left and lower right
    UnicodeChar('▛', 0.5, 0.55),     # Quadrant upper left and upper right and lower left
    UnicodeChar('▜', 0.5, 0.55),     # Quadrant upper left and upper right and lower right
    UnicodeChar('▝', 0.4, 0.45),     # Quadrant upper right
    UnicodeChar('▞', 0.5, 0.55),     # Quadrant upper right and lower left
    UnicodeChar('▟', 0.5, 0.55),     # Quadrant upper right and lower left and lower right

    # Medium characters
    UnicodeChar('▱', 0.45, 0.5),     # White parallelogram
    UnicodeChar('▰', 0.55, 0.6),     # Black parallelogram
    UnicodeChar('▲', 0.5, 0.55),     # White square containing black small square
    UnicodeChar('△', 0.5, 0.55),     # Square with horizontal fill
    UnicodeChar('▴', 0.5, 0.55),     # Square with vertical fill
    UnicodeChar('▵', 0.45, 0.5),     # Square with orthogonal crosshatch fill
    UnicodeChar('▸', 0.5, 0.55),     # Right-pointing triangle
    UnicodeChar('▹', 0.5, 0.55),     # Right-pointing small triangle
    UnicodeChar('►', 0.5, 0.55),     # Up-pointing triangle
    UnicodeChar('▻', 0.5, 0.55),     # Right-pointing triangle

    # Medium-dark characters
    UnicodeChar('◐', 0.6, 0.65),     # Circle with left half black
    UnicodeChar('◑', 0.6, 0.65),     # Circle with right half black
    UnicodeChar('◒', 0.55, 0.6),     # Circle with lower half black
    UnicodeChar('◓', 0.55, 0.6),     # Circle with upper half black
    UnicodeChar('◔', 0.5, 0.55),     # Circle with upper right quadrant black
    UnicodeChar('◕', 0.65, 0.7),     # Circle with all but upper left quadrant black
    UnicodeChar('◖', 0.6, 0.65),     # Left half circle
    UnicodeChar('◗', 0.6, 0.65),     # Right half circle

    # Dark characters
    UnicodeChar('◘', 0.7, 0.75),     # Inverse bullet
    UnicodeChar('◙', 0.7, 0.75),     # Inverse white circle
    UnicodeChar('◚', 0.65, 0.7),     # Upper half inverse white circle
    UnicodeChar('◛', 0.65, 0.7),     # Lower half inverse white circle
    UnicodeChar('◜', 0.65, 0.7),     # Upper left quadrant circular arc
    UnicodeChar('◝', 0.65, 0.7),     # Upper right quadrant circular arc
    UnicodeChar('◞', 0.65, 0.7),     # Lower right quadrant circular arc
    UnicodeChar('◟', 0.65, 0.7),     # Lower left quadrant circular arc

    # Very dark characters
    UnicodeChar('◠', 0.75, 0.8),     # Upper half circle
    UnicodeChar('◡', 0.75, 0.8),     # Lower half circle
    UnicodeChar('◢', 0.8, 0.85),     # Black lower right triangle
    UnicodeChar('◣', 0.8, 0.85),     # Black lower left triangle
    UnicodeChar('◤', 0.8, 0.85),     # Black upper left triangle
    UnicodeChar('◥', 0.8, 0.85),     # Black upper right triangle
    UnicodeChar('◦', 0.7, 0.75),     # White bullet
    UnicodeChar('◬', 0.75, 0.8),     # White up-pointing triangle with dot
    UnicodeChar('◭', 0.75, 0.8),     # Up-pointing triangle with left half black
    UnicodeChar('◮', 0.75, 0.8),     # Up-pointing triangle with right half black

    # Almost black
    UnicodeChar('◯', 0.85, 0.9),     # Large circle
    UnicodeChar('◰', 0.8, 0.85),     # Square with left half black
    UnicodeChar('◱', 0.8, 0.85),     # Square with right half black
    UnicodeChar('◲', 0.8, 0.85),     # Square with upper half black
    UnicodeChar('◳', 0.8, 0.85),     # Square with lower half black
    UnicodeChar('◴', 0.8, 0.85),     # Square with upper left diagonal half black
    UnicodeChar('◵', 0.8, 0.85),     # Square with lower right diagonal half black
    UnicodeChar('◶', 0.8, 0.85),     # Square with upper right diagonal half black
    UnicodeChar('◷', 0.8, 0.85),     # Square with lower left diagonal half black

    # Black characters
    UnicodeChar('■', 0.9, 0.95),     # Black square
    UnicodeChar('□', 0.1, 0.15),     # White square (for contrast)
    UnicodeChar('▪', 0.95, 1.0),     # Black small square
    UnicodeChar('▫', 0.05, 0.1),     # White small square
    UnicodeChar('▬', 0.85, 0.9),     # Black rectangle
    UnicodeChar('▭', 0.15, 0.2),     # White rectangle
    UnicodeChar('▲', 0.9, 0.95),     # Black up-pointing triangle
    UnicodeChar('△', 0.1, 0.15),     # White up-pointing triangle
    UnicodeChar('●', 0.95, 1.0),     # Black circle
    UnicodeChar('○', 0.05, 0.1),     # White circle
    UnicodeChar('◆', 0.9, 0.95),     # Black diamond
    UnicodeChar('◇', 0.1, 0.15),     # White diamond
    UnicodeChar('◈', 0.5, 0.55),     # White diamond containing black small diamond

    # Full black
    UnicodeChar('█', 1.0, 1.0),      # Full block - black
    UnicodeChar('▉', 0.95, 1.0),     # Left seven eighths block
    UnicodeChar('▊', 0.9, 0.95),     # Left three quarters block
    UnicodeChar('▋', 0.85, 0.9),     # Left five eighths block
    UnicodeChar('▌', 0.75, 0.8),     # Left half block
    UnicodeChar('▍', 0.65, 0.7),     # Left three eighths block
    UnicodeChar('▎', 0.55, 0.6),     # Left quarter block
    UnicodeChar('▏', 0.45, 0.5),     # Left one eighth block
    UnicodeChar('▐', 0.75, 0.8),     # Right half block
    UnicodeChar('▔', 0.5, 0.55),     # Upper one eighth block
    UnicodeChar('▕', 0.5, 0.55),     # Right one eighth block
    UnicodeChar('▖', 0.5, 0.55),     # Lower one quarter block
    UnicodeChar('▗', 0.5, 0.55),     # Lower one eighth block
    UnicodeChar('▘', 0.5, 0.55),     # Lower one eighth block
    UnicodeChar('▙', 0.75, 0.8),     # Lower half block
    UnicodeChar('▚', 0.5, 0.55),     # Lower one quarter block
    UnicodeChar('▛', 0.75, 0.8),     # Lower three eighths block
    UnicodeChar('▜', 0.75, 0.8),     # Lower three eighths block
    UnicodeChar('▝', 0.5, 0.55),     # Upper one quarter block
    UnicodeChar('▞', 0.5, 0.55),     # Upper one quarter block
    UnicodeChar('▟', 0.75, 0.8),     # Lower three eighths block
]


def get_char_by_weight(target_weight: float) -> str:
    """
    Get Unicode character closest to target optical weight

    Args:
        target_weight: Target optical weight (0.0 - 1.0)

    Returns:
        Unicode character
    """
    if target_weight < 0:
        target_weight = 0
    if target_weight > 1:
        target_weight = 1

    # Binary search for closest character
    weights = np.array([char.weight for char in UNICODE_CHARS])
    idx = np.abs(weights - target_weight).argmin()

    return UNICODE_CHARS[idx].char


def get_char_by_luminance(luminance: float) -> str:
    """
    Get Unicode character based on luminance

    Args:
        luminance: Luminance value (0.0 - 1.0, where 0 is black, 1 is white)

    Returns:
        Unicode character
    """
    # Convert luminance to optical weight (inverse)
    weight = 1.0 - luminance
    return get_char_by_weight(weight)

