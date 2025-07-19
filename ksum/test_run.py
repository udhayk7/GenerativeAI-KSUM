#!/usr/bin/env python3

import os
import time
import json
from main import generate_script_only, generate_media_from_script
from utils.story_to_scenes import create_advanced_fallback_scenes

# Ensure the output directories exist
for folder in ["outputs", "outputs/images", "outputs/voice", "outputs/music"]:
    os.makedirs(folder, exist_ok=True)

# Sample story for testing
sample_story = """
The young wizard apprentice accidentally mixed the wrong herbs into the potion. 
Instead of creating a simple light spell, the cauldron erupted with swirling blue mist that engulfed the room. 
When it cleared, everything it had touched was now floating gently toward the ceiling, including the master wizard's 
prized magical cat, who looked thoroughly unimpressed with the situation.
"""

def test_direct_scene_generation():
    """Test creating scenes directly with our advanced fallback method"""
    print("\n--- Testing Direct Scene Generation ---\n")
    
    # Generate scenes using our advanced fallback method
    scenes = create_advanced_fallback_scenes(sample_story, num_scenes=3)
    
    # Save to file
    scenes_path = "outputs/direct_scenes.json"
    with open(scenes_path, 'w') as f:
        json.dump(scenes, f, indent=2)
    
    print(f"Generated {len(scenes)} scenes directly")
    
    # Show the scenes
    print("\nGenerated Scenes:")
    for i, scene in enumerate(scenes):
        print(f"\nScene {i+1}:")
        print(f"Description: {scene['description']}")
        print(f"Narration: {scene['narration']}")
        print(f"Tone: {scene['tone']}")
    
    return scenes, scenes_path

def test_script_generation():
    """Test the script generation process"""
    print("\n--- Testing Script Generation ---\n")
    
    # Use our API or fallback to generate a script
    scenes_path, scenes = generate_script_only(sample_story)
    
    print(f"Generated script with {len(scenes)} scenes")
    
    # Show the scenes
    print("\nGenerated Scenes:")
    for i, scene in enumerate(scenes):
        print(f"\nScene {i+1}:")
        print(f"Description: {scene['description']}")
        print(f"Narration: {scene['narration']}")
        print(f"Tone: {scene['tone']}")
    
    return scenes, scenes_path

def test_media_generation(scenes):
    """Test media generation from scenes"""
    print("\n--- Testing Media Generation ---\n")
    
    # Generate media from the script
    output_paths = generate_media_from_script(scenes)
    
    # Print the results
    print("\nGenerated Media:")
    for key, paths in output_paths.items():
        if isinstance(paths, list):
            print(f"- {key}: {len(paths)} files")
            for path in paths:
                print(f"  - {path}")
        else:
            print(f"- {key}: {paths}")
    
    return output_paths

def main():
    """Run the complete test"""
    print("\n=== AI ShortStory Studio Test ===\n")
    
    start_time = time.time()
    
    # Test direct scene generation
    scenes, _ = test_direct_scene_generation()
    
    # Test script generation
    # scenes, _ = test_script_generation()
    
    # Test media generation
    output_paths = test_media_generation(scenes)
    
    end_time = time.time()
    print(f"\nTest completed in {end_time - start_time:.2f} seconds")
    
    if output_paths.get("video"):
        print(f"\nVideo created successfully at {output_paths['video']}")
        print("You can open this video to see the final result.")

if __name__ == "__main__":
    main() 