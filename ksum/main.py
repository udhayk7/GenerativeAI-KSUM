import os
import json
import time
from typing import Dict, Any, List, Tuple
from pathlib import Path

# Import utility modules
from utils.story_to_scenes import story_to_scenes
from utils.image_generator import generate_images_for_scenes
from utils.voice_generator import generate_voice_for_scenes
from utils.music_generator import generate_music_for_story
from utils.video_generator import create_story_video

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        "outputs",
        "outputs/images",
        "outputs/voice",
        "outputs/music",
        "outputs/music/fallbacks"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)

def clean_output_directory():
    """Clean output directory to avoid using old files"""
    import glob
    
    # Remove old scene files
    for filepath in glob.glob("outputs/*.json"):
        try:
            os.remove(filepath)
        except:
            pass
    
    # Remove old image files        
    for filepath in glob.glob("outputs/images/scene_*.png"):
        try:
            os.remove(filepath)
        except:
            pass
            
    # Remove old voice files
    for filepath in glob.glob("outputs/voice/scene_*.mp3"):
        try:
            os.remove(filepath)
        except:
            pass
            
    # Remove old video files
    for filepath in glob.glob("outputs/*.mp4"):
        try:
            os.remove(filepath)
        except:
            pass

def generate_script_only(story_text: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    First step: Generate just the script/scenes from the story
    
    Args:
        story_text: The input short story text
        
    Returns:
        Tuple of (path to scenes JSON, list of scene dictionaries)
    """
    try:
        # Clean output directory
        clean_output_directory()
        
        # Ensure directories exist
        ensure_directories()
        
        # Save the original story
        story_path = "outputs/story.txt"
        with open(story_path, "w") as f:
            f.write(story_text)
        
        print("Generating script from story...")
        scenes_path = "outputs/scenes.json"
        scenes = story_to_scenes(story_text, scenes_path)
        
        if not scenes:
            print("Error: Failed to generate script")
            return scenes_path, []
            
        print(f"Generated script with {len(scenes)} scenes")
        return scenes_path, scenes
        
    except Exception as e:
        print(f"Error in generate_script_only: {e}")
        return "outputs/scenes.json", []

def generate_media_from_script(scenes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Second step: After script approval, generate media from the scenes
    
    Args:
        scenes: List of scene dictionaries
        
    Returns:
        Dictionary with paths to all generated files
    """
    # Initialize result paths
    output_paths = {
        "images": [],
        "voice": [],
        "music": "",
        "video": ""
    }
    
    try:
        # Ensure scenes are saved to file
        scenes_path = "outputs/scenes.json"
        with open(scenes_path, "w") as f:
            json.dump(scenes, f, indent=2)
        output_paths["scenes"] = scenes_path
        
        # Generate images for each scene
        print("\nStep 1: Generating images...")
        image_paths = generate_images_for_scenes(scenes)
        output_paths["images"] = image_paths
        
        # Generate voice narrations for each scene
        print("\nStep 2: Creating voice narrations...")
        voice_paths = generate_voice_for_scenes(scenes)
        output_paths["voice"] = voice_paths
        
        # Generate background music
        print("\nStep 3: Composing background music...")
        music_path = generate_music_for_story(scenes)
        if music_path:
            output_paths["music"] = music_path
            
        # Create video
        print("\nStep 4: Assembling final video...")
        video_path = create_story_video(scenes)
        if video_path:
            output_paths["video"] = video_path
            print(f"Video created successfully: {video_path}")
        else:
            print("Failed to create video")
            
        return output_paths
        
    except Exception as e:
        print(f"Error in generate_media_from_script: {e}")
        return output_paths

def process_story(story_text: str) -> Dict[str, str]:
    """
    Combined function for backwards compatibility - generates script and media in one go
    
    Args:
        story_text: The input short story text
        
    Returns:
        Dictionary with paths to all generated files
    """
    # First generate the script
    scenes_path, scenes = generate_script_only(story_text)
    
    # Then generate the media from the script
    output_paths = generate_media_from_script(scenes)
    
    # Add the story path
    output_paths["story"] = "outputs/story.txt"
    
    return output_paths

def main():
    """Entry point when script is run directly"""
    print("🎬 AI ShortStory Studio 🎬")
    print("==========================\n")
    
    # Check if story.txt exists, otherwise use sample
    story_path = "outputs/story.txt"
    if os.path.exists(story_path):
        with open(story_path, "r") as f:
            story = f.read()
    else:
        # Sample story
        story = """
        The explorer stood at the edge of the ancient ruins, heart pounding with anticipation. 
        After years of research, the lost city was finally before them. As they stepped inside 
        the grand entrance, torchlight revealed glittering treasures beyond imagination. 
        But a sudden rumble warned that disturbing this place had awakened something long forgotten, 
        something that had been waiting centuries for an intruder.
        """
    
    # Process the story
    start_time = time.time()
    
    # First generate script only
    print("\n--- Step 1: Generating Script ---\n")
    scenes_path, scenes = generate_script_only(story)
    
    # Ask for user confirmation (in CLI mode)
    print("\nScript generated. Would you like to continue with media generation? (y/n)")
    confirmation = input("> ")
    
    if confirmation.lower() in ["y", "yes"]:
        # Generate media
        print("\n--- Step 2: Generating Media ---\n")
        output_paths = generate_media_from_script(scenes)
    else:
        print("\nMedia generation cancelled.")
        return
    
    end_time = time.time()
    
    # Print summary
    print("\n✅ Processing Complete!")
    print(f"⏱️ Total time: {end_time - start_time:.2f} seconds")
    print("\nOutput files:")
    for key, paths in output_paths.items():
        if isinstance(paths, list):
            print(f"- {key}: {len(paths)} files")
        elif paths:
            print(f"- {key}: {paths}")
    
    print("\nTo view the results, run: streamlit run frontend.py")
    
if __name__ == "__main__":
    main() 