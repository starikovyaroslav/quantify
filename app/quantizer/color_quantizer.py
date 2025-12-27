"""
Color quantization module
"""
from typing import Tuple

import numpy as np


def quantize_colors(image: np.ndarray, quality: int = 5) -> np.ndarray:
    """
    Quantize colors in image to reduce palette
    
    Args:
        image: Image array (H, W, 3) with RGB values
        quality: Quality level (1-10), higher = more colors
    
    Returns:
        Quantized image array
    """
    # Calculate number of colors based on quality
    # Quality 1 = 16 colors, Quality 10 = 256 colors
    num_colors = int(16 + (quality - 1) * (256 - 16) / 9)
    num_colors = max(16, min(256, num_colors))
    
    # Reshape image to 2D array of pixels
    h, w, c = image.shape
    pixels = image.reshape(-1, c).astype(np.float32)
    
    # Improved quantization: use perceptually uniform color space
    # Convert RGB to LAB for better color quantization
    # For speed, we'll use a hybrid approach
    
    # Use adaptive quantization based on image characteristics
    if quality >= 7:
        # High quality: use more sophisticated quantization
        # Convert to LAB-like space for better perceptual uniformity
        # Simplified LAB conversion
        rgb_normalized = pixels / 255.0
        
        # Apply gamma correction
        rgb_linear = np.where(rgb_normalized > 0.04045,
                             ((rgb_normalized + 0.055) / 1.055) ** 2.4,
                             rgb_normalized / 12.92)
        
        # Convert to XYZ (simplified)
        xyz = np.zeros_like(rgb_linear)
        xyz[:, 0] = rgb_linear[:, 0] * 0.4124564 + rgb_linear[:, 1] * 0.3575761 + rgb_linear[:, 2] * 0.1804375
        xyz[:, 1] = rgb_linear[:, 0] * 0.2126729 + rgb_linear[:, 1] * 0.7151522 + rgb_linear[:, 2] * 0.0721750
        xyz[:, 2] = rgb_linear[:, 0] * 0.0193339 + rgb_linear[:, 1] * 0.1191920 + rgb_linear[:, 2] * 0.9503041
        
        # Quantize in XYZ space
        levels = int(np.ceil(np.power(num_colors, 1/3)))
        levels = max(3, min(8, levels))
        step = 1.0 / levels
        
        xyz_q = (xyz / step).astype(int) * step
        xyz_q = np.clip(xyz_q, 0, levels - 1) * step
        
        # Convert back to RGB (simplified inverse)
        rgb_q = np.zeros_like(xyz_q)
        rgb_q[:, 0] = xyz_q[:, 0] * 3.2404542 - xyz_q[:, 1] * 1.5371385 - xyz_q[:, 2] * 0.4985314
        rgb_q[:, 1] = -xyz_q[:, 0] * 0.9692660 + xyz_q[:, 1] * 1.8760108 + xyz_q[:, 2] * 0.0415560
        rgb_q[:, 2] = xyz_q[:, 0] * 0.0556434 - xyz_q[:, 1] * 0.2040259 + xyz_q[:, 2] * 1.0572252
        
        # Apply inverse gamma
        rgb_q = np.clip(rgb_q, 0, 1)
        rgb_q = np.where(rgb_q > 0.0031308,
                        1.055 * (rgb_q ** (1.0/2.4)) - 0.055,
                        12.92 * rgb_q)
        
        quantized = (rgb_q * 255.0).astype(np.uint8)
    else:
        # Medium/low quality: use faster uniform quantization
        levels = int(np.ceil(np.power(num_colors, 1/3)))
        levels = max(2, min(8, levels))
        step = 256.0 / levels
        
        quantized = ((pixels / step).astype(int) * step).astype(np.uint8)
        quantized = np.clip(quantized, 0, 255)
    
    # Reshape back to image
    return quantized.reshape(h, w, c)


def median_cut_quantize(image: np.ndarray, num_colors: int = 256) -> np.ndarray:
    """
    Quantize colors using median cut algorithm (more accurate but slower)
    Optimized version with vectorized operations
    
    Args:
        image: Image array (H, W, 3) with RGB values
        num_colors: Target number of colors
    
    Returns:
        Quantized image array
    """
    h, w, c = image.shape
    pixels = image.reshape(-1, c).astype(np.float32)
    
    # Build color palette using median cut
    palette = _median_cut(pixels, num_colors)
    
    # Vectorized mapping: find nearest palette color for all pixels at once
    # Use squared Euclidean distance
    pixels_expanded = pixels[:, np.newaxis, :]  # (N, 1, 3)
    palette_expanded = palette[np.newaxis, :, :]  # (1, M, 3)
    
    # Calculate distances: (N, M)
    distances = np.sum((pixels_expanded - palette_expanded) ** 2, axis=2)
    
    # Find nearest palette index for each pixel
    nearest_indices = np.argmin(distances, axis=1)
    
    # Map pixels to palette colors
    quantized = palette[nearest_indices].astype(np.uint8)
    
    return quantized.reshape(h, w, c)


def _median_cut(pixels: np.ndarray, num_colors: int) -> np.ndarray:
    """
    Median cut algorithm for color palette generation
    
    Args:
        pixels: Array of pixels (N, 3)
        num_colors: Target number of colors
    
    Returns:
        Color palette (num_colors, 3)
    """
    # Start with one box containing all pixels
    boxes = [pixels.copy()]
    
    # Split boxes until we have enough colors
    while len(boxes) < num_colors and len(boxes) < len(pixels):
        # Find box with largest range
        largest_box_idx = 0
        largest_range = 0
        
        for i, box in enumerate(boxes):
            if len(box) == 0:
                continue
            # Calculate range for each channel
            ranges = np.max(box, axis=0) - np.min(box, axis=0)
            max_range = np.max(ranges)
            if max_range > largest_range:
                largest_range = max_range
                largest_box_idx = i
        
        # Split largest box
        box_to_split = boxes[largest_box_idx]
        if len(box_to_split) == 0:
            break
        
        # Find channel with largest range
        ranges = np.max(box_to_split, axis=0) - np.min(box_to_split, axis=0)
        channel = np.argmax(ranges)
        
        # Sort by that channel
        sorted_indices = np.argsort(box_to_split[:, channel])
        sorted_box = box_to_split[sorted_indices]
        
        # Split at median
        median_idx = len(sorted_box) // 2
        boxes[largest_box_idx] = sorted_box[:median_idx]
        boxes.append(sorted_box[median_idx:])
    
    # Calculate average color for each box
    palette = []
    for box in boxes:
        if len(box) > 0:
            avg_color = np.mean(box, axis=0).astype(np.uint8)
            palette.append(avg_color)
    
    # If we have fewer colors than requested, pad with black
    while len(palette) < num_colors:
        palette.append(np.array([0, 0, 0], dtype=np.uint8))
    
    return np.array(palette[:num_colors])

