"""
Optical quantization algorithm
"""
from typing import Optional, Tuple

import numpy as np
from PIL import Image

from app.quantizer.color_quantizer import quantize_colors
from app.quantizer.image_preprocessing import optimize_for_quantization
from app.quantizer.unicode_chars import get_char_by_luminance


class OpticalQuantizer:
    """Optical quantization engine"""

    def __init__(self, width: int = 200, height: int = 200, quality: int = 5):
        """
        Args:
            width: Target width in characters
            height: Target height in characters
            quality: Quality level (1-10, affects color quantization)
        """
        self.width = width
        self.height = height
        self.quality = quality

    def quantize(self, image: Image.Image, use_advanced: bool = True, preprocess: bool = True) -> str:
        """
        Convert image to text using optical quantization

        Args:
            image: PIL Image object
            use_advanced: Use advanced color-aware quantization (better quality)
            preprocess: Apply image preprocessing for better results

        Returns:
            Text string with Unicode characters
        """
        # Preprocess image for better quantization
        if preprocess:
            processed = optimize_for_quantization(image, quality=self.quality)
        else:
            processed = image

        # Resize image with high-quality resampling
        resized = processed.resize((self.width, self.height), Image.Resampling.LANCZOS)

        # Convert to RGB if needed
        if resized.mode != 'RGB':
            resized = resized.convert('RGB')

        # Convert to numpy array
        img_array = np.array(resized, dtype=np.uint8)

        # Advanced color quantization using median cut for better quality
        # Use median cut only for high quality (>=7) to balance speed vs quality
        if use_advanced and self.quality >= 7:
            from app.quantizer.color_quantizer import median_cut_quantize
            num_colors = int(16 + (self.quality - 1) * (256 - 16) / 9)
            quantized = median_cut_quantize(img_array, num_colors=min(256, max(64, num_colors)))
        else:
            # Simple quantization for lower quality/faster processing
            quantized = quantize_colors(img_array, quality=self.quality)

        # Enhanced quantization: use color-aware character selection
        return self._quantize_color_aware(quantized)

    def _quantize_color_aware(self, quantized: np.ndarray) -> str:
        """
        Color-aware quantization that considers both luminance and color information

        Args:
            quantized: Quantized image array (H, W, 3)

        Returns:
            Text string with Unicode characters
        """
        h, w, _ = quantized.shape

        # Calculate luminance using ITU-R BT.709 (more accurate for modern displays)
        luminance = np.dot(quantized[..., :3], [0.2126, 0.7152, 0.0722])
        luminance_normalized = luminance / 255.0

        # Calculate color saturation for better character selection
        # Higher saturation = more color information = use more distinct characters
        max_channel = np.max(quantized[..., :3], axis=2)
        min_channel = np.min(quantized[..., :3], axis=2)
        saturation = np.where(max_channel > 0,
                              (max_channel - min_channel) / max_channel,
                              0.0)
        saturation_normalized = saturation / 255.0

        # Generate text with color-aware character selection (optimized)
        # Adjust luminance based on saturation for high-saturation pixels
        adjusted_lum = np.where(
            saturation_normalized > 0.3,
            np.clip(luminance_normalized * (1.0 + saturation_normalized * 0.1), 0.0, 1.0),
            luminance_normalized
        )

        # Pre-compute character lookup table for faster access
        from app.quantizer.unicode_chars import UNICODE_CHARS
        num_chars = len(UNICODE_CHARS)
        chars_list = [char.char for char in UNICODE_CHARS]

        # Convert to indices and build strings efficiently
        char_indices = (adjusted_lum * (num_chars - 1)).astype(np.int32)
        char_indices = np.clip(char_indices, 0, num_chars - 1)

        # Build lines using list comprehension (faster than nested loops)
        lines = []
        for i in range(h):
            line = ''.join(chars_list[char_indices[i, j]] for j in range(w))
            lines.append(line)

        return '\n'.join(lines)

    def quantize_with_colors(self, image: Image.Image) -> str:
        """
        Convert image to text with color information (ANSI codes)
        This creates a more accurate representation but requires terminal support

        Args:
            image: PIL Image object

        Returns:
            Text string with Unicode characters and ANSI color codes
        """
        # Resize image
        resized = image.resize((self.width, self.height), Image.Resampling.LANCZOS)

        # Convert to RGB if needed
        if resized.mode != 'RGB':
            resized = resized.convert('RGB')

        # Convert to numpy array
        img_array = np.array(resized, dtype=np.uint8)

        # Color quantization
        quantized = quantize_colors(img_array, quality=self.quality)

        # Convert to grayscale for character selection
        gray = np.dot(quantized[..., :3], [0.299, 0.587, 0.114])
        gray_normalized = gray / 255.0

        # Generate text with ANSI color codes
        lines = []
        for i, row in enumerate(gray_normalized):
            line_parts = []
            for j, pixel_lum in enumerate(row):
                char = get_char_by_luminance(pixel_lum)
                r, g, b = quantized[i, j]
                # ANSI 256-color mode
                ansi_code = self._rgb_to_ansi256(r, g, b)
                line_parts.append(f"\033[38;5;{ansi_code}m{char}\033[0m")
            lines.append(''.join(line_parts))

        return '\n'.join(lines)

    def _rgb_to_ansi256(self, r: int, g: int, b: int) -> int:
        """
        Convert RGB to ANSI 256-color code

        Args:
            r, g, b: RGB values (0-255)

        Returns:
            ANSI color code (0-255)
        """
        # If all colors are close, use grayscale
        if abs(r - g) < 3 and abs(g - b) < 3 and abs(r - b) < 3:
            gray = int((r + g + b) / 3)
            if gray < 8:
                return 16
            if gray > 248:
                return 231
            return int(232 + (gray - 8) / 10)

        # Otherwise use 6x6x6 color cube
        r_idx = int(r / 51)
        g_idx = int(g / 51)
        b_idx = int(b / 51)

        # Clamp indices
        r_idx = min(5, max(0, r_idx))
        g_idx = min(5, max(0, g_idx))
        b_idx = min(5, max(0, b_idx))

        return 16 + 36 * r_idx + 6 * g_idx + b_idx

    def save_as_utf16(self, text: str, filepath: str):
        """
        Save text as UTF-16 LE file

        Args:
            text: Text content
            filepath: Output file path
        """
        with open(filepath, 'w', encoding='utf-16-le', newline='') as f:
            f.write(text)

