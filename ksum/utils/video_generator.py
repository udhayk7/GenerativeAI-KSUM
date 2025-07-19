import os
import time
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeAudioClip, 
    concatenate_videoclips, CompositeVideoClip, TextClip,
    VideoFileClip, ColorClip
)

def create_placeholder_image(text, width=1024, height=1024):
    """Create a placeholder image with text"""
    # Create a new image with a gradient background
    img = Image.new('RGB', (width, height), color=(73, 109, 137))
    d = ImageDraw.Draw(img)
    
    # Try to load a font, use default if not available
    try:
        font = ImageFont.truetype("Arial", 32)
    except IOError:
        font = ImageFont.load_default()
    
    # Add the scene description text
    text_wrap = text[:200] + "..." if len(text) > 200 else text
    lines = [text_wrap[i:i+40] for i in range(0, len(text_wrap), 40)]
    
    y_position = height // 2 - len(lines) * 20
    for line in lines:
        d.text((width//2, y_position), line, fill=(255, 255, 255), font=font, anchor="mm")
        y_position += 40
        
    # Add a title at the top
    d.text((width//2, 50), "AI ShortStory Studio", fill=(255, 255, 255), font=font, anchor="mm")
    
    return img

def create_text_image(text, width=1024, height=200, bg_color=(0, 0, 0, 128)):
    """Create a text overlay image without requiring ImageMagick"""
    # Create a new image with a semi-transparent background
    img = Image.new('RGBA', (width, height), bg_color)
    d = ImageDraw.Draw(img)
    
    # Try to load a font, use default if not available
    try:
        font = ImageFont.truetype("Arial", 24)
    except IOError:
        font = ImageFont.load_default()
    
    # Add the text
    text_wrap = text[:100] + "..." if len(text) > 100 else text
    lines = []
    words = text_wrap.split()
    line = []
    for word in words:
        line.append(word)
        text_width = d.textlength(" ".join(line), font=font)
        if text_width > width - 40:
            line.pop()
            lines.append(" ".join(line))
            line = [word]
    if line:
        lines.append(" ".join(line))
    
    # Draw the text
    y_position = 20
    for line in lines:
        text_width = d.textlength(line, font=font)
        d.text(((width - text_width) // 2, y_position), line, fill=(255, 255, 255), font=font)
        y_position += 30
    
    return img

def create_silent_audio(duration=5.0):
    """Create a silent audio clip of specified duration"""
    from moviepy.audio.AudioClip import AudioClip
    import numpy as np
    
    # Create a silent audio clip
    silent_audio = AudioClip(
        make_frame=lambda t: np.zeros((2,)),
        duration=duration
    )
    return silent_audio

def ensure_audio_duration(audio_clip, target_duration):
    """Ensure audio clip matches the target duration"""
    if audio_clip.duration > target_duration:
        # Trim the audio
        return audio_clip.subclip(0, target_duration)
    elif audio_clip.duration < target_duration:
        # Extend with silence
        silence = create_silent_audio(target_duration - audio_clip.duration)
        return CompositeAudioClip([audio_clip, silence.set_start(audio_clip.duration)])
    return audio_clip

def create_slideshow(
    scenes: List[Dict[str, Any]], 
    image_paths: List[str], 
    audio_paths: List[str], 
    music_path: Optional[str] = None,
    output_file: str = "outputs/final_video.mp4",
    fade_duration: float = 1.0,
    music_volume: float = 0.2  # Reduced music volume so voice is more prominent
) -> Optional[str]:
    """
    Create a narrated slideshow video from scenes, images, voiceovers and background music
    
    Args:
        scenes: List of scene dictionaries
        image_paths: List of paths to the generated images
        audio_paths: List of paths to the generated voice narrations
        music_path: Path to the background music (optional)
        output_file: Path to save the final video
        fade_duration: Duration of fade transitions in seconds
        music_volume: Volume level for background music (0.0 to 1.0)
        
    Returns:
        Path to the generated video file, or None if generation failed
    """
    try:
        print("Creating narrated slideshow...")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Create a list to store video clips
        video_clips = []
        
        # Check if we have enough files - if not, create placeholders
        if not image_paths and scenes:
            # Create placeholder images
            print("Creating placeholder images for scenes...")
            for i, scene in enumerate(scenes):
                desc = scene.get("description", f"Scene {i+1}")
                # Create a placeholder file
                output_path = os.path.join("outputs/images", f"scene_{i+1}.png")
                img = create_placeholder_image(desc)
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                img.save(output_path)
                image_paths.append(output_path)
                
        # Process each scene
        for i, scene in enumerate(scenes):
            scene_duration = 8.0  # Default duration in seconds
            
            # Get image path for this scene
            scene_image_path = None
            if i < len(image_paths):
                scene_image_path = image_paths[i]
            else:
                # Create a placeholder image
                desc = scene.get("description", f"Scene {i+1}")
                temp_img = create_placeholder_image(desc)
                temp_path = f"outputs/images/temp_scene_{i+1}.png"
                os.makedirs(os.path.dirname(temp_path), exist_ok=True)
                temp_img.save(temp_path)
                scene_image_path = temp_path
            
            # Get audio path for this scene
            scene_audio_path = None
            if i < len(audio_paths) and os.path.exists(audio_paths[i]):
                scene_audio_path = audio_paths[i]
            
            try:
                # Create image clip
                img_clip = ImageClip(scene_image_path)
                
                # First set a fixed duration to avoid timing issues
                img_clip = img_clip.set_duration(scene_duration)
                
                # Set audio if available
                if scene_audio_path:
                    try:
                        # Create a silent backup audio just in case
                        silent_audio = create_silent_audio(scene_duration)
                        
                        try:
                            # Load the audio file directly
                            audio_clip = AudioFileClip(scene_audio_path)
                            
                            # Fix duration issues by ensuring audio is not longer than image
                            audio_duration = min(audio_clip.duration, scene_duration)
                            scene_duration = max(scene_duration, audio_duration)
                            
                            # Ensure both clips have the same duration
                            audio_clip = ensure_audio_duration(audio_clip, scene_duration)
                            img_clip = img_clip.set_duration(scene_duration)
                            
                            # Boost voice volume
                            audio_clip = audio_clip.volumex(1.5)
                            img_clip = img_clip.set_audio(audio_clip)
                        except Exception as e:
                            print(f"Error loading audio: {e}")
                            img_clip = img_clip.set_audio(silent_audio)
                    except Exception as audio_error:
                        print(f"Audio error: {audio_error}")
                        # Last resort fallback
                        img_clip = img_clip.set_duration(scene_duration)
                else:
                    # No audio available, use silent clip
                    silent_audio = create_silent_audio(scene_duration)
                    img_clip = img_clip.set_audio(silent_audio)
                
                # Make sure duration is properly set after audio handling
                img_clip = img_clip.set_duration(scene_duration)
                
                # Add a fade in/out effect
                img_clip = img_clip.crossfadein(fade_duration)
                img_clip = img_clip.crossfadeout(fade_duration)
                
                # Add narration text overlay using our custom PIL function
                narration = scene.get("narration", "")
                if narration:
                    try:
                        # Create text image overlay
                        text_img_path = f"outputs/images/text_overlay_{i+1}.png"
                        text_img = create_text_image(narration, width=img_clip.w)
                        text_img.save(text_img_path)
                        
                        # Load text image as clip
                        text_clip = ImageClip(text_img_path)
                        text_clip = text_clip.set_duration(img_clip.duration)
                        text_clip = text_clip.set_position(('center', 'bottom'))
                        
                        # Composite image and text
                        img_clip = CompositeVideoClip([img_clip, text_clip])
                        
                        # Clean up temporary text image
                        try:
                            os.remove(text_img_path)
                        except:
                            pass
                    except Exception as text_error:
                        print(f"Error adding text overlay: {text_error}")
                
                # Add clip to list
                video_clips.append(img_clip)
                
            except Exception as e:
                print(f"Error processing scene {i+1}: {e}")
                # Create a text clip as fallback
                try:
                    # Create a colored background as fallback
                    color_clip = ColorClip(size=(1024, 1024), color=(0, 0, 128))
                    color_clip = color_clip.set_duration(scene_duration)
                    silent_audio = create_silent_audio(scene_duration)
                    color_clip = color_clip.set_audio(silent_audio)
                    video_clips.append(color_clip)
                except:
                    print(f"Complete fallback failed for scene {i+1}")
        
        if not video_clips:
            print("No valid video clips were created")
            return None
            
        # Concatenate all video clips
        final_clip = concatenate_videoclips(video_clips, method="compose")
        
        # Add background music if provided
        if music_path and os.path.exists(music_path):
            try:
                # Load background music
                music_clip = AudioFileClip(music_path)
                
                # Loop the music if needed to match video duration
                if music_clip.duration < final_clip.duration:
                    # Create multiple copies of the music
                    num_loops = int(np.ceil(final_clip.duration / music_clip.duration))
                    music_parts = [music_clip] * num_loops
                    extended_music = concatenate_videoclips(music_parts).subclip(0, final_clip.duration)
                    music_clip = extended_music
                else:
                    # Cut music to match video duration
                    music_clip = music_clip.subclip(0, final_clip.duration)
                
                # Set volume
                music_clip = music_clip.volumex(music_volume)
                
                # Mix audio - ensure voice audio is preserved
                if final_clip.audio:
                    # Prevent issues with CompositeAudioClip by making copies
                    try:
                        final_audio = CompositeAudioClip([final_clip.audio, music_clip])
                        final_clip = final_clip.set_audio(final_audio)
                    except Exception as audio_mix_error:
                        print(f"Error mixing audio: {audio_mix_error}")
                        # Just use original audio if mixing fails
                else:
                    # If no voice audio, just use music
                    final_clip = final_clip.set_audio(music_clip)
                
            except Exception as e:
                print(f"Error adding background music: {e}")
        
        # Write final video file
        print(f"Writing video to {output_file}...")
        final_clip.write_videofile(
            output_file, 
            codec="libx264", 
            audio_codec="aac", 
            fps=24,
            threads=4,
            preset="medium"
        )
        
        print("Video created successfully!")
        return output_file
        
    except Exception as e:
        print(f"Error creating slideshow: {e}")
        import traceback
        traceback.print_exc()
        return None

def add_title_screen(
    video_path: str, 
    title: str, 
    output_file: str = None,
    duration: float = 3.0
) -> Optional[str]:
    """
    Add a title screen to the beginning of a video
    
    Args:
        video_path: Path to the input video
        title: Title text to display
        output_file: Path to save the new video
        duration: Duration of title screen in seconds
        
    Returns:
        Path to the output video, or None if failed
    """
    try:
        if not output_file:
            output_file = video_path.replace(".mp4", "_with_title.mp4")
            
        # Load the video
        video_clip = VideoFileClip(video_path)
        
        # Create title text
        txt_clip = TextClip(
            title,
            fontsize=70, color='white',
            bg_color='black',
            size=video_clip.size,
            method='caption'
        )
        txt_clip = txt_clip.set_duration(duration)
        
        # Add a fade out
        txt_clip = txt_clip.crossfadeout(1.0)
        
        # Concatenate title with video
        final_clip = concatenate_videoclips([txt_clip, video_clip])
        
        # Write final video
        final_clip.write_videofile(
            output_file,
            codec="libx264",
            audio_codec="aac",
            fps=24
        )
        
        return output_file
        
    except Exception as e:
        print(f"Error adding title screen: {e}")
        return None
    
def create_story_video(
    scenes: List[Dict[str, Any]],
    output_dir: str = "outputs"
) -> Optional[str]:
    """
    Create a complete story video from generated scenes and media
    
    Args:
        scenes: List of scene dictionaries
        output_dir: Directory containing generated media
        
    Returns:
        Path to the final video, or None if failed
    """
    try:
        # Collect image paths
        image_dir = os.path.join(output_dir, "images")
        image_paths = []
        for i in range(len(scenes)):
            img_path = os.path.join(image_dir, f"scene_{i+1}.png")
            if os.path.exists(img_path):
                image_paths.append(img_path)
                
        # Collect audio paths
        audio_dir = os.path.join(output_dir, "voice")
        audio_paths = []
        for i in range(len(scenes)):
            # Try both WAV and MP3 format
            wav_path = os.path.join(audio_dir, f"scene_{i+1}.wav")
            mp3_path = os.path.join(audio_dir, f"scene_{i+1}.mp3")
            
            if os.path.exists(wav_path):
                audio_paths.append(wav_path)
            elif os.path.exists(mp3_path):
                audio_paths.append(mp3_path)
                
        # Check if we have music
        music_path = os.path.join(output_dir, "music", "bg_music.wav")
        if not os.path.exists(music_path):
            # Try MP3 format
            mp3_music_path = os.path.join(output_dir, "music", "bg_music.mp3") 
            if os.path.exists(mp3_music_path):
                music_path = mp3_music_path
            else:
                music_path = None
            
        # Create output video path
        output_file = os.path.join(output_dir, "final_video.mp4")
        
        # Create the slideshow
        return create_slideshow(
            scenes=scenes,
            image_paths=image_paths,
            audio_paths=audio_paths,
            music_path=music_path,
            output_file=output_file
        )
        
    except Exception as e:
        print(f"Error creating story video: {e}")
        return None
        
if __name__ == "__main__":
    # For testing
    from pathlib import Path
    
    # Create test directories and dummy files
    os.makedirs("outputs/images", exist_ok=True)
    os.makedirs("outputs/voice", exist_ok=True)
    os.makedirs("outputs/music", exist_ok=True)
    
    # Create dummy scenes
    test_scenes = [
        {"description": "Scene 1", "narration": "This is scene 1"},
        {"description": "Scene 2", "narration": "This is scene 2"}
    ]
    
    print("Note: This is just a placeholder. Real implementation requires media files.") 