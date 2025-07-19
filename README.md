# AI ShortStory Studio

Transform your short stories into multimedia presentations with AI-powered technology.

## Overview

AI ShortStory Studio is a comprehensive tool that converts text stories into engaging visual and audio experiences. The application:

1. Breaks down stories into cinematic scenes
2. Generates compelling images for each scene
3. Creates voice narration for each scene
4. Composes background music matching the story's tone
5. Compiles everything into a narrated slideshow video

## Features

- **Scene Generation**: Uses AI to convert stories into properly segmented visual scenes
- **Image Creation**: Generates visual representations for each scene with appropriate tone and style
- **Voice Narration**: Converts scene text to speech with appropriate pacing and emotional tone
- **Music Composition**: Creates background music that matches the story's emotional tone
- **Video Compilation**: Combines all elements into a polished video presentation
- **Fallback Systems**: Gracefully handles API failures with sophisticated local generation alternatives

## How It Works

The application follows a two-step process:

1. **Script Generation**: The story is analyzed and broken down into cinematic scenes
   - Users can review and approve the script before proceeding

2. **Media Generation**: Once approved, the script is used to create:
   - Visual images for each scene
   - Voice narration for each scene text
   - Background music matching the story's tone
   - A final compiled video

## Dependencies

- Python 3.9+
- OpenAI API (for GPT-4 and DALL·E 3)
- ElevenLabs API (optional, for voice generation)
- Suno.ai API (optional, for music generation)
- MoviePy (for video creation)
- Streamlit (for UI)
- Additional Python libraries: numpy, Pillow, nltk, etc.

## Installation

1. Clone this repository:
```bash
git clone https://github.com/udhayk7/GenerativeAI-KSUM.git
cd GenerativeAI-KSUM
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file with your API keys (optional):
```
OPENAI_API_KEY=your_openai_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
SUNO_API_KEY=your_suno_api_key
```

## Usage

1. Run the Streamlit frontend:
```bash
streamlit run ksum/frontend.py
```

2. Enter a story in the text area
3. Click "Generate Script" to create the scene breakdown
4. Review and approve the generated script
5. Click "Create Media" to generate images, audio, and final video
6. Download or watch the final video presentation

## API-Free Operation

The system includes sophisticated fallback mechanisms to work even without API access:

- **Script Generation**: Local scene analysis with advanced text segmentation
- **Image Generation**: Creates visual representations using character silhouettes, settings, and scene elements
- **Audio Generation**: Synthesizes speech-like tones that match text content and emotional context
- **Music Generation**: Creates thematic background music using procedural composition

## Directory Structure

- `ksum/` - Main application directory
  - `frontend.py` - Streamlit UI
  - `main.py` - Core application logic
  - `utils/` - Utility modules
    - `story_to_scenes.py` - Scene breakdown logic
    - `image_generator.py` - Image generation
    - `voice_generator.py` - Voice narration
    - `music_generator.py` - Background music creation
    - `video_generator.py` - Final video compilation
  - `prompts/` - GPT-4 system prompts
  - `outputs/` - Generated media (images, audio, final video)

## License

This project is open source and available under the [MIT License](LICENSE).
