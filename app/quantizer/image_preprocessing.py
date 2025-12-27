"""
Image preprocessing for better quantization results
"""
from typing import Optional

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


def preprocess_image(
    image: Image.Image,
    enhance_contrast: bool = True,
    enhance_sharpness: bool = False,
    denoise: bool = False
) -> Image.Image:
    """
    Preprocess image for better quantization results

    Args:
        image: Input PIL Image
        enhance_contrast: Enhance contrast for better color separation
        enhance_sharpness: Enhance sharpness (use with caution)
        denoise: Apply denoising filter

    Returns:
        Preprocessed PIL Image
    """
    processed = image.copy()

    # Convert to RGB if needed
    if processed.mode != 'RGB':
        processed = processed.convert('RGB')

    # Denoise if requested
    if denoise:
        processed = processed.filter(ImageFilter.MedianFilter(size=3))

    # Enhance contrast for better color quantization
    if enhance_contrast:
        enhancer = ImageEnhance.Contrast(processed)
        # Slight contrast boost (1.1 = 10% increase)
        processed = enhancer.enhance(1.1)

    # Enhance sharpness (optional, can cause artifacts)
    if enhance_sharpness:
        enhancer = ImageEnhance.Sharpness(processed)
        processed = enhancer.enhance(1.05)  # Very slight sharpening

    return processed


def adaptive_histogram_equalization(image: Image.Image) -> Image.Image:
    """
    Apply adaptive histogram equalization for better contrast

    Args:
        image: Input PIL Image

    Returns:
        Processed PIL Image
    """
    from PIL import ImageOps

    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')

    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
    # Using PIL's equalize as a simpler alternative
    r, g, b = image.split()
    r_eq = ImageOps.equalize(r)
    g_eq = ImageOps.equalize(g)
    b_eq = ImageOps.equalize(b)

    return Image.merge('RGB', (r_eq, g_eq, b_eq))


def optimize_for_quantization(image: Image.Image, quality: int = 5) -> Image.Image:
    """
    Optimize image specifically for quantization

    Args:
        image: Input PIL Image
        quality: Quality level (1-10)

    Returns:
        Optimized PIL Image
    """
    # Higher quality = more preprocessing
    if quality >= 7:
        # High quality: full preprocessing
        processed = preprocess_image(
            image,
            enhance_contrast=True,
            enhance_sharpness=False,  # Can cause artifacts
            denoise=True
        )
    elif quality >= 5:
        # Medium quality: moderate preprocessing
        processed = preprocess_image(
            image,
            enhance_contrast=True,
            enhance_sharpness=False,
            denoise=False
        )
    else:
        # Low quality: minimal preprocessing for speed
        processed = preprocess_image(
            image,
            enhance_contrast=False,
            enhance_sharpness=False,
            denoise=False
        )

    return processed

