from backend.caption_generator import CaptionGenerator

def test_generation():
    print("Testing CaptionGenerator...")
    try:
        generator = CaptionGenerator()
        print(f"Initialized. Configured: {generator.is_configured}")
        
        # Test 1: Simple generation
        caption1 = generator.generate_caption("Test Event", 5)
        print("\nTest 1 (Default):")
        print(caption1)
        
        # Test 2: With custom context (Event name override)
        caption2 = generator.generate_caption("Default Event", 3, custom_context="PyExpo 2026")
        print("\nTest 2 (Custom Event Name):")
        print(caption2)
        if "PyExpo 2026" in caption2:
            print("SUCCESS: Custom event name respected.")
        else:
            print("FAILURE: Custom event name ignored.")
            
        # Test 3: With long context
        caption3 = generator.generate_caption("Networking Mixer", 4, custom_context="Discussing the future of AI and agentic workflows with the community.")
        print("\nTest 3 (Long Context):")
        print(caption3)
        if "agentic workflows" in caption3:
            print("SUCCESS: Long context included.")
        else:
            print("FAILURE: Long context ignored.")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_generation()
