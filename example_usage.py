"""
Example usage of QuantTxt API
"""
import requests
import time
import os

API_URL = "http://localhost:8000/api/v1"


def quantize_image(image_path: str, width: int = 200, height: int = 200, quality: int = 5):
    """
    Example: Convert image to text
    
    Args:
        image_path: Path to image file
        width: Output width in characters
        height: Output height in characters
        quality: Quality level (1-10)
    """
    # Upload image
    with open(image_path, 'rb') as f:
        files = {'file': (os.path.basename(image_path), f, 'image/jpeg')}
        data = {
            'width': width,
            'height': height,
            'quality': quality
        }
        
        print(f"Uploading {image_path}...")
        response = requests.post(f"{API_URL}/quantize/", files=files, data=data)
        response.raise_for_status()
        
        result = response.json()
        task_id = result['task_id']
        print(f"Task created: {task_id}")
        print(f"Estimated time: {result['estimated_time']} seconds")
        
        # Wait for processing
        while True:
            time.sleep(2)
            status_response = requests.get(f"{API_URL}/quantize/status/{task_id}")
            status_response.raise_for_status()
            status = status_response.json()
            
            print(f"Status: {status['status']}")
            
            if status['status'] == 'completed':
                # Download result
                result_response = requests.get(f"{API_URL}/quantize/result/{task_id}")
                result_response.raise_for_status()
                
                output_path = f"{task_id}_result.txt"
                with open(output_path, 'wb') as out_file:
                    out_file.write(result_response.content)
                
                print(f"Result saved to: {output_path}")
                print("\nTo view the result:")
                print(f"1. Open {output_path} in Notepad (Windows) or TextEdit (Mac)")
                print("2. Set font to Tahoma, size 1pt")
                print("3. Disable word wrap")
                break
            
            elif status['status'] == 'error':
                print(f"Error: {status.get('error', 'Unknown error')}")
                break


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python example_usage.py <image_path> [width] [height] [quality]")
        sys.exit(1)
    
    image_path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    height = int(sys.argv[3]) if len(sys.argv) > 3 else 200
    quality = int(sys.argv[4]) if len(sys.argv) > 4 else 5
    
    if not os.path.exists(image_path):
        print(f"Error: File {image_path} not found")
        sys.exit(1)
    
    quantize_image(image_path, width, height, quality)




