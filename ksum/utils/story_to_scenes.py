import os
import json
import re
import nltk
import random
from typing import List, Dict, Any
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Try to download nltk resources (for fallback mechanism)
try:
    nltk.download('punkt', quiet=True)
except:
    pass

# Movie scene types for fallback generation
SCENE_TYPES = [
    "establishing shot", "character introduction", "dialogue scene", "action sequence", 
    "emotional moment", "revelation", "montage", "flashback", "conflict", "resolution"
]

# Cinematic styles for variety
CINEMATIC_STYLES = [
    "golden hour lighting with warm tones", "dramatic chiaroscuro with high contrast", 
    "soft ethereal lighting with dreamy atmosphere", "vibrant color palette with rich saturation",
    "moody low-key lighting with deep shadows", "bright high-key lighting with minimal shadows",
    "noir-inspired with stark contrast", "vintage film look with muted colors",
    "neon-lit cyberpunk aesthetic", "earthy natural lighting"
]

# Camera shots for variety
CAMERA_SHOTS = [
    "close-up", "extreme close-up", "medium shot", "wide shot", "overhead shot",
    "low angle", "high angle", "tracking shot", "dolly zoom", "long shot"
]

def extract_characters(story_text: str) -> List[str]:
    """Extract potential character names from the story"""
    # Simple extraction based on capitalized words not at the beginning of sentences
    words = story_text.split()
    
    # Find potential character names (capitalized words not following periods)
    potential_characters = []
    for i, word in enumerate(words):
        if i > 0 and word[0].isupper() and words[i-1][-1] not in ['.', '!', '?']:
            # Clean up punctuation
            clean_word = re.sub(r'[^\w\s]', '', word)
            if clean_word and len(clean_word) > 1:
                potential_characters.append(clean_word)
    
    # Count occurrences to find most likely character names
    char_count = {}
    for char in potential_characters:
        char_count[char] = char_count.get(char, 0) + 1
    
    # Filter to characters mentioned at least twice
    characters = [char for char, count in char_count.items() if count >= 1]
    
    # Add some generic characters if none found
    if not characters:
        characters = ["Protagonist", "Character"]
    
    return characters[:5]  # Limit to 5 characters max

def extract_settings(story_text: str) -> List[str]:
    """Extract potential settings from the story"""
    # Look for location keywords
    location_keywords = ["room", "house", "city", "forest", "mountain", "sea", "ocean", 
                        "building", "castle", "village", "town", "office", "school",
                        "garden", "park", "street", "road", "path", "kitchen", "bedroom"]
    
    settings = []
    for keyword in location_keywords:
        pattern = r'(?i)((?:\w+\s){0,3}' + keyword + r'(?:\s\w+){0,3})'
        matches = re.findall(pattern, story_text)
        settings.extend(matches)
    
    # If no settings found, use generic ones
    if not settings:
        settings = ["interior location", "exterior location"]
    
    return settings[:3]  # Limit to 3 settings

def extract_key_objects(story_text: str) -> List[str]:
    """Extract potential key objects from the story"""
    # Common objects that might be important in stories
    object_keywords = ["book", "letter", "key", "door", "window", "phone", "sword", 
                      "ring", "necklace", "clock", "watch", "gun", "knife", "car",
                      "photograph", "picture", "painting", "box", "chair", "table",
                      "bed", "lamp", "light", "fire", "water", "food", "drink"]
    
    objects = []
    for keyword in object_keywords:
        if keyword in story_text.lower():
            # Get some context around the object
            pattern = r'(?i)((?:\w+\s){0,2}' + keyword + r'(?:\s\w+){0,2})'
            matches = re.findall(pattern, story_text)
            objects.extend(matches)
    
    return objects[:5]  # Limit to 5 objects

def extract_themes(story_text: str) -> List[str]:
    """Extract potential themes from the story"""
    theme_keywords = {
        "love": ["love", "heart", "romance", "affection", "passion"],
        "friendship": ["friend", "friendship", "companion", "ally", "comrade"],
        "betrayal": ["betray", "deception", "dishonesty", "treachery"],
        "revenge": ["revenge", "vengeance", "retribution", "payback"],
        "mystery": ["mystery", "enigma", "puzzle", "secret", "clue"],
        "adventure": ["adventure", "journey", "quest", "expedition"],
        "conflict": ["conflict", "struggle", "battle", "fight", "war"],
        "transformation": ["change", "transform", "evolve", "metamorphosis"],
        "redemption": ["redemption", "forgiveness", "atonement"],
        "loss": ["loss", "grief", "mourning", "sorrow", "death"]
    }
    
    found_themes = []
    story_lower = story_text.lower()
    
    for theme, keywords in theme_keywords.items():
        for keyword in keywords:
            if keyword in story_lower:
                found_themes.append(theme)
                break
    
    # If no themes found, add some generic ones
    if not found_themes:
        found_themes = ["discovery", "challenge"]
    
    return found_themes[:3]  # Limit to 3 themes

def extract_emotions(story_text: str) -> List[str]:
    """Extract potential emotions from the story"""
    emotion_keywords = {
        "happy": ["happy", "joy", "delight", "pleased", "smile", "laugh"],
        "sad": ["sad", "sorrow", "unhappy", "miserable", "cry", "tear"],
        "angry": ["angry", "fury", "rage", "mad", "irritated", "annoyed"],
        "afraid": ["fear", "afraid", "scared", "terrified", "dread"],
        "surprised": ["surprise", "astonished", "amazed", "shocked"],
        "disgust": ["disgust", "repulsed", "revolted"],
        "anticipation": ["anticipation", "expectation", "excitement"],
        "trust": ["trust", "belief", "faith", "confidence"],
        "curious": ["curious", "intrigued", "interested"],
        "confused": ["confused", "perplexed", "puzzled", "bewildered"]
    }
    
    found_emotions = []
    story_lower = story_text.lower()
    
    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            if keyword in story_lower:
                found_emotions.append(emotion)
                break
    
    # If no emotions found, add some generic ones
    if not found_emotions:
        found_emotions = ["curious", "determined"]
    
    return found_emotions

def create_advanced_fallback_scenes(story_text: str, num_scenes: int = 3) -> List[Dict[str, Any]]:
    """
    Create highly detailed fallback scenes by analyzing the story text
    
    Args:
        story_text: The input story text
        num_scenes: Target number of scenes
        
    Returns:
        List of scene dictionaries with rich details
    """
    # Clean up and normalize the text
    text = story_text.strip()
    
    # Get story elements through text analysis
    characters = extract_characters(text)
    settings = extract_settings(text)
    objects = extract_key_objects(text)
    themes = extract_themes(text)
    emotions = extract_emotions(text)
    
    # Try to split by paragraphs first
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    # If not enough paragraphs, try to use sentence splitting
    if len(paragraphs) < num_scenes:
        try:
            # Use NLTK if available
            sentences = nltk.sent_tokenize(text)
        except:
            # Manual sentence splitting as fallback
            sentences = re.split(r'[.!?]+', text)
        
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Distribute sentences among scenes
        if len(sentences) >= num_scenes:
            sentences_per_scene = max(1, len(sentences) // num_scenes)
            scene_texts = []
            
            for i in range(num_scenes):
                start_idx = i * sentences_per_scene
                end_idx = start_idx + sentences_per_scene if i < num_scenes-1 else len(sentences)
                scene_text = ' '.join(sentences[start_idx:end_idx])
                scene_texts.append(scene_text)
        else:
            # Not enough sentences, just use what we have
            scene_texts = sentences[:num_scenes]
            # Pad with empty strings if needed
            scene_texts.extend([''] * (num_scenes - len(scene_texts)))
    else:
        # Use paragraphs
        scene_texts = paragraphs[:num_scenes]
        # Pad with empty strings if needed
        scene_texts.extend([''] * (num_scenes - len(scene_texts)))
    
    # Generate scenes with rich details
    scenes = []
    scene_types = random.sample(SCENE_TYPES, min(num_scenes, len(SCENE_TYPES)))
    cinematic_styles = random.sample(CINEMATIC_STYLES, min(num_scenes, len(CINEMATIC_STYLES)))
    camera_shots = random.sample(CAMERA_SHOTS, min(num_scenes, len(CAMERA_SHOTS)))
    
    for i, (scene_text, scene_type, style, shot) in enumerate(zip(scene_texts, scene_types, cinematic_styles, camera_shots)):
        # Get details for this scene
        character = characters[i % len(characters)] if characters else "Protagonist"
        setting = settings[i % len(settings)] if settings else "setting"
        emotion = emotions[i % len(emotions)] if emotions else "emotional"
        theme = themes[i % len(themes)] if themes else "thematic"
        
        # Get objects for this scene
        scene_objects = [obj for j, obj in enumerate(objects) if j % num_scenes == i] if objects else []
        object_text = ", featuring " + " and ".join(scene_objects) if scene_objects else ""
        
        # Determine scene tone
        tones = ["mysterious", "joyful", "somber", "tense", "romantic", "adventurous", "dramatic", "peaceful"]
        tone = tones[i % len(tones)]
        
        # Create description with rich details
        description = f"Scene {i+1}: A {shot} of {character} in the {setting}, during a {scene_type} moment. {style}{object_text}. The atmosphere conveys a {tone} and {emotion} feeling, emphasizing the theme of {theme}."
        
        # Clean up narration text - ALWAYS use actual story text, not placeholders
        narration = scene_text if scene_text else text[:100] + "..."
        
        # Create a detailed image prompt
        image_prompt = f"A {tone} scene showing {character} in {setting} with {style}. {shot} perspective{object_text}. Cinematic lighting, detailed, artistic composition with professional film quality."
        
        scenes.append({
            "description": description,
            "narration": narration,
            "tone": tone,
            "image_prompt": image_prompt
        })
    
    return scenes

def create_smart_fallback_scenes(story_text: str, num_scenes: int = 3) -> List[Dict[str, Any]]:
    """
    Create intelligent fallback scenes when API fails by analyzing the story text
    
    Args:
        story_text: The input story text
        num_scenes: Number of scenes to create
        
    Returns:
        List of scene dictionaries
    """
    # Clean up and normalize the text
    text = story_text.strip()
    
    # If very short text, just use as one scene
    if len(text) < 100:
        return [{
            "description": f"A visualization of the story: {text[:50]}...",
            "narration": text,
            "tone": "neutral",
            "image_prompt": f"A cinematic scene depicting: {text[:50]}... with artistic lighting and detailed visuals."
        }]
    
    # Try to split by paragraphs first
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    
    # If not enough paragraphs, split by sentences
    if len(paragraphs) < num_scenes:
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Calculate how many sentences per scene
        if len(sentences) >= num_scenes:
            sentences_per_scene = len(sentences) // num_scenes
            scene_texts = []
            
            for i in range(num_scenes):
                start_idx = i * sentences_per_scene
                end_idx = start_idx + sentences_per_scene if i < num_scenes-1 else len(sentences)
                scene_text = '. '.join(sentences[start_idx:end_idx]) + '.'
                scene_texts.append(scene_text)
        else:
            # If not enough sentences, just use paragraphs or whole text
            scene_texts = paragraphs if paragraphs else [text]
    else:
        # Use paragraphs if there are enough
        scene_texts = paragraphs[:num_scenes]
    
    # Generate scenes from the text segments
    scenes = []
    tones = ["mysterious", "adventurous", "emotional", "dramatic", "peaceful"]
    
    for i, scene_text in enumerate(scene_texts):
        if i >= num_scenes:
            break
            
        # Extract key terms for better image prompts
        words = scene_text.lower().split()
        keywords = [w for w in words if len(w) > 4 and w not in {"there", "their", "which", "would", "could", "about", "through"}]
        keywords = keywords[:5]  # Take top 5 keywords
        
        tone = tones[i % len(tones)]
        
        scenes.append({
            "description": f"Scene {i+1}: {scene_text[:100]}...",
            "narration": scene_text,
            "tone": tone,
            "image_prompt": f"A {tone} scene showing {' '.join(keywords)}. Cinematic lighting, detailed, artistic composition."
        })
    
    return scenes

def story_to_scenes(story_text: str, output_file: str = "outputs/scenes.json") -> List[Dict[str, Any]]:
    """
    Break down a short story into visual scenes using GPT-4
    
    Args:
        story_text: The input short story text
        output_file: Path to save the JSON output
        
    Returns:
        List of scene dictionaries containing descriptions and narration text
    """
    try:
        # Create the prompt for GPT-4
        prompt = f"""
        Break down the following short story into 2-4 distinct visual scenes for a narrated slideshow:

        STORY:
        {story_text}

        For each scene:
        1. Create a detailed visual description for image generation
        2. Extract the narration text that should accompany this visual
        3. Suggest a brief emotional tone for this scene (e.g., "mysterious", "joyful", "tense")
        
        Format your response as a JSON array with this structure:
        [
            {{
                "description": "Detailed visual description for image generation (no text in image)",
                "narration": "Text that should be read during this scene",
                "tone": "emotional tone of the scene",
                "image_prompt": "Optimized prompt for DALL-E image generation with style guidance"
            }},
            // additional scenes...
        ]
        
        IMPORTANT GUIDELINES:
        - Make each scene visually distinct
        - Description should focus on what should be SEEN in the image
        - Narration should be the exact text from the story that corresponds to this scene
        - The image_prompt should be detailed and include artistic style guidance
        - Don't include text overlay instructions in image descriptions
        - Keep the original story's emotional tone
        """
        
        try:
            # Call the OpenAI API
            response = openai.chat.completions.create(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert storyteller and visual designer breaking stories into compelling scenes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            # Extract and parse the JSON response
            json_response = response.choices[0].message.content
            
            # Find JSON content (in case there's surrounding text)
            import re
            json_match = re.search(r'\[.*\]', json_response, re.DOTALL)
            if json_match:
                json_content = json_match.group(0)
            else:
                json_content = json_response
                
            # Parse JSON
            scenes = json.loads(json_content)
        except Exception as api_error:
            print(f"API call failed: {api_error}")
            # Use advanced fallback if API call fails
            scenes = create_advanced_fallback_scenes(story_text)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save to file
        with open(output_file, 'w') as f:
            json.dump(scenes, f, indent=2)
            
        return scenes
        
    except Exception as e:
        print(f"Error breaking story into scenes: {e}")
        # Use intelligent fallback scenes
        fallback_scenes = create_advanced_fallback_scenes(story_text)
        
        # Try to save fallback scenes
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(fallback_scenes, f, indent=2)
        except Exception:
            pass
            
        return fallback_scenes

if __name__ == "__main__":
    # For testing
    test_story = """
    The explorer stood at the edge of the ancient ruins, heart pounding with anticipation. 
    After years of research, the lost city was finally before them. As they stepped inside 
    the grand entrance, torchlight revealed glittering treasures beyond imagination. 
    But a sudden rumble warned that disturbing this place had awakened something long forgotten, 
    something that had been waiting centuries for an intruder.
    """
    
    scenes = story_to_scenes(test_story)
    print(f"Generated {len(scenes)} scenes:") 