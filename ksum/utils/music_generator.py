import os
import time
import wave
import math
import random
import struct
import array
import numpy as np
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Suno API (if available)
SUNO_API_KEY = os.getenv("SUNO_API_KEY")

# Default music themes based on emotions
DEFAULT_MUSIC_THEMES = {
    "adventure": "Epic orchestral adventure music with heroic brass and strings",
    "mysterious": "Dark ambient mysterious music with subtle piano and ethereal pads",
    "happy": "Cheerful uplifting music with acoustic guitar and light percussion",
    "sad": "Melancholic piano music with soft strings and gentle melody",
    "tense": "Suspenseful music with rising tension and dramatic percussion",
    "romantic": "Emotional romantic music with sweeping strings and piano",
    "magical": "Magical fantasy music with harp arpeggios and light bells",
    "neutral": "Gentle ambient background music with subtle piano"
}

# Path to fallback music samples
FALLBACK_MUSIC_DIR = Path("outputs/music/fallbacks")

def generate_note(frequency, duration, sample_rate=44100, amplitude=10000, fade=0.1):
    """Generate a single musical note"""
    # Number of frames to generate
    num_frames = int(sample_rate * duration)
    
    # Fade in/out duration in frames
    fade_frames = int(fade * sample_rate)
    
    # Generate the waveform (sine wave)
    waveform = []
    for i in range(num_frames):
        # Calculate the current time
        t = i / sample_rate
        
        # Basic sine wave
        sample = amplitude * math.sin(2 * math.pi * frequency * t)
        
        # Apply fade in/out
        if i < fade_frames:
            # Fade in
            sample *= i / fade_frames
        elif i > num_frames - fade_frames:
            # Fade out
            sample *= (num_frames - i) / fade_frames
            
        # Add the sample
        waveform.append(int(sample))
        
    return waveform

def generate_chord(frequencies, duration, sample_rate=44100, amplitude=4000, fade=0.1):
    """Generate a chord from multiple frequencies"""
    num_frames = int(sample_rate * duration)
    waveform = [0] * num_frames
    
    # Generate each note in the chord
    for freq in frequencies:
        note = generate_note(freq, duration, sample_rate, amplitude, fade)
        
        # Add the note to the chord
        for i in range(min(len(note), num_frames)):
            waveform[i] += note[i]
    
    return waveform

def generate_arpeggio(frequencies, duration, notes_per_second=4, sample_rate=44100, amplitude=8000):
    """Generate an arpeggio from the given frequencies"""
    note_duration = 1 / notes_per_second
    num_frames = int(sample_rate * duration)
    waveform = [0] * num_frames
    
    # Calculate how many full arpeggios we can fit
    total_notes = int(duration * notes_per_second)
    
    # Generate each note in the arpeggio
    for i in range(total_notes):
        freq = frequencies[i % len(frequencies)]
        start_frame = int(i * note_duration * sample_rate)
        note = generate_note(freq, note_duration * 1.2, sample_rate, amplitude, fade=0.05)
        
        # Add the note to the waveform
        for j in range(len(note)):
            if start_frame + j < num_frames:
                waveform[start_frame + j] += note[j]
    
    return waveform

def generate_musical_theme(theme, duration=15.0, sample_rate=44100):
    """Generate a musical theme based on the theme description"""
    # Base musical frequencies for different scales
    c_major = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88]  # C D E F G A B
    c_minor = [261.63, 293.66, 311.13, 349.23, 392.00, 415.30, 466.16]  # C D Eb F G Ab Bb
    c_pentatonic = [261.63, 293.66, 329.63, 392.00, 440.00]  # C D E G A
    
    # Choose scale based on theme
    theme_lower = theme.lower()
    if any(word in theme_lower for word in ["happy", "cheerful", "uplifting"]):
        scale = c_major
        tempo = random.uniform(2.5, 4.0)  # Notes per second
        pattern = "arpeggio"
        chords = [
            [scale[0], scale[2], scale[4]],  # I (C E G)
            [scale[3], scale[5], scale[0]],  # IV (F A C)
            [scale[4], scale[6], scale[1]],  # V (G B D)
            [scale[0], scale[2], scale[4]]   # I (C E G)
        ]
    elif any(word in theme_lower for word in ["sad", "melancholic", "sorrow"]):
        scale = c_minor
        tempo = random.uniform(1.5, 2.5)  # Notes per second
        pattern = "chord"
        chords = [
            [scale[0], scale[2], scale[4]],  # i (C Eb G)
            [scale[5], scale[0], scale[2]],  # VI (Ab C Eb)
            [scale[3], scale[5], scale[0]],  # iv (F Ab C)
            [scale[4], scale[6], scale[1]]   # V (G Bb D)
        ]
    elif any(word in theme_lower for word in ["mysterious", "dark", "tension", "suspense"]):
        scale = c_minor
        tempo = random.uniform(1.0, 2.0)  # Notes per second
        pattern = "arpeggio"
        chords = [
            [scale[0], scale[3], scale[6]],  # Diminished (C F Bb)
            [scale[1], scale[4], scale[6]],  # (D G Bb)
            [scale[0], scale[3], scale[6]],  # Repeat
            [scale[4], scale[0], scale[2]]   # (G C Eb)
        ]
    elif any(word in theme_lower for word in ["adventure", "epic", "heroic"]):
        scale = c_major
        tempo = random.uniform(3.0, 4.0)  # Notes per second
        pattern = "mixed"
        chords = [
            [scale[0], scale[2], scale[4]],  # I (C E G)
            [scale[0], scale[2], scale[4]],  # Repeat
            [scale[3], scale[5], scale[0]],  # IV (F A C)
            [scale[4], scale[6], scale[1]]   # V (G B D)
        ]
    else:  # neutral, ambient, etc.
        scale = c_pentatonic
        tempo = random.uniform(2.0, 3.0)  # Notes per second
        pattern = "chord"
        chords = [
            [scale[0], scale[2], scale[4]],  # (C E A)
            [scale[1], scale[3], scale[0]],  # (D G C)
            [scale[4], scale[1], scale[3]],  # (A D G)
            [scale[0], scale[2], scale[4]]   # (C E A)
        ]
    
    # Adjust octaves for more musical range
    bass_octave = 0.5  # One octave down
    high_octave = 2.0  # One octave up
    
    # Create a complete musical piece
    waveform = []
    chord_duration = duration / len(chords)
    
    # Generate different patterns based on the theme
    for chord in chords:
        section_waveform = []
        
        if pattern == "arpeggio":
            # Arpeggios for a flowing feel
            arpeggio_notes = chord + [chord[0] * 2]  # Add root note an octave up
            section_waveform = generate_arpeggio(arpeggio_notes, chord_duration, tempo)
            
            # Add bass notes
            bass_note = generate_note(chord[0] * bass_octave, chord_duration, amplitude=5000, fade=0.2)
            for i in range(min(len(bass_note), len(section_waveform))):
                section_waveform[i] += bass_note[i]
                
        elif pattern == "chord":
            # Sustained chords for emotional themes
            section_waveform = generate_chord(chord, chord_duration, fade=0.3)
            
            # Add rhythmic bass
            bass_duration = chord_duration / 4
            for i in range(4):
                bass_note = generate_note(chord[0] * bass_octave, bass_duration, amplitude=6000, fade=0.1)
                start_frame = int(i * bass_duration * sample_rate)
                for j in range(len(bass_note)):
                    if start_frame + j < len(section_waveform):
                        section_waveform[start_frame + j] += bass_note[j]
        
        else:  # mixed pattern
            # Start with a chord
            chord_sound = generate_chord(chord, chord_duration/2, fade=0.2)
            section_waveform.extend(chord_sound)
            
            # Then do an arpeggio
            arpeggio_notes = chord + [chord[0] * 2]  # Add root note an octave up
            arpeggio_sound = generate_arpeggio(arpeggio_notes, chord_duration/2, tempo)
            section_waveform.extend(arpeggio_sound)
        
        waveform.extend(section_waveform)
    
    # Add some reverb effect (simple delay-based)
    reverb_waveform = [0] * len(waveform)
    delay_ms = 100  # 100ms delay
    delay_frames = int(delay_ms * sample_rate / 1000)
    decay = 0.6  # Decay factor
    
    for i in range(len(waveform)):
        reverb_waveform[i] = waveform[i]
        if i >= delay_frames:
            reverb_waveform[i] += int(waveform[i - delay_frames] * decay)
    
    # Normalize waveform to prevent clipping
    max_amplitude = max(abs(min(reverb_waveform)), abs(max(reverb_waveform)))
    if max_amplitude > 0:
        scale_factor = 32000 / max_amplitude  # Scale to near 16-bit max without clipping
        for i in range(len(reverb_waveform)):
            reverb_waveform[i] = int(reverb_waveform[i] * scale_factor)
    
    return array.array('h', reverb_waveform)

def save_wave_file(waveform, output_file, sample_rate=44100):
    """Save the waveform as a WAV file"""
    with wave.open(output_file, 'w') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(waveform.tobytes())

def generate_music_with_suno(theme, output_file):
    """
    Generate music using Suno.ai API
    
    Args:
        theme: Music theme description
        output_file: Path to save the generated music
        
    Returns:
        Path to the generated music file, or None if generation failed
    """
    try:
        # This is a placeholder for the Suno API implementation
        # Since Suno API details may change, this would need to be updated
        # with the actual API integration
        print(f"Generating music for theme: {theme}")
        print("Note: Suno API implementation is a placeholder")
        
        # Generate music using our internal algorithm instead
        waveform = generate_musical_theme(theme, duration=15.0)
        save_wave_file(waveform, output_file)
        
        print(f"Music saved to {output_file}")
        return output_file
        
    except Exception as e:
        print(f"Error generating music with Suno: {e}")
        return None

def create_fallback_music_dir():
    """Create directory for fallback music if it doesn't exist"""
    os.makedirs(FALLBACK_MUSIC_DIR, exist_ok=True)
    
    # Create placeholder files if no files exist
    if not list(FALLBACK_MUSIC_DIR.glob("*.wav")):
        for theme, tone in [
            ("adventure", "adventure"),
            ("mysterious", "mysterious"),
            ("happy", "happy"),
            ("sad", "sad")
        ]:
            placeholder_file = FALLBACK_MUSIC_DIR / f"{theme}.wav"
            waveform = generate_musical_theme(tone, duration=15.0)
            save_wave_file(waveform, placeholder_file)
                
def get_fallback_music(theme, output_file):
    """
    Use a pre-downloaded music file as fallback
    
    Args:
        theme: Music theme description
        output_file: Path to save the music file
        
    Returns:
        Path to the music file, or None if failed
    """
    try:
        # Create fallback music directory if needed
        create_fallback_music_dir()
        
        # Look for matching fallback music files
        fallback_files = list(FALLBACK_MUSIC_DIR.glob("*.wav"))
        
        if not fallback_files:
            # No fallback files available, create one directly
            waveform = generate_musical_theme(theme, duration=15.0)
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            save_wave_file(waveform, output_file)
            return output_file
            
        # Try to find a matching theme
        matching_files = []
        for file in fallback_files:
            file_theme = file.stem.lower()
            if file_theme in theme.lower() or any(file_theme in t for t in theme.lower().split()):
                matching_files.append(file)
                
        # Choose a random matching file or any file if no match
        chosen_file = random.choice(matching_files) if matching_files else random.choice(fallback_files)
        
        # Copy the file to output location
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(chosen_file, "rb") as src, open(output_file, "wb") as dst:
            dst.write(src.read())
            
        print(f"Using fallback music: {chosen_file.name}")
        return output_file
        
    except Exception as e:
        print(f"Error using fallback music: {e}")
        return None

def get_music_theme_from_scenes(scenes):
    """
    Determine the overall music theme from scene tones
    
    Args:
        scenes: List of scene dictionaries
        
    Returns:
        A music theme description
    """
    # Extract all tones from scenes
    tones = [scene.get("tone", "").lower() for scene in scenes]
    
    # Count tone frequencies
    tone_counts = {}
    for tone in tones:
        if tone in tone_counts:
            tone_counts[tone] += 1
        else:
            tone_counts[tone] = 1
            
    # Find the most common tone
    most_common_tone = max(tone_counts.items(), key=lambda x: x[1])[0] if tone_counts else "neutral"
    
    # Map to a music theme
    for theme_key in DEFAULT_MUSIC_THEMES:
        if theme_key in most_common_tone or most_common_tone in theme_key:
            return DEFAULT_MUSIC_THEMES[theme_key]
            
    # Fallback to neutral theme
    return DEFAULT_MUSIC_THEMES["neutral"]

def generate_music(theme: str, output_file: str) -> Optional[str]:
    """
    Generate background music based on a theme
    
    Args:
        theme: Description of the desired music
        output_file: Path to save the music file
        
    Returns:
        Path to the generated music file, or None if generation failed
    """
    # Try Suno.ai if API key is available
    if SUNO_API_KEY:
        result = generate_music_with_suno(theme, output_file)
        if result:
            return result
            
    # Fallback to local music
    return get_fallback_music(theme, output_file)

def generate_music_for_story(scenes, output_dir="outputs/music") -> Optional[str]:
    """
    Generate background music for a story based on scene tones
    
    Args:
        scenes: List of scene dictionaries
        output_dir: Directory to save the generated music
        
    Returns:
        Path to the generated music file, or None if generation failed
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Get music theme from scenes
    theme = get_music_theme_from_scenes(scenes)
    
    # Generate music
    output_file = os.path.join(output_dir, "bg_music.wav")
    return generate_music(theme, output_file)

if __name__ == "__main__":
    # For testing
    test_scenes = [
        {"tone": "mysterious"},
        {"tone": "tense"},
        {"tone": "mysterious"}
    ]
    
    theme = get_music_theme_from_scenes(test_scenes)
    output_path = "outputs/music/test_music.wav"
    
    print(f"Testing with theme: {theme}")
    generate_music(theme, output_path) 