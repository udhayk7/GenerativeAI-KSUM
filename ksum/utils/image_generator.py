import os
import requests
import time
import random
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
import numpy as np
from typing import Optional
import openai
import math
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_gradient_background(width, height, color1=None, color2=None, style="vertical"):
    """Generate a gradient background with various style options"""
    if color1 is None:
        color1 = (
            random.randint(0, 100), 
            random.randint(0, 100),
            random.randint(0, 150)
        )
    
    if color2 is None:
        color2 = (
            random.randint(100, 200),
            random.randint(100, 200),
            random.randint(150, 255)
        )
        
    # Create gradient array
    gradient = np.zeros((height, width, 3), dtype=np.uint8)
    
    if style == "vertical":
        # Standard vertical gradient
        for y in range(height):
            r = color1[0] + (color2[0] - color1[0]) * y / height
            g = color1[1] + (color2[1] - color1[1]) * y / height
            b = color1[2] + (color2[2] - color1[2]) * y / height
            gradient[y,:] = [r, g, b]
            
    elif style == "horizontal":
        # Horizontal gradient
        for x in range(width):
            r = color1[0] + (color2[0] - color1[0]) * x / width
            g = color1[1] + (color2[1] - color1[1]) * x / width
            b = color1[2] + (color2[2] - color1[2]) * x / width
            gradient[:,x] = [r, g, b]
            
    elif style == "radial":
        # Radial gradient
        center_x = width // 2
        center_y = height // 2
        max_dist = math.sqrt(center_x**2 + center_y**2)
        
        for y in range(height):
            for x in range(width):
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                ratio = min(dist / max_dist, 1.0)
                
                r = color1[0] + (color2[0] - color1[0]) * ratio
                g = color1[1] + (color2[1] - color1[1]) * ratio
                b = color1[2] + (color2[2] - color1[2]) * ratio
                gradient[y, x] = [r, g, b]
    
    # Convert to PIL Image
    return Image.fromarray(gradient)

def get_tone_colors(tone):
    """Get color palette based on scene tone"""
    tone_palettes = {
        "mysterious": {
            "bg": [(20, 0, 40), (60, 30, 110)],
            "fg": [(120, 0, 200), (200, 150, 255), (80, 30, 80)],
            "accent": [(0, 200, 255), (255, 50, 200)]
        },
        "joyful": {
            "bg": [(100, 200, 255), (200, 255, 220)],
            "fg": [(255, 200, 0), (255, 150, 0), (0, 180, 120)],
            "accent": [(255, 100, 100), (255, 50, 50)]
        },
        "somber": {
            "bg": [(50, 50, 70), (80, 80, 120)],
            "fg": [(130, 130, 180), (70, 70, 70), (120, 120, 170)],
            "accent": [(200, 200, 255), (150, 120, 200)]
        },
        "tense": {
            "bg": [(70, 10, 10), (150, 30, 30)],
            "fg": [(200, 50, 30), (100, 0, 0), (150, 50, 50)],
            "accent": [(255, 200, 50), (255, 150, 0)]
        },
        "romantic": {
            "bg": [(150, 50, 100), (255, 200, 220)],
            "fg": [(255, 150, 150), (200, 100, 150), (255, 200, 180)],
            "accent": [(255, 220, 200), (255, 150, 200)]
        },
        "adventurous": {
            "bg": [(0, 50, 0), (100, 150, 100)],
            "fg": [(150, 200, 50), (200, 180, 0), (120, 100, 0)],
            "accent": [(255, 200, 0), (200, 255, 100)]
        },
        "dramatic": {
            "bg": [(20, 0, 40), (80, 10, 30)],
            "fg": [(150, 0, 0), (50, 0, 100), (100, 50, 50)],
            "accent": [(255, 200, 0), (200, 0, 0)]
        },
        "peaceful": {
            "bg": [(50, 100, 200), (200, 240, 255)],
            "fg": [(100, 200, 255), (150, 200, 200), (100, 180, 200)],
            "accent": [(255, 255, 200), (200, 255, 255)]
        }
    }
    
    # Default to mysterious if tone not found
    return tone_palettes.get(tone.lower(), tone_palettes["mysterious"])

def draw_character_silhouette(draw, x, y, width, height, posture="standing"):
    """Draw a character silhouette with various poses"""
    if posture == "standing":
        # Head
        head_radius = int(width * 0.1)
        head_y = y - height + int(height * 0.15)
        draw.ellipse((x - head_radius, head_y - head_radius, 
                     x + head_radius, head_y + head_radius), fill=(0, 0, 0))
        
        # Body
        body_width = int(width * 0.2)
        body_height = int(height * 0.45)
        body_y = head_y + head_radius
        draw.rectangle((x - body_width//2, body_y, 
                       x + body_width//2, body_y + body_height), fill=(0, 0, 0))
        
        # Legs
        leg_width = int(width * 0.08)
        leg_height = int(height * 0.4)
        leg_y = body_y + body_height
        draw.rectangle((x - body_width//2, leg_y, 
                       x - body_width//2 + leg_width, leg_y + leg_height), fill=(0, 0, 0))
        draw.rectangle((x + body_width//2 - leg_width, leg_y, 
                       x + body_width//2, leg_y + leg_height), fill=(0, 0, 0))
        
        # Arms
        arm_width = int(width * 0.08)
        arm_height = int(height * 0.3)
        arm_y = body_y + int(body_height * 0.1)
        draw.rectangle((x - body_width//2 - arm_width, arm_y, 
                       x - body_width//2, arm_y + arm_height), fill=(0, 0, 0))
        draw.rectangle((x + body_width//2, arm_y, 
                       x + body_width//2 + arm_width, arm_y + arm_height), fill=(0, 0, 0))
    
    elif posture == "sitting":
        # Head
        head_radius = int(width * 0.1)
        head_y = y - int(height * 0.6)
        draw.ellipse((x - head_radius, head_y - head_radius, 
                     x + head_radius, head_y + head_radius), fill=(0, 0, 0))
        
        # Body
        body_width = int(width * 0.2)
        body_height = int(height * 0.3)
        body_y = head_y + head_radius
        draw.rectangle((x - body_width//2, body_y, 
                       x + body_width//2, body_y + body_height), fill=(0, 0, 0))
        
        # Legs
        leg_width = int(width * 0.08)
        leg_height = int(height * 0.2)
        leg_y = body_y + body_height
        draw.rectangle((x - body_width//2, leg_y, 
                       x - body_width//2 + leg_width, leg_y + leg_height/2), fill=(0, 0, 0))
        draw.rectangle((x + body_width//2 - leg_width, leg_y, 
                       x + body_width//2, leg_y + leg_height/2), fill=(0, 0, 0))
        
        # Extended legs
        draw.rectangle((x - body_width//2 + leg_width//2, leg_y + leg_height/2, 
                        x + body_width//2 - leg_width//2, leg_y + leg_height), fill=(0, 0, 0))
    
    elif posture == "action":
        # Head
        head_radius = int(width * 0.1)
        head_y = y - height + int(height * 0.15)
        draw.ellipse((x - head_radius, head_y - head_radius, 
                     x + head_radius, head_y + head_radius), fill=(0, 0, 0))
        
        # Body (tilted)
        body_width = int(width * 0.2)
        body_height = int(height * 0.4)
        body_y = head_y + head_radius
        # Draw a polygon for tilted body
        draw.polygon([(x - body_width//2, body_y), 
                      (x + body_width//2, body_y - body_height//4),
                      (x + body_width//2, body_y + body_height - body_height//4),
                      (x - body_width//2, body_y + body_height)], fill=(0, 0, 0))
        
        # Legs in action pose
        leg_width = int(width * 0.08)
        leg_height = int(height * 0.35)
        leg_y = body_y + body_height
        draw.polygon([(x - body_width//2, leg_y), 
                      (x - body_width//2 - leg_width, leg_y + leg_height),
                      (x - body_width//2 + leg_width, leg_y + leg_height)], fill=(0, 0, 0))
        draw.polygon([(x + body_width//2, leg_y - body_height//4), 
                      (x + body_width//2 + leg_width, leg_y + leg_height//2),
                      (x + body_width//2 - leg_width, leg_y + leg_height//2)], fill=(0, 0, 0))
        
        # Arms in action
        arm_width = int(width * 0.08)
        arm_height = int(height * 0.25)
        arm_y = body_y + int(body_height * 0.1)
        draw.polygon([(x - body_width//2, arm_y), 
                      (x - body_width//2 - arm_width, arm_y - arm_height//2),
                      (x - body_width//2 - arm_width//2, arm_y + arm_height//2)], fill=(0, 0, 0))
        draw.polygon([(x + body_width//2, arm_y - body_height//4), 
                      (x + body_width//2 + arm_width, arm_y + arm_height),
                      (x + body_width//2 + arm_width//2, arm_y - arm_height//3)], fill=(0, 0, 0))

def draw_scene_element(draw, x, y, size, type_name, color):
    """Draw various scene elements based on type"""
    if type_name == "tree":
        # Tree trunk
        trunk_width = int(size * 0.2)
        trunk_height = int(size * 0.6)
        draw.rectangle((x - trunk_width//2, y - trunk_height, 
                        x + trunk_width//2, y), fill=(80, 50, 20))
        
        # Tree foliage
        foliage_radius = int(size * 0.4)
        draw.ellipse((x - foliage_radius, y - trunk_height - foliage_radius, 
                     x + foliage_radius, y - trunk_height + foliage_radius), fill=color)
    
    elif type_name == "building":
        # Simple building
        building_width = size
        building_height = int(size * 1.5)
        draw.rectangle((x - building_width//2, y - building_height, 
                        x + building_width//2, y), fill=color)
        
        # Windows
        window_size = int(size * 0.15)
        window_spacing = int(size * 0.25)
        window_color = (200, 200, 255)
        
        for floor in range(3):
            for window in range(3):
                window_x = x - building_width//2 + window_spacing//2 + window * window_spacing
                window_y = y - building_height + window_spacing//2 + floor * window_spacing
                if window_x + window_size <= x + building_width//2 and window_y + window_size <= y:
                    draw.rectangle((window_x, window_y, 
                                   window_x + window_size, window_y + window_size), fill=window_color)
    
    elif type_name == "mountain":
        # Mountain shape
        mountain_height = size
        mountain_base = int(size * 1.2)
        draw.polygon([(x - mountain_base//2, y), 
                      (x, y - mountain_height),
                      (x + mountain_base//2, y)], fill=color)
        
        # Snow cap
        snow_height = int(mountain_height * 0.3)
        draw.polygon([(x - int(mountain_base * 0.2), y - mountain_height + snow_height), 
                     (x, y - mountain_height),
                     (x + int(mountain_base * 0.2), y - mountain_height + snow_height)], 
                     fill=(240, 240, 255))
    
    elif type_name == "clouds":
        # Cloud puffs
        cloud_parts = random.randint(3, 5)
        for i in range(cloud_parts):
            puff_x = x + (i - cloud_parts//2) * (size//3)
            puff_y = y - random.randint(0, size//4)
            puff_size = random.randint(int(size * 0.3), int(size * 0.5))
            draw.ellipse((puff_x - puff_size//2, puff_y - puff_size//2,
                          puff_x + puff_size//2, puff_y + puff_size//2), fill=color)
    
    elif type_name == "water":
        # Water surface
        water_width = size * 2
        water_height = int(size * 0.8)
        draw.rectangle((x - water_width//2, y - water_height, 
                        x + water_width//2, y), fill=color)
        
        # Waves
        wave_color = (color[0] + 30 if color[0] + 30 < 256 else 255,
                      color[1] + 30 if color[1] + 30 < 256 else 255,
                      color[2] + 30 if color[2] + 30 < 256 else 255)
        
        for i in range(3):
            wave_y = y - water_height + i * (water_height // 3)
            draw.line((x - water_width//2, wave_y, x + water_width//2, wave_y), 
                      fill=wave_color, width=2)
    
    elif type_name == "light_ray":
        # Light rays
        num_rays = random.randint(5, 8)
        ray_length = size
        
        for i in range(num_rays):
            angle = 2 * math.pi * i / num_rays
            end_x = x + int(ray_length * math.cos(angle))
            end_y = y + int(ray_length * math.sin(angle))
            draw.line((x, y, end_x, end_y), fill=color, width=3)
    
    elif type_name == "portal":
        # Portal ring
        outer_radius = size // 2
        inner_radius = int(size * 0.35)
        draw.ellipse((x - outer_radius, y - outer_radius, 
                     x + outer_radius, y + outer_radius), fill=color)
        
        # Inner portal (transparent in real images, here just darker)
        inner_color = (color[0] // 2, color[1] // 2, color[2] // 2)
        draw.ellipse((x - inner_radius, y - inner_radius, 
                     x + inner_radius, y + inner_radius), fill=inner_color)
    
    else:  # Default to a geometric shape
        shape_type = random.choice(["circle", "rectangle", "triangle"])
        
        if shape_type == "circle":
            draw.ellipse((x - size//2, y - size//2, x + size//2, y + size//2), fill=color)
        elif shape_type == "rectangle":
            draw.rectangle((x - size//2, y - size//2, x + size//2, y + size//2), fill=color)
        else:  # triangle
            draw.polygon([(x, y - size//2), (x - size//2, y + size//2), (x + size//2, y + size//2)], fill=color)

def draw_setting(draw, img_width, img_height, setting_type, colors):
    """Draw scene setting elements based on type"""
    if "exterior" in setting_type.lower():
        # Sky
        bg_style = random.choice(["vertical", "horizontal", "radial"])
        # Draw sky/background elements
        
        # Ground/horizon
        horizon_y = int(img_height * random.uniform(0.5, 0.7))
        draw.rectangle((0, horizon_y, img_width, img_height), fill=colors["fg"][0])
        
        # Sun/Moon
        if random.random() > 0.5:
            # Sun
            sun_x = random.randint(img_width//4, 3*img_width//4)
            sun_y = random.randint(img_height//5, horizon_y - img_height//5)
            sun_size = random.randint(img_width//10, img_width//6)
            draw.ellipse((sun_x - sun_size//2, sun_y - sun_size//2,
                         sun_x + sun_size//2, sun_y + sun_size//2), fill=colors["accent"][0])
            
            # Light rays
            draw_scene_element(draw, sun_x, sun_y, sun_size*2, "light_ray", colors["accent"][0])
        else:
            # Moon
            moon_x = random.randint(img_width//4, 3*img_width//4)
            moon_y = random.randint(img_height//5, horizon_y - img_height//5)
            moon_size = random.randint(img_width//12, img_width//8)
            draw.ellipse((moon_x - moon_size//2, moon_y - moon_size//2,
                         moon_x + moon_size//2, moon_y + moon_size//2), fill=colors["accent"][1])
        
        # Background mountains or buildings
        for i in range(3):
            element_x = random.randint(img_width//6, 5*img_width//6)
            element_size = random.randint(img_width//5, img_width//3)
            if "mountain" in setting_type.lower() or "forest" in setting_type.lower() or "nature" in setting_type.lower():
                draw_scene_element(draw, element_x, horizon_y, element_size, "mountain", colors["fg"][i % len(colors["fg"])])
            else:
                draw_scene_element(draw, element_x, horizon_y, element_size, "building", colors["fg"][i % len(colors["fg"])])
        
        # Trees or other foreground elements
        for i in range(5):
            element_x = random.randint(img_width//8, 7*img_width//8)
            element_y = random.randint(horizon_y, img_height)
            element_size = random.randint(img_height//6, img_height//4)
            if "forest" in setting_type.lower() or "nature" in setting_type.lower():
                draw_scene_element(draw, element_x, element_y, element_size, "tree", colors["fg"][i % len(colors["fg"])])
            
        # Clouds
        for i in range(3):
            cloud_x = random.randint(img_width//8, 7*img_width//8)
            cloud_y = random.randint(img_height//8, horizon_y//2)
            cloud_size = random.randint(img_width//10, img_width//6)
            draw_scene_element(draw, cloud_x, cloud_y, cloud_size, "clouds", (240, 240, 255))
            
    elif "interior" in setting_type.lower():
        # Floor
        floor_y = int(img_height * 0.7)
        draw.rectangle((0, floor_y, img_width, img_height), fill=colors["fg"][0])
        
        # Wall
        draw.rectangle((0, 0, img_width, floor_y), fill=colors["bg"][1])
        
        # Window or picture
        element_x = random.randint(img_width//4, 3*img_width//4)
        element_y = int(floor_y * 0.5)
        element_size = min(img_width//4, floor_y//2)
        
        if "window" in setting_type.lower() or random.random() > 0.5:
            # Window
            window_width = element_size
            window_height = int(element_size * 1.5)
            draw.rectangle((element_x - window_width//2, element_y - window_height//2,
                           element_x + window_width//2, element_y + window_height//2), 
                           fill=colors["accent"][0])
            
            # Window frame
            frame_width = int(window_width * 0.1)
            draw.line((element_x, element_y - window_height//2, element_x, element_y + window_height//2), 
                      fill=colors["fg"][1], width=frame_width)
            draw.line((element_x - window_width//2, element_y, element_x + window_width//2, element_y), 
                      fill=colors["fg"][1], width=frame_width)
        else:
            # Picture or decoration
            draw.rectangle((element_x - element_size//2, element_y - element_size//2,
                           element_x + element_size//2, element_y + element_size//2), 
                           fill=colors["accent"][1])
            
            # Frame
            frame_width = int(element_size * 0.1)
            draw.rectangle((element_x - element_size//2 - frame_width, element_y - element_size//2 - frame_width,
                           element_x + element_size//2 + frame_width, element_y + element_size//2 + frame_width),
                           outline=colors["fg"][1], width=frame_width)
        
        # Furniture
        furniture_y = floor_y - img_height//10
        furniture_width = img_width//3
        furniture_height = img_height//6
        draw.rectangle((img_width//2 - furniture_width//2, furniture_y - furniture_height,
                       img_width//2 + furniture_width//2, furniture_y), fill=colors["fg"][1])
            
    elif "magical" in setting_type.lower() or "fantasy" in setting_type.lower():
        # Magical background with portal/energy elements
        
        # Background glow
        draw_scene_element(draw, img_width//2, img_height//2, max(img_width, img_height), 
                          "light_ray", colors["accent"][0])
        
        # Portal
        portal_size = min(img_width, img_height) // 2
        draw_scene_element(draw, img_width//2, img_height//2, portal_size, "portal", colors["accent"][1])
        
        # Energy particles/stars
        for i in range(20):
            particle_x = random.randint(0, img_width)
            particle_y = random.randint(0, img_height)
            particle_size = random.randint(5, 15)
            draw.ellipse((particle_x - particle_size//2, particle_y - particle_size//2,
                         particle_x + particle_size//2, particle_y + particle_size//2), 
                         fill=random.choice(colors["fg"]))
    
    else:  # Generic abstract setting
        # Abstract background with geometric shapes
        for i in range(15):
            shape_x = random.randint(0, img_width)
            shape_y = random.randint(0, img_height)
            shape_size = random.randint(img_width//20, img_width//8)
            draw_scene_element(draw, shape_x, shape_y, shape_size, "circle", random.choice(colors["fg"]))

def analyze_scene_type(description):
    """Analyze scene description to extract setting and character info"""
    description_lower = description.lower()
    
    # Default values
    setting_type = "interior"
    character_pose = "standing"
    has_character = True
    
    # Determine setting
    if any(term in description_lower for term in ["exterior", "outside", "outdoor", "nature", "forest", "mountain", "field", "landscape"]):
        setting_type = "exterior"
    elif any(term in description_lower for term in ["magical", "fantasy", "mystical", "ethereal", "otherworldly"]):
        setting_type = "magical"
    
    # Determine character pose
    if any(term in description_lower for term in ["action", "running", "fight", "battle", "moving"]):
        character_pose = "action"
    elif any(term in description_lower for term in ["sitting", "seated", "resting"]):
        character_pose = "sitting"
        
    # Check if scene likely has a character
    if any(term in description_lower for term in ["landscape", "empty", "deserted", "abandoned", "still life"]):
        has_character = False
        
    return setting_type, character_pose, has_character

def generate_visual_element(draw, img_width, img_height, x, y, size, color):
    """Generate a random visual element (circle, square, star, etc.)"""
    shape_type = random.choice(["circle", "rectangle", "polygon"])
    
    if shape_type == "circle":
        radius = random.randint(size // 4, size // 2)
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    elif shape_type == "rectangle":
        width = random.randint(size // 3, size // 2)
        height = random.randint(size // 3, size // 2)
        draw.rectangle((x - width, y - height, x + width, y + height), fill=color)
    elif shape_type == "polygon":
        points = []
        sides = random.randint(3, 6)  # Triangle to hexagon
        for i in range(sides):
            angle = 2 * 3.14159 * i / sides
            px = x + int(size/2 * np.cos(angle))
            py = y + int(size/2 * np.sin(angle))
            points.append((px, py))
        draw.polygon(points, fill=color)

def create_scene_elements(draw, img_width, img_height, scene_type, tone):
    """Create visual elements based on scene type and tone"""
    
    # Get colors for this tone
    colors = get_tone_colors(tone)
    
    # Analyze scene type for setting and character info
    setting_type, character_pose, has_character = analyze_scene_type(scene_type)
    
    # Draw appropriate setting
    draw_setting(draw, img_width, img_height, setting_type, colors)
    
    # Add character if appropriate
    if has_character:
        if "close-up" in scene_type.lower():
            # For close-ups, character is larger and more central
            character_x = img_width // 2
            character_y = img_height - img_height // 4
            character_size = img_width // 2
        else:
            # For wider shots, character is smaller
            character_x = img_width // 3
            character_y = img_height - img_height // 6
            character_size = img_width // 3
        
        # Draw character
        draw_character_silhouette(draw, character_x, character_y, character_size, character_pose)
        
        # For multiple characters
        if "group" in scene_type.lower() or random.random() > 0.7:
            second_character_x = 2 * img_width // 3
            second_character_y = img_height - img_height // 6
            second_character_size = img_width // 3
            draw_character_silhouette(draw, second_character_x, second_character_y, second_character_size, 
                                     random.choice(["standing", "sitting"]))

def generate_placeholder_image(text, output_file, width=1024, height=1024, tone="mysterious"):
    """
    Create a visually interesting placeholder image based on the scene description
    
    Args:
        text: Text description of the scene
        output_file: Path to save the image
        width: Image width
        height: Image height
        tone: Emotional tone of the scene
    """
    # Extract scene type from text
    scene_type = text[:100]
    
    # Get color palette for this tone
    colors = get_tone_colors(tone)
    
    # Create gradient background based on tone
    gradient_style = random.choice(["vertical", "horizontal", "radial"])
    img = generate_gradient_background(width, height, colors["bg"][0], colors["bg"][1], gradient_style)
    draw = ImageDraw.Draw(img)
    
    # Add visual elements based on scene type and tone
    create_scene_elements(draw, width, height, scene_type, tone)
    
    # Apply some filters for effect
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.2)
    
    # Try to load a font, use default if not available
    try:
        font_size = 36
        title_font_size = 48
        font = ImageFont.truetype("Arial", font_size)
        title_font = ImageFont.truetype("Arial", title_font_size)
    except IOError:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Add the AI ShortStory Studio title at the top center
    title = "AI ShortStory Studio"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, 50), title, fill=(255, 255, 255), font=title_font)
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Save the image
    img.save(output_file)
    print(f"Visual placeholder image saved to {output_file}")
    return output_file

def generate_image(
    prompt: str, 
    output_file: str,
    size: str = "1024x1024",
    quality: str = "standard",
    style: str = "vivid"
) -> Optional[str]:
    """
    Generate an image using OpenAI's DALL-E 3 model
    
    Args:
        prompt: The text prompt for image generation
        output_file: Path to save the generated image
        size: Image size (1024x1024, 1024x1792, or 1792x1024)
        quality: Image quality (standard or hd)
        style: Image style (vivid or natural)
        
    Returns:
        Path to the generated image file, or None if generation failed
    """
    try:
        # Print status
        print(f"Generating image for prompt: {prompt[:50]}...")
        
        # Extract tone from prompt
        tone = "mysterious"  # default
        tone_keywords = ["mysterious", "joyful", "somber", "tense", "romantic", "adventurous", "dramatic", "peaceful"]
        for keyword in tone_keywords:
            if keyword in prompt.lower():
                tone = keyword
                break
        
        # Enhance the prompt if needed
        enhanced_prompt = f"{prompt} High quality, detailed, cinematic lighting."
        
        # Create folders if they don't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Try to call the OpenAI API
        try:
            # Call the OpenAI API
            response = openai.images.generate(
                model="dall-e-3",
                prompt=enhanced_prompt,
                size=size,
                quality=quality,
                style=style,
                n=1
            )
            
            # Get image URL
            image_url = response.data[0].url
            
            # Download image
            response = requests.get(image_url)
            if response.status_code == 200:
                # Save the image
                img = Image.open(BytesIO(response.content))
                img.save(output_file)
                print(f"Image saved to {output_file}")
                return output_file
            else:
                print(f"Failed to download image: Status code {response.status_code}")
                # Fall back to placeholder
                return generate_placeholder_image(prompt, output_file, tone=tone)
        
        except Exception as api_error:
            print(f"Error with API call: {api_error}")
            # Fall back to placeholder
            return generate_placeholder_image(prompt, output_file, tone=tone)
            
    except Exception as e:
        print(f"Error generating image: {e}")
        # Try to generate a placeholder as last resort
        try:
            return generate_placeholder_image(prompt, output_file, tone="mysterious")
        except:
            return None
        
def generate_images_for_scenes(scenes, output_dir="outputs/images"):
    """
    Generate images for all scenes in a story
    
    Args:
        scenes: List of scene dictionaries
        output_dir: Directory to save the generated images
        
    Returns:
        List of paths to the generated image files
    """
    os.makedirs(output_dir, exist_ok=True)
    image_paths = []
    
    for i, scene in enumerate(scenes):
        # Get the image prompt and tone from the scene
        prompt = scene.get("image_prompt", scene.get("description", ""))
        tone = scene.get("tone", "mysterious")
        
        # Generate the image
        output_file = os.path.join(output_dir, f"scene_{i+1}.png")
        image_path = generate_image(prompt, output_file)
        
        if image_path:
            image_paths.append(image_path)
        
        # Add a small delay between API calls
        if i < len(scenes) - 1:
            time.sleep(1)
            
    return image_paths

if __name__ == "__main__":
    # For testing
    test_prompt = "A close-up of a detective examining clues in a dimly lit room"
    output_path = "outputs/images/test_image.png"
    generate_placeholder_image(test_prompt, output_path, tone="mysterious") 