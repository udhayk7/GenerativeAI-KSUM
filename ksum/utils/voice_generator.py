import os
import time
import array
import wave
import math
import random
import struct
import numpy as np
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure ElevenLabs API (if available)
elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")

def text_to_speech_tone(text, output_file, duration=None):
    """Generate a simple speech-like tone pattern based on text"""
    # Calculate duration based on text length if not provided
    if duration is None:
        # Estimate reading speed (average English speaker: ~150 words per minute)
        words = len(text.split())
        duration = max(3.0, words / 150 * 60)  # At least 3 seconds
    
    # Audio parameters
    sample_rate = 44100
    amplitude = 20000  # Increased amplitude for more volume
    
    # Generate a seed from the text for consistent results with same text
    seed = sum(ord(c) for c in text[:20])
    random.seed(seed)
    
    # Create different frequencies based on the text sentiment
    # Check for emotional keywords
    lower_text = text.lower()
    if any(word in lower_text for word in ['happy', 'joy', 'exciting', 'thrill']):
        base_freq = random.uniform(350, 440)  # Higher frequency for positive emotion
        pattern = "rising"
    elif any(word in lower_text for word in ['sad', 'sorrow', 'tragic', 'gloomy']):
        base_freq = random.uniform(200, 280)  # Lower frequency for negative emotion
        pattern = "falling"
    elif any(word in lower_text for word in ['tension', 'fear', 'scary', 'danger']):
        base_freq = random.uniform(300, 350)  # Mid frequency with variations for tension
        pattern = "wavering"
    else:
        base_freq = random.uniform(280, 320)  # Neutral frequency
        pattern = "neutral"
        
    # Calculate how many samples we need
    num_samples = int(sample_rate * duration)
    
    # Initialize the audio data array
    audio_data = array.array('h', [0] * num_samples)
    
    # Create speech-like patterns based on the text
    for i in range(num_samples):
        time_point = i / sample_rate  # Time in seconds
        
        # Create a speech-like rhythm
        syllable_rate = 4  # Syllables per second (slowed down)
        syllable_position = (time_point * syllable_rate) % 1.0
        
        # Different amplitude envelope for syllables
        if syllable_position < 0.4:
            syllable_amp = 0.95 + 0.05 * math.sin(syllable_position * 2 * math.pi / 0.4)
        else:
            syllable_amp = 0.85 * (1 - (syllable_position - 0.4) / 0.6)
        
        # Apply different patterns based on text sentiment
        if pattern == "rising":
            freq_mod = base_freq * (1 + 0.1 * time_point / duration)
        elif pattern == "falling":
            freq_mod = base_freq * (1 + 0.1 * (1 - time_point / duration))
        elif pattern == "wavering":
            freq_mod = base_freq * (1 + 0.1 * math.sin(2 * math.pi * time_point / 1.5))
        else:  # neutral
            freq_mod = base_freq
            
        # Add some variations to make it more speech-like
        vibrato = math.sin(2 * math.pi * 5 * time_point)
        vibrato_amount = 0.01
        
        # Add word-like articulation effects
        if int(time_point * 2) % 2 == 0:  # Every 0.5 seconds
            articulation = 0.15 * math.sin(2 * math.pi * 12 * time_point)  # Faster variation for articulation
        else:
            articulation = 0
        
        # Calculate sample value with all modulations
        frequency = freq_mod * (1 + vibrato_amount * vibrato)
        sample_value = syllable_amp * amplitude * math.sin(2 * math.pi * frequency * time_point)
        sample_value += articulation * amplitude  # Add articulation effect
        
        # Add some noise for more realistic speech
        noise = random.uniform(-0.03 * amplitude, 0.03 * amplitude)
        sample_value += noise
        
        # Apply fade-in and fade-out
        fade_duration = min(0.3, duration / 10)
        if time_point < fade_duration:
            fade_factor = time_point / fade_duration
        elif time_point > duration - fade_duration:
            fade_factor = (duration - time_point) / fade_duration
        else:
            fade_factor = 1.0
            
        sample_value *= fade_factor
        
        # Store the sample
        audio_data[i] = int(sample_value)
    
    # Create a WAV file
    with wave.open(output_file, 'w') as wav_file:
        # Set parameters
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 2 bytes for 'h' short
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(audio_data.tobytes())
    
    # Create a stereo version of the audio which works better with MoviePy
    stereo_output = output_file.replace('.wav', '_stereo.wav')
    stereo_data = array.array('h', [0] * num_samples * 2)
    for i in range(num_samples):
        stereo_data[i*2] = audio_data[i]     # Left channel
        stereo_data[i*2+1] = audio_data[i]   # Right channel
    
    with wave.open(stereo_output, 'w') as wav_file:
        wav_file.setnchannels(2)  # Stereo
        wav_file.setsampwidth(2)  # 2 bytes
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(stereo_data.tobytes())
    
    # Replace original with stereo version
    import shutil
    shutil.move(stereo_output, output_file)
    
    return output_file

def generate_silent_wave_file(output_file: str, duration: float = 5.0):
    """
    Generate a silent WAV file
    
    Args:
        output_file: Path to save the audio file
        duration: Duration in seconds
    """
    # Calculate parameters for a basic silent WAV file
    sample_rate = 44100  # standard audio sample rate
    num_channels = 2     # stereo
    sample_width = 2     # 16-bit
    
    # Calculate the number of frames
    num_frames = int(duration * sample_rate)
    
    # Create silent audio data (all zeros)
    silence_data = array.array('h', [0] * num_frames * num_channels)
    
    # Create a Wave_write object
    with wave.open(output_file, 'w') as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(silence_data.tobytes())

def generate_fallback_audio(text: str, output_file: str) -> Optional[str]:
    """
    Create a fallback audio file with speech-like tones
    This is used when the ElevenLabs API is not available
    
    Args:
        text: The text to convert to speech
        output_file: Path to save the audio file
        
    Returns:
        Path to the generated audio file, or None if generation failed
    """
    try:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        print(f"Creating audio for: {text[:50]}...")
        
        # Generate speech-like tones based on the text
        text_to_speech_tone(text, output_file)
        
        print(f"Audio saved to {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Error generating fallback audio: {e}")
        # Last resort fallback - create a silent file
        try:
            generate_silent_wave_file(output_file, duration=3.0)
            return output_file
        except:
            return None

def generate_voice_for_scenes(scenes, output_dir="outputs/voice") -> List[str]:
    """
    Generate voice narrations for all scenes in a story
    
    Args:
        scenes: List of scene dictionaries
        output_dir: Directory to save the generated audio files
        
    Returns:
        List of paths to the generated audio files
    """
    os.makedirs(output_dir, exist_ok=True)
    audio_paths = []
    
    # Clean the output directory first to avoid stale files
    for file in os.listdir(output_dir):
        if file.endswith('.wav') or file.endswith('.mp3'):
            try:
                os.remove(os.path.join(output_dir, file))
            except:
                pass
    
    # For this demo, we'll just use the fallback approach
    for i, scene in enumerate(scenes):
        # Get the narration text from the scene
        narration = scene.get("narration", "")
        
        # Skip if no narration
        if not narration:
            continue
            
        # Generate the voice narration
        output_file = os.path.join(output_dir, f"scene_{i+1}.wav")
        audio_path = generate_fallback_audio(narration, output_file)
            
        if audio_path:
            audio_paths.append(audio_path)
            
        # Add a small delay between files
        time.sleep(0.1)
            
    return audio_paths

if __name__ == "__main__":
    # For testing
    test_text = "The explorer stood at the edge of the ancient ruins, heart pounding with anticipation."
    output_path = "outputs/voice/test_audio.wav"
    generate_fallback_audio(test_text, output_path) 