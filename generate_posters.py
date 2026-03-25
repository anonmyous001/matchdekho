import json
import os
from PIL import Image, ImageDraw, ImageFont

base_img_path = r"C:\Users\amrit\.gemini\antigravity\brain\2e5a85b8-7577-4395-8363-8a118458841f\ipl_base_poster_1774468277037.png"
json_path = "api/upcomingevnets.json"
output_dir = "image/upcoming"

os.makedirs(output_dir, exist_ok=True)

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Font loading setup
try:
    font_large = ImageFont.truetype("arialbd.ttf", 90)
    font_medium = ImageFont.truetype("arialbd.ttf", 45)
    font_small = ImageFont.truetype("arial.ttf", 30)
except IOError:
    print("Warning: arialbd.ttf not found, using default font. Text size might be bad.")
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

base_img = Image.open(base_img_path).convert("RGBA")
base_img = base_img.resize((1280, 720)) # Resize base once
W, H = base_img.size

for i, match in enumerate(data['upcomingMatches']):
    img = base_img.copy()
    
    # Add a slight dark overlay to make text pop more
    overlay = Image.new('RGBA', img.size, (0, 0, 0, 100))
    img = Image.alpha_composite(img, overlay)
    
    draw = ImageDraw.Draw(img)
    
    title = match['title']
    teams = f"{match['team1']} VS {match['team2']}"
    date_venue = f"{match['date']} | {match['time']} | {match['venue']}"
    
    def get_text_dimensions(text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Draw Teams (huge)
    tw, th = get_text_dimensions(teams, font_large)
    draw.text(((W-tw)/2, (H-th)/2), teams, fill="white", font=font_large, align="center")
    
    # Draw Match info (above teams)
    cw, ch = get_text_dimensions(title, font_medium)
    draw.text(((W-cw)/2, (H-th)/2 - ch - 40), title, fill="#FFD700", font=font_medium, align="center")
    
    # Draw Date/Venue (below teams)
    vw, vh = get_text_dimensions(date_venue, font_small)
    draw.text(((W-vw)/2, (H+th)/2 + 40), date_venue, fill="#CCCCCC", font=font_small, align="center")
    
    file_name = f"match_{i+1}.jpg"
    out_path = os.path.join(output_dir, file_name)
    
    img.convert("RGB").save(out_path, "JPEG", quality=85)
    match['poster'] = f"image/upcoming/{file_name}"

with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

print(f"Generated {len(data['upcomingMatches'])} posters successfully!")
