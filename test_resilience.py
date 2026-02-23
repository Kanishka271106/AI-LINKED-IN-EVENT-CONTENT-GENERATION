import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from backend.image_processor import ImageProcessor

def test_failure_resilience():
    processor = ImageProcessor()
    
    # Test with a mix of non-existent and potentially valid (but empty) paths
    test_paths = [
        "non_existent_image_1.jpg",
        "non_existent_image_2.png"
    ]
    
    print("\nTesting batch_process with non-existent files...")
    try:
        results = processor.batch_process(test_paths)
        
        print(f"Total processed: {results['total_images']}")
        print(f"All results length: {len(results['all_results'])}")
        
        for i, res in enumerate(results['all_results']):
            print(f"Result {i+1} ({res['filename']}): error='{res.get('error', 'None')}', quality={res['quality_score']}")
            
        if len(results['all_results']) == 2:
            print("\n[SUCCESS] ImageProcessor handled missing files without crashing.")
        else:
            print("\n[FAILURE] Unexpected results length.")
            
    except Exception as e:
        print(f"\n[FAILURE] ImageProcessor crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_failure_resilience()
