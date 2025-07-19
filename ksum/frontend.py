import streamlit as st
import os
import json
import time
from pathlib import Path
from main import process_story, generate_script_only, generate_media_from_script

# Set page config
st.set_page_config(
    page_title="AI ShortStory Studio",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Apply custom CSS for better styling
st.markdown("""
<style>
    .main-title {
        text-align: center;
        font-weight: bold;
        color: #1E3A8A;
    }
    .stProgress .st-bo {
        background-color: #1E3A8A;
    }
    .story-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    .output-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        border: 1px solid #e9ecef;
    }
    .step-header {
        color: #1E3A8A;
        font-weight: 600;
    }
    .script-box {
        background-color: #f0f7ff;
        padding: 15px;
        border-radius: 5px;
        border-left: 4px solid #1E3A8A;
        margin: 10px 0;
    }
    .scene-description {
        background-color: #f5f5f5;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .scene-narration {
        color: #444;
        font-style: italic;
        margin: 5px 0;
    }
    .approve-button {
        background-color: #28a745;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        text-align: center;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Sample story templates
STORY_TEMPLATES = {
    "Adventure": "The explorer stood at the edge of the ancient ruins, heart pounding with anticipation. After years of research, the lost city was finally before them. As they stepped inside the grand entrance, torchlight revealed glittering treasures beyond imagination. But a sudden rumble warned that disturbing this place had awakened something long forgotten, something that had been waiting centuries for an intruder.",
    "Mystery": "The detective examined the curious note left at the crime scene. The handwriting was elegant, the message cryptic: 'When midnight strikes thrice, truth will emerge from shadow.' The room showed no signs of forced entry, yet the valuable painting had vanished. More puzzling still was the single white glove placed precisely where the artwork had hung.",
    "Fantasy": "The young wizard apprentice accidentally mixed the wrong herbs into the potion. Instead of creating a simple light spell, the cauldron erupted with swirling blue mist that engulfed the room. When it cleared, everything it had touched was now floating gently toward the ceiling, including the master wizard's prized magical cat, who looked thoroughly unimpressed with the situation.",
}

# Initialize session state
if "story_submitted" not in st.session_state:
    st.session_state.story_submitted = False
if "script_generated" not in st.session_state:
    st.session_state.script_generated = False
if "script_approved" not in st.session_state:
    st.session_state.script_approved = False
if "processing_complete" not in st.session_state:
    st.session_state.processing_complete = False
if "progress" not in st.session_state:
    st.session_state.progress = 0
if "scenes" not in st.session_state:
    st.session_state.scenes = []
if "current_step" not in st.session_state:
    st.session_state.current_step = None
if "output_paths" not in st.session_state:
    st.session_state.output_paths = {}

# Header
st.markdown("<h1 class='main-title'>🎬 AI ShortStory Studio</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Transform your short stories into multimedia presentations with AI</p>", unsafe_allow_html=True)

# Story Input Section (only show if script not yet generated)
if not st.session_state.script_generated:
    st.markdown("<h3 class='step-header'>Step 1: Enter Your Story</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("<div class='story-container'>", unsafe_allow_html=True)
        
        # Template selection or custom story
        template_option = st.selectbox(
            "Choose a template or write your own story:",
            ["Write your own story", "Adventure", "Mystery", "Fantasy"]
        )
        
        if template_option == "Write your own story":
            story_text = st.text_area("Enter your short story (100-500 words recommended):", 
                                   height=200,
                                   placeholder="Once upon a time...")
        else:
            story_text = st.text_area("Edit the template or use as is:", 
                                   value=STORY_TEMPLATES[template_option],
                                   height=200)
        
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown("<div style='padding: 20px; background-color: #e9f7fe; border-radius: 10px; height: 100%;'>", unsafe_allow_html=True)
        st.markdown("### Tips:")
        st.markdown("- Keep your story between 100-500 words")
        st.markdown("- Include descriptive visual elements")
        st.markdown("- Consider emotional moments that would benefit from music")
        st.markdown("- Stories with clear scene transitions work best")
        st.markdown("</div>", unsafe_allow_html=True)

    # Generate script button
    if st.button("✨ Generate Script", type="primary", use_container_width=True):
        if story_text and len(story_text.strip()) > 50:
            st.session_state.story_submitted = True
            
            # Create folders if they don't exist
            for folder in ["outputs", "outputs/images", "outputs/voice", "outputs/music"]:
                os.makedirs(folder, exist_ok=True)
                
            # Save the story to a file
            with open("outputs/story.txt", "w") as f:
                f.write(story_text)
            
            # Generate script only
            with st.spinner("Creating your script..."):
                st.session_state.current_step = "Breaking story into scenes"
                st.session_state.progress = 0.3
                
                # Call function to generate script only
                scenes_path, scenes = generate_script_only(story_text)
                
                st.session_state.scenes = scenes
                st.session_state.output_paths = {"scenes": scenes_path}
                st.session_state.script_generated = True
                st.session_state.progress = 0.5
            
            st.rerun()
        else:
            st.error("Please enter a longer story (at least 50 characters).")

# Script Review and Approval Section (only show if script is generated but not approved)
elif st.session_state.script_generated and not st.session_state.script_approved:
    st.markdown("<h3 class='step-header'>Step 2: Review and Approve Script</h3>", unsafe_allow_html=True)
    
    # Display the generated script for review
    st.markdown("<div class='output-container'>", unsafe_allow_html=True)
    st.subheader("Your Generated Script")
    
    for i, scene in enumerate(st.session_state.scenes):
        st.markdown(f"<div class='script-box'>", unsafe_allow_html=True)
        st.markdown(f"#### Scene {i+1}")
        st.markdown(f"<div class='scene-description'><strong>Visual Description:</strong> {scene.get('description', '')}</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='scene-narration'><strong>Narration:</strong> \"{scene.get('narration', '')}\"</div>", unsafe_allow_html=True)
        st.markdown(f"<strong>Emotional Tone:</strong> {scene.get('tone', 'neutral')}")
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Approve button
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("✏️ Edit Story", use_container_width=True):
            # Reset state to go back to story input
            st.session_state.script_generated = False
            st.session_state.script_approved = False
            st.session_state.progress = 0
            st.rerun()
            
    with col2:
        if st.button("✅ Approve Script & Create Media", type="primary", use_container_width=True):
            st.session_state.script_approved = True
            st.session_state.current_step = "Generating images"
            st.session_state.progress = 0.5
            
            # Start the media generation process
            with st.spinner("Creating your multimedia experience..."):
                # Process the approved script to generate media
                output_paths = generate_media_from_script(st.session_state.scenes)
                st.session_state.output_paths.update(output_paths)
                
                st.session_state.processing_complete = True
                st.session_state.progress = 1.0
            
            st.rerun()

# Progress tracking if script approved but processing is not complete
elif st.session_state.script_approved and not st.session_state.processing_complete:
    st.markdown("<h3 class='step-header'>Creating Your Media</h3>", unsafe_allow_html=True)
    progress_bar = st.progress(st.session_state.progress)
    
    st.info(f"Current step: {st.session_state.current_step}")
    
    # Simulate progress updates (in real implementation, this would be updated by the background process)
    if st.session_state.progress < 1.0:
        time.sleep(0.1)
        st.session_state.progress += 0.01
        if st.session_state.progress >= 0.6 and st.session_state.current_step == "Generating images":
            st.session_state.current_step = "Creating voice narration"
        elif st.session_state.progress >= 0.75 and st.session_state.current_step == "Creating voice narration":
            st.session_state.current_step = "Composing background music"
        elif st.session_state.progress >= 0.9 and st.session_state.current_step == "Composing background music":
            st.session_state.current_step = "Assembling final video"
            
        st.rerun()

# Results section (shown when processing is complete)
if st.session_state.processing_complete:
    st.markdown("<h3 class='step-header'>Your Story Experience</h3>", unsafe_allow_html=True)
    
    # Display scenes and generated content
    for i, scene in enumerate(st.session_state.scenes):
        with st.expander(f"Scene {i+1}", expanded=True):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Display the scene description
                st.markdown(f"**Description:**")
                st.markdown(scene.get("description", ""))
                
                # Display voice narration if available
                voice_path = os.path.join("outputs", "voice", f"scene_{i+1}.mp3")
                if os.path.exists(voice_path):
                    st.markdown("**Narration:**")
                    st.audio(voice_path)
                
            with col2:
                # Display generated image if available
                image_path = os.path.join("outputs", "images", f"scene_{i+1}.png")
                if os.path.exists(image_path):
                    st.image(image_path, use_container_width=True)
    
    # Display background music if available
    music_path = os.path.join("outputs", "music", "bg_music.mp3")
    if os.path.exists(music_path):
        st.markdown("**Background Music:**")
        st.audio(music_path)
    
    # Display final video if available
    video_path = st.session_state.output_paths.get("video", "")
    if os.path.exists(video_path):
        st.markdown("**Final Story Experience:**")
        st.video(video_path)
        
        # Download button for the video
        with open(video_path, "rb") as file:
            st.download_button(
                label="Download Video",
                data=file,
                file_name="ai_story_experience.mp4",
                mime="video/mp4"
            )
    else:
        st.error("Video generation failed. Please check the logs.")

    # Reset button
    if st.button("Create Another Story", use_container_width=True):
        # Reset session state
        st.session_state.story_submitted = False
        st.session_state.script_generated = False
        st.session_state.script_approved = False
        st.session_state.processing_complete = False
        st.session_state.progress = 0
        st.session_state.scenes = []
        st.session_state.current_step = None
        st.session_state.output_paths = {}
        st.rerun()

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center;'>AI ShortStory Studio - Created for Hackathon</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    # This will run the Streamlit app when executed directly
    pass 