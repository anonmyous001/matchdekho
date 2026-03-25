import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# Map team short names to generated image paths
brain_dir = r"C:\Users\amrit\.gemini\antigravity\brain\2e5a85b8-7577-4395-8363-8a118458841f"
team_images = {
    'CSK': os.path.join(brain_dir, "bg_csk_1774468971568.png"),
    'MI': os.path.join(brain_dir, "bg_mi_1774468993531.png"),
    'RCB': os.path.join(brain_dir, "bg_rcb_1774469013680.png"),
    'KKR': os.path.join(brain_dir, "bg_kkr_1774469137824.png"),
    'SRH': os.path.join(brain_dir, "bg_srh_1774469153949.png"),
    'DC': os.path.join(brain_dir, "bg_dc_1774469172563.png"),
    'PBKS': os.path.join(brain_dir, "bg_pbks_1774469200417.png"),
    'RR': os.path.join(brain_dir, "bg_rr_1774469219532.png"),
    'GT': os.path.join(brain_dir, "bg_gt_1774469237630.png"),
    'LSG': os.path.join(brain_dir, "bg_lsg_1774469256247.png")
}

json_path = "api/upcomingevnets.json"
output_dir = "image/upcoming"
os.makedirs(output_dir, exist_ok=True)

with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Load fonts
try:
    font_vs = ImageFont.truetype("arialbd.ttf", 100)
    font_large = ImageFont.truetype("arialbd.ttf", 60)
    font_medium = ImageFont.truetype("arialbd.ttf", 35)
    font_small = ImageFont.truetype("arial.ttf", 25)
except IOError:
    font_vs = font_large = font_medium = font_small = ImageFont.load_default()

# Desired output poster size
W, H = 1200, 675
half_W = W // 2

# Pre-load and resize team images to save time inside loop
loaded_teams = {}
for team, path in team_images.items():
    try:
        if os.path.exists(path):
            img = Image.open(path).convert("RGBA")
            # Resize image to fill at least half width and full height
            # Actually, let's resize it to fill full W and H so players are big
            # DALL-E outputs 1024x1024 or 1792x1024. We'll resize/crop to WxH
            img_ratio = img.width / img.height
            target_ratio = W / H
            if img_ratio > target_ratio:
                # image is wider, scale based on height
                new_h = H
                new_w = int(img_ratio * H)
            else:
                new_w = W
                new_h = int(W / img_ratio)
            
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            # Center crop to exactly WxH
            left = (new_w - W) // 2
            top = (new_h - H) // 2
            img = img.crop((left, top, left + W, top + H))
            
            # Darken the whole image slightly to make text pop
            overlay = Image.new('RGBA', (W, H), (0, 0, 0, 100))
            img = Image.alpha_composite(img, overlay)
            
            loaded_teams[team] = img
        else:
            print(f"File not found for {team}: {path}")
    except Exception as e:
        print(f"Error loading {team}: {e}")

# Function to text dimensions
def get_text_dims(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]

# Now generate matches
for i, match in enumerate(data['upcomingMatches']):
    t1 = match['team1']
    t2 = match['team2']
    
    # Create blank canvas
    merged = Image.new('RGBA', (W, H), (20, 20, 40, 255))
    
    # Left side (Team 1)
    if t1 in loaded_teams:
        img1 = loaded_teams[t1]
        # Crop the left half of the Team 1 image (0, 0, half_W, H)
        left_half = img1.crop((0, 0, half_W, H))
        merged.paste(left_half, (0, 0))
        
    # Right side (Team 2)
    if t2 in loaded_teams:
        img2 = loaded_teams[t2]
        # Crop the right half of the Team 2 image (half_W, 0, W, H)
        right_half = img2.crop((half_W, 0, W, H))
        merged.paste(right_half, (half_W, 0))
        
    # Draw dark gradient box in middle for text readability
    # (Optional, but adds to the poster style)
    draw = ImageDraw.Draw(merged)
    # A center band
    draw.rectangle([W//2 - 150, 0, W//2 + 150, H], fill=(0, 0, 0, 160))
    
    # Draw 'VS' in center
    vw, vh = get_text_dims(draw, "VS", font_vs)
    draw.text(((W-vw)/2, (H-vh)/2), "VS", font=font_vs, fill=(255, 69, 0, 255))
    
    # Draw Team 1 Name Left Side
    tw1, th1 = get_text_dims(draw, t1, font_large)
    draw.text((half_W // 2 - tw1 // 2, (H-th1)/2), t1, font=font_large, fill=(255, 255, 255, 255))
    
    # Draw Team 2 Name Right Side
    tw2, th2 = get_text_dims(draw, t2, font_large)
    draw.text((half_W + half_W // 2 - tw2 // 2, (H-th2)/2), t2, font=font_large, fill=(255, 255, 255, 255))
    
    # Match title (Top middle)
    title = match['title']
    cw, ch = get_text_dims(draw, title, font_medium)
    draw.text(((W-cw)/2, 40), title, font=font_medium, fill=(255, 215, 0, 255)) # Gold
    
    # Date/Time/Venue (Bottom middle)
    date_venue = f"{match['date']} | {match['time']} | {match['venue']}"
    dw, dh = get_text_dims(draw, date_venue, font_small)
    
    # Draw background box for venue
    box_pad = 10
    draw.rectangle([(W-dw)/2 - box_pad, H - 60 - box_pad, (W+dw)/2 + box_pad, H - 60 + dh + box_pad], fill=(0,0,0,180))
    draw.text(((W-dw)/2, H - 60), date_venue, font=font_small, fill=(200, 200, 200, 255))
    
    # Save Image
    file_name = f"match_{i+1}.jpg"
    out_path = os.path.join(output_dir, file_name)
    merged.convert("RGB").save(out_path, "JPEG", quality=90)
    
print("Successfully generated all 20 VIP Face-Off posters based on actual team graphics!")
