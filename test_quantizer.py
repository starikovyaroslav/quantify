"""
Test script for quantizer algorithm
"""
import numpy as np
from PIL import Image
from app.quantizer.quantizer import OpticalQuantizer


def create_test_image():
    """Create a test image with gradients"""
    width, height = 200, 200
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Create gradient
    for y in range(height):
        for x in range(width):
            img[y, x] = [
                int(255 * x / width),  # Red gradient
                int(255 * y / height),  # Green gradient
                int(255 * (x + y) / (width + height))  # Blue gradient
            ]
    
    return Image.fromarray(img)


def test_quantizer():
    """Test the quantizer with a sample image"""
    print("Creating test image...")
    test_image = create_test_image()
    
    print("Testing quantizer...")
    quantizer = OpticalQuantizer(width=100, height=100, quality=5)
    
    print("Quantizing...")
    result = quantizer.quantize(test_image)
    
    print("Saving result...")
    quantizer.save_as_utf16(result, "test_output.txt")
    
    print("Done! Check test_output.txt")
    print("\nFirst 10 lines of output:")
    print("\n".join(result.split("\n")[:10]))


if __name__ == "__main__":
    test_quantizer()




