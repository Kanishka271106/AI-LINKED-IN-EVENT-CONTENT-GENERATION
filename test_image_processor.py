import sys
import os
import cv2

# Add the project root to sys.path
sys.path.append(os.getcwd())

from backend.image_processor import ImageProcessor

def test_processor():
    processor = ImageProcessor()
    
    # Use the image provided in user metadata if possible, otherwise look for images in uploads
    test_image = "C:/Users/Earc/.gemini/antigravity/brain/f6f3e9c2-a682-4fe6-acaf-d5d4365396b2/uploaded_media_1770353687569.jpg"
    
    if not os.path.exists(test_image):
        print(f"Test image not found at {test_image}")
        return

    print(f"--- Testing Quality Assessment on {os.path.basename(test_image)} ---")
    quality = processor.assess_quality(test_image)
    for key, value in quality.items():
        print(f"{key}: {value}")
    
    print(f"\n--- Testing Professional Enhancement ---")
    output_path = "C:/Users/Earc/.gemini/antigravity/brain/f6f3e9c2-a682-4fe6-acaf-d5d4365396b2/test_enhanced.jpg"
    enhanced_path = processor.enhance_image(test_image, output_path)
    if os.path.exists(enhanced_path):
        print(f"Enhanced image saved to: {enhanced_path}")
    else:
        print("Failed to save enhanced image.")

if __name__ == "__main__":
    test_processor()
