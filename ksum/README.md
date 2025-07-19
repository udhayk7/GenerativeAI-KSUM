# 🎬 AI ShortStory Studio

Transform your short stories into multimedia presentations with AI-generated scenes, images, narration, music, and video.

## 🌟 Features

- **Story Breakdown**: Uses GPT-4 to analyze and break down stories into visual scenes
- **Image Generation**: Creates AI-generated images for each scene using DALL-E 3
- **Voice Narration**: Generates realistic voice narration with ElevenLabs
- **Background Music**: Adds emotional background music that matches story tone
- **Video Creation**: Compiles everything into a professional narrated slideshow
- **User-Friendly Interface**: Clean, interactive UI built with Streamlit

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- ElevenLabs API key
- (Optional) Suno.ai API key

## 🚀 Quick Start

1. **Clone this repository**

   ```bash
   git clone <repository-url>
   cd ai-shortstory-studio
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API keys**

   Create a `.env` file in the project root:

   ```
   OPENAI_API_KEY=your_openai_api_key
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   SUNO_API_KEY=your_suno_api_key  # Optional
   ```

4. **Run the app**

   ```bash
   streamlit run frontend.py
   ```

5. **Open your browser**

   Navigate to http://localhost:8501

## 🖥️ Usage

1. Enter your short story or select from a template
2. Click "Create My Story Experience"
3. Wait for processing to complete
4. View your generated scenes, images, narration, and final video
5. Download the final video to share

## 📁 Project Structure

```
ai-shortstory-studio/
├── main.py             # Main orchestration script
├── frontend.py         # Streamlit UI
├── requirements.txt    # Dependencies
├── .env.example        # Example environment variables
├── utils/              # Core modules
│   ├── story_to_scenes.py    # Story breakdown with GPT-4
│   ├── image_generator.py    # Image generation with DALL-E
│   ├── voice_generator.py    # Voice narration with ElevenLabs
│   ├── music_generator.py    # Music generation
│   └── video_generator.py    # Video creation with MoviePy
├── prompts/            # Prompt templates
└── outputs/            # Generated media
    ├── images/         # Generated images
    ├── voice/          # Voice narrations
    ├── music/          # Background music
    └── scenes.json     # Scene breakdown
```

## 🛠️ Troubleshooting

- **Missing API keys**: Make sure your `.env` file contains valid API keys
- **Audio issues**: Check that ffmpeg is installed correctly
- **Image generation fails**: Verify your OpenAI API key has access to DALL-E
- **Long processing time**: This is normal, especially for longer stories

## 🔒 API Usage and Costs

This application uses various AI APIs that may incur costs:
- OpenAI API (GPT-4 and DALL-E): ~$0.10-$0.30 per story
- ElevenLabs API: ~$0.03-$0.10 per story
- Suno.ai API (if used): Varies based on usage

## 📝 License

This project is for educational and demonstration purposes. 